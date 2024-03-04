# SPDX-FileCopyrightText: Florian Maurer
#
# SPDX-License-Identifier: Apache-2.0

# now we can evaluate the runs

from pathlib import Path

import matplotlib.pyplot as plt

from queries import query_data

simulation = "amiris_germany2019"
from_date = "2019-02-01"
to_date = "2019-12-31"
# to_date = "2019-12-31"
base_path = Path("output", simulation)

data = query_data(simulation, from_date, to_date)
print(data.keys())

plt.style.use("seaborn-v0_8")

pt = data["dispatch_wind_offshore"]
(pt["AMIRIS"] - pt["ASSUME"]).plot()


def savefig(path: str, *args, **kwargs):
    output_path = Path(base_path, path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, *args, transparent=False, bbox_inches="tight", **kwargs)


ddf = data["assume_dispatch"]
base = ddf[ddf.columns[0]] * 0
plt.figure(figsize=(10,5))
for col in ddf.columns:
    line = base + ddf[col]
    # c = (0.3, 0.2, 0.6, 0.8) if "nuclear" in col else "g"
    c = None
    alpha = 0.6
    plt.fill_between(line.index, line, base, alpha=alpha, label=col)
    base += ddf[col]
plt.ylabel("Hourly dispatch power [$GW$]")
plt.xlabel("Datetime")
plt.xticks(rotation=25)
plt.legend()
savefig("overview-dispatch.png")
plt.show()

### price duration curve
plt.figure(figsize=(10,5))
data["preislinie_amiris"].plot()
data["preislinie_assume"].plot()
data["preislinie_entsoe"].plot()

plt.xlabel("hours")
plt.ylabel("price in [€/MW]")
plt.legend()
savefig("price_duration_curve.png")
plt.show()

plt.figure(figsize=(10,5))
plt.scatter(data["preis_entsoe"], data["preis_assume"][:7993])
plt.scatter(data["preis_entsoe"], data["preis_amiris"])
plt.xlabel("historic price of ENTSO-E")
plt.ylabel("simulation price at respective hour")
plt.legend(["ASSUME", "AMIRIS"])
plt.title("scatter plot of the simulation prices")
savefig("price_scatter_curve.png")


### dispatch duration curve

techs = ["nuclear", "wind_offshore", "wind_onshore", "solar", "lignite", "natural gas"]
data["ddcs"] = {}
for tech in techs:
    data["ddcs"][f"{tech}_entsoe"] = (
        data["dispatch_entsoe"][tech]
        .sort_values(ascending=False)
        .reset_index(drop=True)
    )

    data["ddcs"][f"{tech}_assume"] = (
        data[f"dispatch_{tech}"]["ASSUME"]
        .sort_values(ascending=False)
        .reset_index(drop=True)*1e3
    )
    data["ddcs"][f"{tech}_amiris"] = (
        data[f"dispatch_{tech}"]["AMIRIS"]
        .sort_values(ascending=False)
        .reset_index(drop=True)*1e3
    )

for tech in techs:
    plt.figure(figsize=(10,5))
    (data["ddcs"][f"{tech}_entsoe"]/1e6).plot()
    (data["ddcs"][f"{tech}_amiris"]/1e6).plot()
    (data["ddcs"][f"{tech}_assume"]/1e6).plot()
    plt.title(tech)
    plt.xlabel("hour")
    plt.ylabel("energy in GW")
    plt.legend()
    savefig(f"dispatch_duration_curve_{tech}.png")
    plt.show()



data["dispatch_wind_onshore"][100:400]["ASSUME"].plot()
data["dispatch_entsoe"]["wind_onshore"][100:400].plot()

data["dispatch_wind_offshore"][100:1000]["ASSUME"].plot()
(data["assume_dispatch"]["wind_offshore"][100:1000]).plot()
data["dispatch_entsoe"]["wind_offshore"][100:1000].plot()
(data["assume_dispatch"]["wind_offshore"][100:1000]).plot()

(data["assume_dispatch"]["lignite"][100:400] * 1e6).plot()
data["dispatch_entsoe"]["lignite"][100:400].plot()

res_amiris = data["preis_entsoe"]-data["preis_amiris"]
res_assume = data["preis_entsoe"]-data["preis_assume"]
mae_amiris = abs(res_amiris)
mae_assume = abs(res_assume)
mae_assume = mae_assume.fillna(0)
print("MAE ASSUME",simulation, mae_assume.mean())
print("MAE AMIRIS",simulation, mae_amiris.mean())

rmse_amiris = np.sqrt(
    ((res_amiris)**2).fillna(0).mean()
)

rmse_assume = np.sqrt(
    ((res_assume)**2).fillna(0).mean()
)

print("RMSE ASSUME",simulation, rmse_assume.mean())
print("RMSE AMIRIS",simulation, rmse_amiris.mean())

plt.figure(figsize=(10,5))
res_assume.resample("7d").mean().plot()
res_amiris.resample("7d").mean().plot()
plt.legend(["assume", "amiris"])
plt.title("7d average of price residuals to ENTSO-E")
plt.ylabel("price deviation in [€/MW]")
plt.xlabel("time")
savefig("price_deviation")
plt.show()