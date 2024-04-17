from functools import lru_cache

import pandas as pd
from sqlalchemy import create_engine, text

from config import db_uri, entsoe_uri

###########################

simulation = "amiris_germany2018"
from_date = "2018-01-01"
to_date = "2018-12-31"


@lru_cache(maxsize=32)
def query_data(simulation: str, from_date: str, to_date: str):
    entsoe_engine = create_engine(entsoe_uri)
    engine = create_engine(db_uri)

    VALID_COUNTRY = "('DE_LU', 'DE_AT_LU')"
    if "austria" in simulation:
        VALID_COUNTRY = "('AT')"
    print(simulation)
    # assume_dispatch
    data = {}
    sql = f"""
    SELECT
    "datetime" as "time",
    sum(power) AS "market_dispatch",
    market_id,
    um.technology
    FROM market_dispatch md
    join power_plant_meta um on um."index" = md.unit_id and um.simulation = md.simulation
    WHERE
    "datetime" BETWEEN '{from_date}' AND '{to_date}' AND
    md.simulation = '{simulation}'
    GROUP BY 1, market_id, technology
    ORDER BY technology, market_id desc, 1
    """

    assume_dispatch = pd.read_sql(sql, engine, index_col="time", parse_dates="time")

    series = []
    for label, sub_df in assume_dispatch.groupby(["market_id", "technology"]):
        lab = "-".join(label)
        lab = lab.replace("Market_1-", "")

        # if "lignite" not in lab and "nuclear" not in lab:
        #    continue
        group_sum = sub_df.market_dispatch.groupby("time").sum()
        group_sum.name = lab
        series.append(group_sum.resample("1h").ffill())

    ddf = pd.DataFrame(series)
    ddf = ddf.T.ffill()

    ddf = ddf[sorted(ddf.columns, reverse=True)]
    ddf = ddf.fillna(0)
    data["assume_dispatch"] = ddf * 1e3  # MW to kWh

    # amiris and assume dispatch
    query = f"""
    select time_bucket('3600.000s',a."time") AS "time",
    avg("ASSUME Actual dispatch") as "ASSUME",
    avg("AMIRIS Awarded Energy") as "AMIRIS",
    c."technology",
    a."agent"
    from
    (SELECT
    index as "time",
    avg(power) AS "ASSUME Actual dispatch",
    SUBSTRING(unit,27) as "agent",
    simulation,
    unit
    FROM unit_dispatch
    WHERE
    index BETWEEN '{from_date}' AND '{to_date}' AND
    LOWER(simulation) = '{simulation}' AND
    unit like 'VariableRenewableOperator_%'
    GROUP BY 1, unit, power, simulation
    ORDER BY 1) a
    join (SELECT
    "TimeStep" as "time",
    "AgentId"::text as "agent",
    avg("AwardedEnergyInMWH") as "AMIRIS Awarded Energy"
    FROM {simulation}.VariableRenewableOperator
    WHERE
    "TimeStep" BETWEEN '{from_date}' AND '{to_date}'
    GROUP BY 1, "agent"
    ORDER BY 1) b on a.agent=b.agent and a.time=b.time
    join power_plant_meta c on a.unit = c.index and c.simulation=a.simulation
    GROUP BY 1, c.technology, a.agent
    """

    dispatch_data = pd.read_sql(
        text(query), engine, index_col="time", parse_dates="time"
    )
    for technology in dispatch_data["technology"].unique():
        dd = dispatch_data[dispatch_data["technology"] == technology]
        del dd["agent"]
        del dd["technology"]
        data[f"dispatch_{technology}"] = dd.resample("1h").sum()

    query = f"""
    select time_bucket('3600.000s',a."time") AS "time",
    avg("ASSUME Actual dispatch") as "ASSUME", 
    avg("AMIRIS Awarded Energy") as "AMIRIS",
    --avg("AMIRIS Awarded Energy"- "ASSUME Actual dispatch") as "Difference",
    a.technology,
    a.agent
    from
    (select
    time,
    sum("ASSUME Actual dispatch") as "ASSUME Actual dispatch",
    SUBSTRING(unit,27,1) as "agent",
    c.simulation,
    c.technology
    from
    (
    SELECT time_bucket('3600.000s',index) AS "time",
    avg(power) AS "ASSUME Actual dispatch",
    unit,
    simulation
    FROM unit_dispatch
    WHERE
    index BETWEEN '{from_date}' AND '{to_date}' AND
    LOWER(simulation) = '{simulation}' AND
    unit like 'PredefinedPlantBuilder_200%'
    GROUP BY 1, unit, power, simulation
    ORDER BY 1
    ) q
    join power_plant_meta c on q.unit = c.index and c.simulation=q.simulation
    --where c.technology = 'oil'
    group by 1, agent, c.technology, c.simulation) a
    join (SELECT
    time_bucket('3600.000s',"TimeStep") AS "time",
    substring("AgentId"::text,3) as "agent",
    avg("AwardedEnergyInMWH") as "AMIRIS Awarded Energy"
    --avg("OfferedEnergyInMWH"*1e3) as "OfferedEnergyInMWH",
    --avg("ReceivedMoneyInEUR") as "ReceivedMoneyInEUR",
    --avg("VariableCostsInEUR") as "VariableCostsInEUR"
    FROM {simulation}.ConventionalPlantOperator
    WHERE
    "TimeStep" BETWEEN '{from_date}' AND '{to_date}'
    GROUP BY 1, "agent"
    ORDER BY 1) b on a.agent=b.agent and a.time=b.time

    GROUP BY 1, a.agent, a.technology
    """
    amiris_dispatch = pd.read_sql(
        text(query), engine, index_col="time", parse_dates="time"
    )
    for technology in ["nuclear", "lignite", "hard coal", "natural gas", "oil"]:
        dd = amiris_dispatch[amiris_dispatch["technology"] == technology]
        del dd["agent"]
        del dd["technology"]
        data[f"dispatch_{technology}"] = dd.resample("1h").sum()

    # storage dispatch
    query = f"""
SELECT time_bucket('3600.000s',"TimeStep") AS "time",
avg("AwardedDischargeEnergyInMWH")-avg("AwardedChargeEnergyInMWH") as "storage_amiris",
avg("StoredEnergyInMWH")*1e3 as "soc_amiris"
FROM {simulation}.StorageTrader
WHERE
  "TimeStep" BETWEEN '{from_date}' AND '{to_date}'
GROUP BY 1
ORDER BY 1"""
    amiris_storage = pd.read_sql(
        text(query), engine, index_col="time", parse_dates="time"
    )

    query = f"""
SELECT time_bucket('3600.000s',"start_time") AS "time",
  avg(accepted_volume) AS "assume_storage"
FROM market_orders
WHERE
  start_time BETWEEN '{from_date}' AND '{to_date}' AND
  unit_id like 'StorageTrader%' AND
  simulation = '{simulation}'
GROUP BY 1, unit_id, market_id
ORDER BY 1
"""
    assume_storage = pd.read_sql(
        text(query), engine, index_col="time", parse_dates="time"
    )

    data["dispatch_storage"] = pd.concat(
        [amiris_storage["storage_amiris"], assume_storage["assume_storage"]], axis=1
    )
    data["dispatch_storage"].columns = ["AMIRIS", "ASSUME"]
    data["dispatch_storage"].fillna(0, inplace=True)

    # entsoe dispatch

    query = f"""
    SELECT
    time_bucket('3600.000s',index) AS "time",
    avg(nuclear*1e3) as nuclear,
    avg("fossil_hard_coal"*1e3) as coal,
    avg(("hydro_run-of-river_and_poundage"+hydro_water_reservoir)*1e3) as hydro,
    avg(biomass*1e3) as bio,
    avg(("fossil_coal-derived_gas"+"fossil_gas")*1e3) as "natural gas",
    avg("fossil_brown_coal/lignite" *1e3) as lignite,
    avg((fossil_oil+coalesce(fossil_oil_shale,0)+coalesce(fossil_peat,0))*1e3) as oil,
    avg(("fossil_hard_coal")*1e3) as "hard coal",
    avg(("wind_offshore")*1e3) as wind_offshore,
    avg(("wind_onshore")*1e3) as wind_onshore,
    avg(solar*1e3) as solar,
    avg((hydro_pumped_storage*1e3)) as "storage",
    avg((geothermal+other+waste)*1e3) as others
    FROM query_generation
    WHERE
    index BETWEEN '{from_date}' AND '{to_date}' AND
    country in {VALID_COUNTRY}
    GROUP BY 1
    ORDER BY 1
    """
    data["dispatch_entsoe"] = pd.read_sql(
        query, entsoe_engine, index_col="time", parse_dates="time"
    )

    query = f"""
    SELECT time_bucket('3600.000s',index) AS "time",
    avg("0") AS "entsoe_price"
    FROM query_day_ahead_prices
    WHERE
    index BETWEEN '{from_date}' AND '{to_date}' AND
    country in {VALID_COUNTRY}
    GROUP BY 1
    ORDER BY 1
    """
    entsoe_price = pd.read_sql(
        query, entsoe_engine, index_col="time", parse_dates="time"
    )
    data["preis_entsoe"] = entsoe_price["entsoe_price"]
    data["preis_entsoe"].index = data["preis_entsoe"].index.tz_localize(None)
    data["preislinie_entsoe"] = entsoe_price.sort_values(
        by="entsoe_price", ascending=False
    ).reset_index()["entsoe_price"]

    query = f"""SELECT time_bucket('3600.000s',"product_start") AS "time",
    avg(price) AS "assume_price"
    FROM market_meta
    WHERE ("simulation" LIKE '{simulation}') AND market_id = 'Market_1' AND 
    product_start BETWEEN '{from_date}' AND '{to_date}'
    GROUP BY market_id, simulation, product_start
    ORDER BY 1;
    """

    assume_price = pd.read_sql(query, engine, index_col="time", parse_dates="time")
    data["preis_assume"] = assume_price["assume_price"]
    data["preislinie_assume"] = assume_price.sort_values(
        by="assume_price", ascending=False
    ).reset_index()["assume_price"]

    # Preisdauerlinie
    # Ausgewählte Wochenscheiben der Preise

    query = f"""
    SELECT time_bucket('3600.000s',"TimeStep") AS "time",
    avg("ElectricityPriceInEURperMWH") as "amiris_price"
    FROM {simulation}.DayAheadMarketSingleZone
    WHERE
    "TimeStep" BETWEEN '{from_date}' AND '{to_date}'
    GROUP BY 1
    ORDER BY 1
    """

    amiris_price = pd.read_sql(query, engine, index_col="time", parse_dates="time")
    data["preis_amiris"] = amiris_price["amiris_price"]
    data["preislinie_amiris"] = amiris_price.sort_values(
        by="amiris_price", ascending=False
    ).reset_index()["amiris_price"]
    return data
