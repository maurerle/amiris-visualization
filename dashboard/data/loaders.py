# SPDX-FileCopyrightText: 2024 German Aerospace Center
#
# SPDX-License-Identifier: Apache-2.0
import json
import pathlib as pt

import pandas as pd


def get_meta(store: object, hdfpackage_path: str) -> dict:
    return json.loads(store.get_storer(hdfpackage_path).attrs["plot_metadata"])


def load_data(path: pt.Path) -> dict:
    datasets = {}
    metadata = {}

    if path is not None and path.exists():
        with pd.HDFStore(path=path, mode="r") as store:
            for key in store:
                datasets[key] = store.get(key)
                metadata[key] = get_meta(store, key)
    else:
        datasets = {}
        metadata = {}

    return datasets, metadata
