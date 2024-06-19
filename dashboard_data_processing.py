# SPDX-FileCopyrightText: 2024 German Aerospace Center
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

from dashboard.data.preparation import DataPreparer
from dashboard.data.reader import DataReader

if __name__ == "__main__":
    preparer = DataPreparer()
    data_reader = DataReader(preparer, Path("./data/csv"))
    for year in [2015, 2016, 2017, 2018, 2019]:
        data_reader.read_all(year)
    preparer.save_to_file("./data/compare.hdf5")

# for file in Path("./data/csv").glob("**/*"):
#     if "dispatch_entsoe.csv" == file.name:
#         print(file)
#         import pandas as pd
#         df = pd.read_csv(file.absolute(), index_col="time")
#         df /= 1e3

#         df.to_csv(file.parent / "dispatch_entsoe.csv")
