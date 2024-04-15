from enum import Enum, auto
from pathlib import Path
from typing import Dict

import pandas as pd

from dashboard.data.preparation import DataPreparer, column_metadata


class TimeFormat(Enum):
    FAME = auto()
    UTC = auto()


class Model(Enum):
    AMIRIS = auto()
    ASSUME = auto()
    HISTORICAL = auto()


class Column(Enum):
    PRICE = column_metadata("Electricity Price", unit="EUR/MWh")


class CsvFile:
    """A CSV data file of one or multiple timeseries with one column denoting the time"""

    ERR_YEAR_MISSING = "File not read for year {} of CsvFile {}"

    def __init__(self, model: Model, file: str, time_column: str, time_format: TimeFormat, separator: str,
                 columns: Dict[Column, str]) -> None:
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
        df["TimeStamp"] = self._convert_time_column(df[self._time_column], self._time_format)
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

    def add_column(self, preparer: DataPreparer, group: str, year: int, column: Column) -> None:
        """Adds data for given `column` and `year` to specified `group` of given `preparer`"""
        column_name = self._columns[column]
        if year not in self._data.keys():
            raise ValueError(self.ERR_YEAR_MISSING.format(year, self._filename))
        series = self._data[year][column_name]
        series.name = self._model.name
        preparer.add_values(group=group, series=series, metadata=column.value)


FILES = {
    Model.AMIRIS: {
        "DayAheadMarket": CsvFile(model=Model.AMIRIS, file="DayAheadMarketSingleZone.csv", time_column="TimeStep",
                                  time_format=TimeFormat.UTC, separator=";",
                                  columns={Column.PRICE: "ElectricityPriceInEURperMWH"})
    },
    Model.ASSUME: {
        "MarketMeta": CsvFile(model=Model.ASSUME, file="market_meta.csv", time_column="time",
                              time_format=TimeFormat.UTC, separator=",",
                              columns={Column.PRICE: "price"})
    },
    Model.HISTORICAL: {
        "DaPrices": CsvFile(model=Model.HISTORICAL, file="da_prices.csv", time_column="TimeStep",
                            time_format=TimeFormat.FAME, separator=";",
                            columns={Column.PRICE: "ElectricityPriceInEURperMWH"})
    }
}


class DataReader:
    """Reads data from AMIRIS and ASSUME outputs as well as historic timeseries"""

    def __init__(self, preparer: DataPreparer, amiris_folder: Path, assume_folder: Path, historic_folder: Path):
        self._preparer = preparer
        self._folders = {
            Model.AMIRIS: amiris_folder,
            Model.ASSUME: assume_folder,
            Model.HISTORICAL: historic_folder,
        }
        self._files_read: Dict[Model, Dict[str, CsvFile]] = {
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
        self._read_electricity_prices(year)

    def _read_electricity_prices(self, year: int) -> None:
        """
        Extract electricity prices from AMIRIS, ASSUME and historic data in given year and save to DataPreparer

        Args:
            year: target year to extract data for
        """
        self._preparer.init_data_group(group="prices", key_metadata={
            "TimeStamp": column_metadata(label="Simulation Time", unit="h"),
        })
        self._get_file(Model.AMIRIS, "DayAheadMarket", year).add_column(self._preparer, "prices", year, Column.PRICE)
        self._get_file(Model.ASSUME, "MarketMeta", year).add_column(self._preparer, "prices", year, Column.PRICE)
        self._get_file(Model.HISTORICAL, "DaPrices", year).add_column(self._preparer, "prices", year, Column.PRICE)

    def _get_file(self, model: Model, file_id: str, year: int) -> CsvFile:
        """Return file for the given `model` and `file_id` that has the data loaded for the given `year`"""
        model_files = self._files_read[model]
        if file_id not in model_files.keys():
            model_files[file_id] = FILES[model][file_id]
        file = model_files[file_id]
        if not file.has_data_for_year(year):
            file.read_at(self._folders[model], year)
        return file
