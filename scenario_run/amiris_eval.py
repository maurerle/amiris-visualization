# SPDX-FileCopyrightText: Florian Maurer
#
# SPDX-License-Identifier: Apache-2.0

# now we can evaluate the runs

import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from queries import query_data

plt.style.use("seaborn-v0_8")


def plot_all_plots(
    simulation: str,
    from_date: str,
    to_date: str,
    data,
    latex_table: bool = False,
):
    base_path = Path("output", simulation)

    # set plot to true here to see plots inline
    def savefig(path: str, plot=False, *args, **kwargs):
        output_path = Path(base_path, f"{path}.svg")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(
            output_path, *args, transparent=False, bbox_inches="tight", **kwargs
        )
        if plot:
            plt.show()
        plt.close()

    # pt = data["dispatch_wind_onshore"]
    # (pt["AMIRIS"] - pt["ASSUME"]).plot()

    ### price duration curve
    plt.figure(figsize=(10, 5))
    data["preislinie_amiris"].plot()
    data["preislinie_assume"].plot()
    data["preislinie_entsoe"].plot()
    plt.xlabel("hours")
    plt.ylabel("price in [€/MW]")
    plt.legend(["AMIRIS", "ASSUME", "ENTSO-E"])
    savefig("price_duration_curve")

    ### dispatch duration curve

    techs = [
        "nuclear",
        "wind_offshore",
        "wind_onshore",
        "solar",
        "lignite",
        "natural gas",
        "hard coal",
        "oil",
        "hydro",
    ]
    data["ddcs"] = {}
    for tech in techs:
        if tech not in data["dispatch_entsoe"]:
            continue
        if f"dispatch_{tech}" not in data:
            continue
        data["ddcs"][f"{tech}_entsoe"] = (
            data["dispatch_entsoe"][tech]
            .sort_values(ascending=False)
            .reset_index(drop=True)
        )

        data["ddcs"][f"{tech}_assume"] = (
            data[f"dispatch_{tech}"]["ASSUME"]
            .sort_values(ascending=False)
            .reset_index(drop=True)
            * 1e3
        )
        data["ddcs"][f"{tech}_amiris"] = (
            data[f"dispatch_{tech}"]["AMIRIS"]
            .sort_values(ascending=False)
            .reset_index(drop=True)
            * 1e3
        )

        plt.figure(figsize=(10, 5))
        (data["ddcs"][f"{tech}_entsoe"] / 1e6).plot()
        (data["ddcs"][f"{tech}_amiris"] / 1e6).plot()
        (data["ddcs"][f"{tech}_assume"] / 1e6).plot()
        plt.title(tech)
        plt.xlabel("hour")
        plt.ylabel("energy in GW")
        plt.legend()
        savefig(f"dispatch_duration_curve_{tech}")

    if False:
        data["dispatch_wind_onshore"][100:400]["ASSUME"].plot()
        data["dispatch_entsoe"]["wind_onshore"][100:400].plot()

        data["dispatch_wind_offshore"][100:1000]["ASSUME"].plot()
        (data["assume_dispatch"]["wind_offshore"][100:1000]).plot()
        data["dispatch_entsoe"]["wind_offshore"][100:1000].plot()
        (data["assume_dispatch"]["wind_offshore"][100:1000]).plot()

        (data["assume_dispatch"]["lignite"][100:400] * 1e0).plot()
        data["dispatch_entsoe"]["lignite"][100:400].plot()

        savefig("dispatch_wind_lignite")
    # price scatter plot
    print(data["preis_entsoe"].index)
    preis_entsoe = data["preis_entsoe"][from_date:to_date]
    preis_amiris = data["preis_amiris"][from_date:to_date]
    preis_assume = data["preis_assume"][from_date:to_date]
    # preis_amiris = preis_amiris[preis_entsoe>=0]
    # preis_assume = preis_assume[preis_entsoe>=0]
    # preis_entsoe = preis_entsoe[preis_entsoe>=0]

    # Pearson correlation coefficient
    preis_entsoe = preis_entsoe.reindex(preis_amiris.index, fill_value=0)
    corref_amiris = np.corrcoef(preis_entsoe, preis_amiris)[0, 1]
    corref_assume = np.corrcoef(preis_entsoe, preis_assume)[0, 1]
    print(f"CORR COEFF AMIRIS {simulation}  {corref_amiris:.4f}")
    print(f"CORR COEFF ASSUME {simulation}  {corref_assume:.4f}")

    max_entsoe = preis_entsoe.max()
    min_entsoe = preis_entsoe.min()
    min_entsoe = preis_amiris.min()
    plt.figure(figsize=(8, 8))
    plt.scatter(preis_entsoe, preis_amiris, s=8)
    plt.scatter(preis_entsoe, preis_assume, s=8)
    plt.plot([min_entsoe, max_entsoe], [min_entsoe, max_entsoe], "k--", linewidth=1)
    plt.xlabel("historic price of ENTSO-E [€/MWh]")
    plt.ylabel("simulation price at respective hour [€/MWh]")
    plt.gca().axis("equal")
    plt.gca().set_aspect("equal", adjustable="box")
    plt.legend(
        [
            f"AMIRIS\t    corr coef: {corref_amiris:.4f}".expandtabs(),
            f"ASSUME\t corr coef: {corref_assume:.4f}".expandtabs(),
        ]
    )
    plt.yticks(np.arange(min_entsoe // 20 * 20, max_entsoe + 1 // 20 * 20, 20))
    plt.xticks(np.arange(preis_entsoe.min() // 20 * 20, max_entsoe + 1 // 20 * 20, 20))
    # plt.title("scatter plot of the simulation prices")
    savefig("price_scatter_curve")
    res_amiris = preis_entsoe - preis_amiris
    res_assume = preis_entsoe - preis_assume
    # res_assume = res_assume - res_assume.mean()
    mae_amiris = abs(res_amiris)
    mae_assume = abs(res_assume)
    mae_assume = mae_assume.fillna(0)
    print("MAE AMIRIS", simulation, mae_amiris.mean())
    print("MAE ASSUME", simulation, mae_assume.mean())

    print(f"mean AMIRIS {simulation}  {preis_amiris.mean():.2f}")
    print(f"mean ASSUME {simulation}  {preis_assume.mean():.2f}")
    print(f"mean ENTSO-E {simulation}  {preis_entsoe.mean():.2f}")

    rmse_amiris = np.sqrt(((res_amiris) ** 2).fillna(0).mean())

    rmse_assume = np.sqrt(((res_assume) ** 2).fillna(0).mean())

    print("RMSE ASSUME", simulation, rmse_assume.mean())
    print("RMSE AMIRIS", simulation, rmse_amiris.mean())

    plt.figure(figsize=(10, 5))
    preis_amiris.resample("7d").mean().plot()
    preis_assume.resample("7d").mean().plot()
    preis_entsoe.resample("7d").mean().plot()
    plt.legend(["AMIRIS", "ASSUME", "ENTSO-E"])
    plt.title("7d average of price")

    plt.figure(figsize=(10, 5))
    res_amiris.resample("7d").mean().plot()
    res_assume.resample("7d").mean().plot()
    plt.legend(["AMIRIS", "ASSUME"])
    plt.title("7d average of price residuals to ENTSO-E")
    plt.ylabel("price deviation in [€/MW]")
    plt.xlabel("time")
    savefig("price_deviation")

    if latex_table:
        table_str = f"""
                ~ & MAE & RMSE & max & min & mean & std \\\\ \hline
                AMIRIS & {mae_amiris.mean():.2f} & {rmse_assume.mean():.2f} & {preis_amiris.max():.2f} & {preis_amiris.min():.2f} & {preis_amiris.mean():.2f} & {preis_amiris.std():.2f}\\\\ \hline
                ASSUME & {mae_assume.mean():.2f} & {rmse_amiris.mean():.2f} & {preis_assume.max():.2f} & {preis_assume.min():.2f} & {preis_assume.mean():.2f} & {preis_assume.std():.2f}\\\\ \hline
                Historic & 0 & 0 & {preis_entsoe.max():.2f} & {preis_entsoe.min():.2f} & {preis_entsoe.mean():.2f} & {preis_entsoe.std():.2f}\\\\
        """

        table_new = (
            r"""
        \\begin{table}[!ht]
            \centering
            \\begin{tabular}{l|l|l|l|l|l|l}%s   \end{tabular}
            \caption{Quantitative results of the price fit towards the historic dataset of Germany 2019}
            \label{tab:quantitative results}
        \end{table}
        """  # noqa: UP031
            % table_str
        )
        print(table_new)
        output_path = Path(base_path, "table.tex")
        with open(output_path, "w") as f:
            f.write(table_new)

    ddf = data["assume_dispatch"][4000:4500]
    ddf = ddf.reindex(
        [
            "biomass",
            "nuclear",
            "oil",
            "hydro",
            "lignite",
            "hard coal",
            "other",
            "wind_offshore",
            "wind_onshore",
            "solar",
        ],
        axis=1,
    )
    ddf.dropna(axis=1, how="all", inplace=True)
    base = ddf[ddf.columns[0]] * 0
    plt.figure(figsize=(10, 5))
    for col in ddf.columns:
        line = base + ddf[col]
        alpha = 0.6
        plt.fill_between(line.index, line, base, alpha=alpha, label=col)
        base += ddf[col]
    plt.ylabel("Hourly dispatch power [$GW$]")
    plt.xlabel("Datetime")
    plt.xticks(rotation=25)
    plt.legend()
    savefig("overview-dispatch-assume")

    if "2019" in simulation:
        start = "2019-06-17"
        end = "2019-07-10"

        techs = ["nuclear", "hard coal", "lignite", "natural gas", "oil", "hydro"]
        for tech in techs:
            plt.figure(figsize=(10, 5))
            dispatch_entsoe = (data["dispatch_entsoe"][tech] / 1e3)[start:end].dropna()
            if len(dispatch_entsoe) > 0:
                data[f"dispatch_{tech}"]["AMIRIS"][start:end].plot()
                data[f"dispatch_{tech}"]["ASSUME"][start:end].plot()
                dispatch_entsoe.plot()
                plt.legend(["AMIRIS", "ASSUME", "ENTSO-E"])
                plt.xlabel("time")
                plt.ylabel("power in MW")
                savefig(f"sample-dispatch-{tech}")

        start = "2019-01-19"
        end = "2019-02-04"
        plt.figure(figsize=(10, 5))
        plt.step(preis_amiris[start:end].index, preis_amiris[start:end], linewidth=1)
        plt.step(preis_assume[start:end].index, preis_assume[start:end], linewidth=1)
        plt.step(preis_entsoe[start:end].index, preis_entsoe[start:end], linewidth=1)
        plt.legend(["AMIRIS", "ASSUME", "ENTSO-E"])
        plt.xlabel("time")
        plt.xticks(rotation=25)
        plt.ylabel("price in €/MW")
        savefig("sample-price")

        start = "2019-04-29"
        end = "2019-05-13"
        plt.figure(figsize=(10, 5))
        plt.step(preis_amiris[start:end].index, preis_amiris[start:end], linewidth=1)
        plt.step(preis_assume[start:end].index, preis_assume[start:end], linewidth=1)
        plt.step(preis_entsoe[start:end].index, preis_entsoe[start:end], linewidth=1)
        plt.xticks(rotation=25)
        plt.legend(["AMIRIS", "ASSUME", "ENTSO-E"])
        plt.xlabel("time")
        plt.ylabel("price in €/MW")
        savefig("sample-price2")


def results_to_csv(results: dict[str, dict[str, pd.DataFrame]]):
    for key, value in results.items():
        path = Path("output/csv", key)
        path.mkdir(parents=True, exist_ok=True)
        for val_key, val_value in value.items():
            val_path = Path(path, val_key + ".csv")
            if isinstance(val_value, dict):
                return_value = pd.DataFrame(val_value)
            else:
                return_value = val_value
            return_value.to_csv(val_path)


if __name__ == "__main__":
    simulations = [
        "amiris_germany2015",
        "amiris_germany2016",
        "amiris_germany2017",
        "amiris_germany2018",
        "amiris_germany2019",
        "amiris_austria2019",
    ]

    # simulation = "amiris_germany2019"
    # from_date = "2019-01-02"
    # to_date = "2019-12-31"
    # data = query_data(simulation, from_date, to_date)
    # plot_all_plots(simulation, from_date, to_date, data)
    results_pickle_path = Path("results.pkl")
    if results_pickle_path.is_file():
        with open(results_pickle_path, "rb") as f:
            results = pickle.load(f)
    else:
        results = {}

    for simulation in simulations:
        year = simulation[14:18]

        from_date = f"{year}-01-02"
        to_date = f"{year}-12-30"
        if not results.get(simulation):
            print(f"querying data for {simulation}")
            data = query_data(simulation, from_date, to_date)
            results[simulation] = data
        plot_all_plots(simulation, from_date, to_date, results[simulation])

    with open(results_pickle_path, "wb") as f:
        pickle.dump(results, f)

    results_to_csv(results)
