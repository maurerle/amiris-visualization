# SPDX-FileCopyrightText: 2024 German Aerospace Center
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import pandas as pd

from dashboard.data import Column, Model, TimeFormat
from dashboard.data.preparation import DataPreparer


class CsvFile:
    """A CSV data file of one or multiple timeseries with one column denoting the time"""

    ERR_YEAR_MISSING = "File not read for year {} of CsvFile {}"

    def __init__(
        self,
        model: Model,
        file: str,
        time_column: str,
        time_format: TimeFormat,
        separator: str,
        columns: dict[Column, str],
    ) -> None:
        self._model = model
        self._filename = file
        self._time_column = time_column
        self._time_format = time_format
        self._separator = separator
        self._columns = columns
        self._data = {}

    def has_data_for_year(self, year: int) -> bool:
        """Returns True if data for the given `year` is available"""
        return year in self._data.keys()

    def read_at(self, base_path: Path, year: int) -> None:
        """Read file at given base_path and year and store data for actual queries to its content"""
        file_path = Path(base_path, str(year), self._filename)
        self._data[year] = self._read_csv_file(file_path)

    def _read_csv_file(self, path: Path) -> pd.DataFrame:
        """Read csv file at given path assuming a 1-line header and given separator.
        Returns a dataframe with index "TimeStamp", whose values are given in UTC hours"""
        df = pd.read_csv(path, sep=self._separator, header=0)
        df["TimeStamp"] = self._convert_time_column(
            df[self._time_column], self._time_format
        )
        df.drop(columns=[self._time_column], inplace=True)
        return df.set_index("TimeStamp")

    @staticmethod
    def _convert_time_column(column: pd.Series, time_format: TimeFormat) -> pd.Series:
        """Converts given series of times in specified format to hourly UTC times"""
        if time_format is TimeFormat.FAME:
            column = column.apply(lambda time: time.replace("_", " ")[:-6] + "h")
        elif time_format is TimeFormat.UTC:
            column = column.apply(lambda time: time[:-6] + "h")

        return column

    def add_column(
        self, preparer: DataPreparer, group: str, year: int, column: Column
    ) -> None:
        """Adds data for given `column` and `year` to specified `group` of given `preparer`"""
        column_name = self._columns[column]
        if year not in self._data.keys():
            raise ValueError(self.ERR_YEAR_MISSING.format(year, self._filename))
        series = self._data[year][column_name]
        series.name = self._model.name
        preparer.add_values(group=group, series=series, metadata=column.value)
