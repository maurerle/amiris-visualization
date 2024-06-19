# SPDX-FileCopyrightText: 2024 German Aerospace Center
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

from dashboard.data import Column, Model
from dashboard.data.files import FILES, CsvFile
from dashboard.data.preparation import DataPreparer, column_metadata


class DataReader:
    """Reads data from AMIRIS and ASSUME outputs as well as historic timeseries"""

    def __init__(
        self,
        preparer: DataPreparer,
        amiris_folder: Path,
        assume_folder: Path,
        historic_folder: Path,
    ):
        self._preparer = preparer
        self._folders = {
            Model.AMIRIS: amiris_folder,
            Model.ASSUME: assume_folder,
            Model.HISTORICAL: historic_folder,
        }
        self._files_read: dict[Model, dict[str, CsvFile]] = {
            Model.AMIRIS: {},
            Model.ASSUME: {},
            Model.HISTORICAL: {},
        }

    def read_all(self, year: int) -> None:
        """
        Read all timeseries for AMIRIS, ASSUME and historic data of given year and save to DataPreparer
        Args:
            year: to read the data for
        """
        self._populate(
            group="prices",
            amiris="DayAheadMarket",
            assume="MarketMeta",
            history="DaPrices",
            year=year,
            column=Column.PRICE,
        )
        self._populate(
            group="nuclear",
            amiris="Nuclear",
            assume="Nuclear",
            history="Dispatch",
            year=year,
            column=Column.NUCLEAR,
        )
        self._populate(
            group="lignite",
            amiris="Lignite",
            assume="Lignite",
            history="Dispatch",
            year=year,
            column=Column.LIGNITE,
        )
        self._populate(
            group="coal",
            amiris="Coal",
            assume="Coal",
            history="Dispatch",
            year=year,
            column=Column.COAL,
        )
        self._populate(
            group="gas",
            amiris="Gas",
            assume="Gas",
            history="Dispatch",
            year=year,
            column=Column.GAS,
        )
        self._populate(
            group="oil",
            amiris="Oil",
            assume="Oil",
            history="Dispatch",
            year=year,
            column=Column.OIL,
        )
        self._populate(
            group="hydro",
            amiris="Hydro",
            assume="Hydro",
            history="Dispatch",
            year=year,
            column=Column.HYDRO,
        )
        self._populate(
            group="pv",
            amiris="PV",
            assume="PV",
            history="Dispatch",
            year=year,
            column=Column.PV,
        )
        self._populate(
            group="onshore",
            amiris="Onshore",
            assume="Onshore",
            history="Dispatch",
            year=year,
            column=Column.ONSHORE,
        )
        self._populate(
            group="offshore",
            amiris="Offshore",
            assume="Offshore",
            history="Dispatch",
            year=year,
            column=Column.OFFSHORE,
        )

    def _populate(
        self,
        group: str,
        amiris: str,
        assume: str,
        history: str,
        year: int,
        column: Column,
    ) -> None:
        """
        Create a new group for given column and assign series data from files for AMIRIS, ASSUME and historical data

        Args:
            group: name of series group to be created
            amiris: name of AMIRIS file that contains data of assigned column
            assume: name of ASSUME file that contains data of assigned column
            history: name of historical file that contains data of assigned column
            year: target year to extract data for
            column: target column to extract data for
        """
        self._preparer.init_data_group(
            group=group,
            key_metadata={
                "TimeStamp": column_metadata(label="Simulation Time", unit="h"),
            },
        )
        self._get_file(Model.AMIRIS, amiris, year).add_column(
            self._preparer, group, year, column
        )
        self._get_file(Model.ASSUME, assume, year).add_column(
            self._preparer, group, year, column
        )
        self._get_file(Model.HISTORICAL, history, year).add_column(
            self._preparer, group, year, column
        )

    def _get_file(self, model: Model, file_id: str, year: int) -> CsvFile:
        """Return file for the given `model` and `file_id` that has the data loaded for the given `year`"""
        model_files = self._files_read[model]
        if file_id not in model_files.keys():
            model_files[file_id] = FILES[model][file_id]
        file = model_files[file_id]
        if not file.has_data_for_year(year):
            file.read_at(self._folders[model], year)
        return file
