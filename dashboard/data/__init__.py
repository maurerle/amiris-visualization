# SPDX-FileCopyrightText: 2024 German Aerospace Center
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum, auto

from dashboard.data.preparation import column_metadata


class TimeFormat(Enum):
    FAME = auto()
    UTC = auto()


class Model(Enum):
    AMIRIS = auto()
    ASSUME = auto()
    HISTORICAL = auto()


class Column(Enum):
    PRICE = column_metadata(label="Electricity Price", unit="EUR/MWh")
    NUCLEAR = column_metadata(label="Dispatch: Nuclear", unit="MWh/h")
    LIGNITE = column_metadata(label="Dispatch: Lignite", unit="MWh/h")
    COAL = column_metadata(label="Dispatch: Hard Coal", unit="MWh/h")
    GAS = column_metadata(label="Dispatch: Natural Gas", unit="MWh/h")
    OIL = column_metadata(label="Dispatch: Oil", unit="MWh/h")
    HYDRO = column_metadata(label="Dispatch: Run of River", unit="MWh/h")
    PV = column_metadata(label="Dispatch: PV", unit="MWh/h")
    ONSHORE = column_metadata(label="Dispatch: Wind onshore", unit="MWh/h")
    OFFSHORE = column_metadata(label="Dispatch: Wind offshore", unit="MWh/h")
    STORAGE = column_metadata(label="Dispatch: Pumped Hydro Storage", unit="MWh/h")
