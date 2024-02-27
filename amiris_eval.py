# SPDX-FileCopyrightText: Florian Maurer
#
# SPDX-License-Identifier: Apache-2.0

# now we can evaluate the runs

import time
from functools import partial
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from config import db_uri

savefig = partial(plt.savefig, transparent=False, bbox_inches="tight")

engine = create_engine(db_uri)

sql = """
SELECT ident, simulation,
sum(round(CAST(value AS numeric), 2))  FILTER (WHERE variable = 'total_cost') as total_cost,
sum(round(CAST(value AS numeric), 2)*1000)  FILTER (WHERE variable = 'total_volume') as total_volume,
sum(round(CAST(value AS numeric), 2))  FILTER (WHERE variable = 'avg_price') as average_cost
FROM kpis
where variable in ('total_cost', 'total_volume', 'avg_price')
and simulation in ('example_02d_eom_case', 'example_02d_ltm_case')
group by simulation, ident ORDER BY simulation
"""
kpis = pd.read_sql(sql, engine)
kpis["total_volume"] /= 1e9
kpis["total_cost"] /= 1e6
savefig = partial(plt.savefig, transparent=False, bbox_inches="tight")

## Data preparation
eom = kpis[kpis["ident"] == "EOM"]
ltm = kpis[kpis["ident"] == "LTM_OTC"].reset_index()
# ltm.loc[0, "average_cost"] = None
xticks = list(eom["simulation"])
# xlabels = [f"{i}%" for i in range(0, 101, 10)]
xlabels = ["EOM", "EOM + LTM"]
plt.style.use("seaborn-v0_8")

fig, (ax1, ax2) = plt.subplots(2, 1)
# Total Dispatch cost
ax1.bar(eom["simulation"], eom["total_cost"], label="EOM")
eom_ltm = eom[eom.simulation == "ltm_case10"]
ax1.bar(
    ltm["simulation"],
    ltm["total_cost"],
    bottom=eom_ltm["total_cost"],
    label="LTM",
)
ax1.set_ylabel("Total dispatch cost \n per market [mill. $€$]")
ax1.set_xticks(xticks, xlabels)
ax1.legend()
# Total Average Cost
ax2.scatter(eom["simulation"], eom["average_cost"], label="EOM")
ax2.scatter(ltm["simulation"], ltm["average_cost"], label="LTM")
ax2.bar(eom["simulation"], eom["total_cost"] * 0)
ax2.set_ylabel("Average cost \n for each scenario [$€/MWh$]")
# ax2.set_xlabel("Fraction of base load traded on LTM in percent")
ax2.set_xlabel("Selected electricity market design")
ax2.set_xticks(xticks, xlabels)
ax2.legend()
savefig("overview-cost.png")
plt.show()

# second plot
simulation = "amiris_germany2019"
sql = f"""
SELECT
"datetime" as "time",
sum(power) AS "market_dispatch",
market_id,
um.technology,
md.simulation
FROM market_dispatch md
join power_plant_meta um on um."index" = md.unit_id and um.simulation = md.simulation
WHERE
md.simulation = '{simulation}'
GROUP BY 1, market_id, technology
ORDER BY technology, market_id desc, 1
"""

df = pd.read_sql(sql, engine, index_col="time", parse_dates="time")
# fig, ax = plt.subplots(figsize=(8,6))
series = []
for label, sub_df in df.groupby(["market_id", "technology"]):
    lab = "-".join(label)
    lab = lab.replace("LTM_OTC", "LTM")

    if "lignite" not in lab and "nuclear" not in lab:
        continue
    group_sum = sub_df.market_dispatch.groupby("time").sum()
    group_sum.name = lab
    series.append(group_sum.resample("1h").ffill())

ddf = pd.DataFrame(series)
ddf = ddf.T.ffill()

ddf = ddf[sorted(ddf.columns, reverse=True)]
ddf = ddf.fillna(0)
ddf /= 1e3
base = ddf[ddf.columns[0]] * 0
for col in ddf.columns:
    line = base + ddf[col]
    c = (0.3, 0.2, 0.6, 0.8) if "nuclear" in col else "g"
    alpha = 0.8 if "LTM" in col else 0.6
    plt.fill_between(line.index, line, base, alpha=alpha, label=col, color=c)
    base += ddf[col]
plt.ylabel("Hourly dispatch power [$GW$]")
plt.xlabel("Datetime")
plt.xticks(rotation=25)
plt.legend()
savefig("overview-dispatch.png")
plt.show()


# ------
query = f"""
select 
time_bucket('10800.000s',a."time") AS "time",
avg("ASSUME Actual dispatch") as "ASSUME Actual dispatch", 
avg("AMIRIS Awarded Energy") as "AMIRIS Awarded Energy",
avg("AMIRIS Awarded Energy"- "ASSUME Actual dispatch") as "Difference", 
a."agent"
from
(SELECT
  index as "time",
  avg(power) AS "ASSUME Actual dispatch",
  SUBSTRING(unit,27) as "agent"
FROM unit_dispatch
WHERE
  index BETWEEN '2020-12-31T23:49:05.945Z' AND '2021-01-01T21:05:40.528Z' AND
  LOWER(simulation) = 'amiris_germany2019' AND
  unit like 'VariableRenewableOperator_%'
GROUP BY 1, unit, power
ORDER BY 1) a
join (SELECT
  "TimeStep" as "time",
  "AgentId"::text as "agent",
  avg("AwardedEnergyInMWH") as "AMIRIS Awarded Energy"
  --avg("OfferedEnergyInMWH"*1e3) as "OfferedEnergyInMWH",
  --avg("ReceivedMoneyInEUR") as "ReceivedMoneyInEUR",
  --avg("VariableCostsInEUR") as "VariableCostsInEUR"
FROM amiris_germany2019.VariableRenewableOperator
WHERE
  "TimeStep" BETWEEN '2020-12-31T23:49:05.945Z' AND '2021-01-01T21:05:40.528Z'
GROUP BY 1, "agent"
ORDER BY 1) b on a.agent=b.agent and a.time=b.time
--where a.agent = '10'
GROUP BY 1, a."agent"
"""
