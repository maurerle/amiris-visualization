# SPDX-FileCopyrightText: 2024 German Aerospace Center
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

from dashboard.data.preparation import DataPreparer
from dashboard.data.reader import DataReader

if __name__ == '__main__':
    preparer = DataPreparer()
    data_reader = DataReader(preparer, Path("./data/amiris"), Path("./data/assume"), Path("./data/historic"))
    for year in [2019]:
        data_reader.read_all(year)
    preparer.save_to_file("./data/compare.hdf5")
