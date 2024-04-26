# SPDX-FileCopyrightText: 2024 German Aerospace Center
#
# SPDX-License-Identifier: Apache-2.0
from dashboard.data import Model, Column, TimeFormat
from dashboard.data.csv_file import CsvFile

FILES = {
    Model.AMIRIS: {
        "DayAheadMarket": CsvFile(model=Model.AMIRIS, file="DayAheadMarketSingleZone.csv", time_column="TimeStep",
                                  time_format=TimeFormat.UTC, separator=";",
                                  columns={Column.PRICE: "ElectricityPriceInEURperMWH"}),
        "Nuclear": CsvFile(model=Model.AMIRIS, file="dispatch_nuclear.csv", time_column="time",
                           time_format=TimeFormat.UTC, separator=",", columns={Column.NUCLEAR: "AMIRIS"}),
        "Lignite": CsvFile(model=Model.AMIRIS, file="dispatch_lignite.csv", time_column="time",
                           time_format=TimeFormat.UTC, separator=",", columns={Column.LIGNITE: "AMIRIS"}),
        "Coal": CsvFile(model=Model.AMIRIS, file="dispatch_hard_coal.csv", time_column="time",
                        time_format=TimeFormat.UTC, separator=",", columns={Column.COAL: "AMIRIS"}),
        "Gas": CsvFile(model=Model.AMIRIS, file="dispatch_natural_gas.csv", time_column="time",
                       time_format=TimeFormat.UTC, separator=",", columns={Column.GAS: "AMIRIS"}),
        "Oil": CsvFile(model=Model.AMIRIS, file="dispatch_oil.csv", time_column="time",
                       time_format=TimeFormat.UTC, separator=",", columns={Column.OIL: "AMIRIS"}),
        "Hydro": CsvFile(model=Model.AMIRIS, file="dispatch_hydro.csv", time_column="time",
                         time_format=TimeFormat.UTC, separator=",", columns={Column.HYDRO: "AMIRIS"}),
        "PV": CsvFile(model=Model.AMIRIS, file="dispatch_solar.csv", time_column="time",
                      time_format=TimeFormat.UTC, separator=",", columns={Column.PV: "AMIRIS"}),
        "Onshore": CsvFile(model=Model.AMIRIS, file="dispatch_wind_onshore.csv", time_column="time",
                           time_format=TimeFormat.UTC, separator=",", columns={Column.ONSHORE: "AMIRIS"}),
        "Offshore": CsvFile(model=Model.AMIRIS, file="dispatch_wind_offshore.csv", time_column="time",
                            time_format=TimeFormat.UTC, separator=",", columns={Column.OFFSHORE: "AMIRIS"}),
    },
    Model.ASSUME: {
        "MarketMeta": CsvFile(model=Model.ASSUME, file="market_meta.csv", time_column="time",
                              time_format=TimeFormat.UTC, separator=",", columns={Column.PRICE: "price"}),
        "Nuclear": CsvFile(model=Model.ASSUME, file="dispatch_nuclear.csv", time_column="time",
                           time_format=TimeFormat.UTC, separator=",", columns={Column.NUCLEAR: "ASSUME"}),
        "Lignite": CsvFile(model=Model.ASSUME, file="dispatch_lignite.csv", time_column="time",
                           time_format=TimeFormat.UTC, separator=",", columns={Column.LIGNITE: "ASSUME"}),
        "Coal": CsvFile(model=Model.ASSUME, file="dispatch_hard_coal.csv", time_column="time",
                        time_format=TimeFormat.UTC, separator=",", columns={Column.COAL: "ASSUME"}),
        "Gas": CsvFile(model=Model.ASSUME, file="dispatch_natural_gas.csv", time_column="time",
                       time_format=TimeFormat.UTC, separator=",", columns={Column.GAS: "ASSUME"}),
        "Oil": CsvFile(model=Model.ASSUME, file="dispatch_oil.csv", time_column="time",
                       time_format=TimeFormat.UTC, separator=",", columns={Column.OIL: "ASSUME"}),
        "Hydro": CsvFile(model=Model.ASSUME, file="dispatch_hydro.csv", time_column="time",
                         time_format=TimeFormat.UTC, separator=",", columns={Column.HYDRO: "ASSUME"}),
        "PV": CsvFile(model=Model.ASSUME, file="dispatch_solar.csv", time_column="time",
                      time_format=TimeFormat.UTC, separator=",", columns={Column.PV: "ASSUME"}),
        "Onshore": CsvFile(model=Model.ASSUME, file="dispatch_wind_onshore.csv", time_column="time",
                           time_format=TimeFormat.UTC, separator=",", columns={Column.ONSHORE: "ASSUME"}),
        "Offshore": CsvFile(model=Model.ASSUME, file="dispatch_wind_offshore.csv", time_column="time",
                            time_format=TimeFormat.UTC, separator=",", columns={Column.OFFSHORE: "ASSUME"}),
    },
    Model.HISTORICAL: {
        "DaPrices": CsvFile(model=Model.HISTORICAL, file="da_prices.csv", time_column="TimeStep",
                            time_format=TimeFormat.FAME, separator=";",
                            columns={Column.PRICE: "ElectricityPriceInEURperMWH"}),
        "Dispatch": CsvFile(model=Model.HISTORICAL, file="dispatch.csv", time_column="time", time_format=TimeFormat.UTC,
                            separator=",",
                            columns={Column.NUCLEAR: "nuclear", Column.LIGNITE: "lignite", Column.COAL: "hard coal",
                                     Column.GAS: "natural gas", Column.OIL: "oil", Column.HYDRO: "hydro",
                                     Column.PV: "solar", Column.ONSHORE: "wind_onshore",
                                     Column.OFFSHORE: "wind_offshore"}),
    }
}
