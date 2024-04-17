# SPDX-FileCopyrightText: 2024 German Aerospace Center
#
# SPDX-License-Identifier: Apache-2.0
from typing import Dict

import pandas as pd

from dashboard.tools import update_options_with_overrides


def _default_line_options():
    return {
        "title": {"text": None},
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"animation": False},
        },
        "axisPointer": {
            "link": [
                {"xAxisIndex": "all"}
            ]
        },
        "dataZoom": [
            {
                "type": 'slider',
                "xAxisIndex": 0,
            },
            {
                "type": 'inside',
                "xAxisIndex": 0,
                "zoomOnMouseWheel": True
            }
        ],
        "xAxis": {
            "nameLocation": "middle",
        },
        "yAxis": {
            "nameLocation": "middle",
        },
        "toolbox": {
            "feature": {
                "dataZoom": {
                    "show": True
                }
            }
        },
    }


def lines(data: pd.DataFrame, metadata: Dict[str, Dict[str, str]]) -> Dict:
    """
    Plots all columns from given dataframe as lines

    Args:
        data: containing multiple columns and one index
        metadata: associated with the columns; shape: {<column_name>: {'label': <label>}}

    Returns:
        ECharts options dictionary
    """
    options = {
        "legend": {
            "data": [metadata[col]["label"] for col in data.columns],
            "selector": True,
        },
        "xAxis": {
            "type": "category",
            "data": data.index.tolist(),
        },
        "yAxis": {
            "type": "value"
        },
        "series": [{
            "data": data[col].tolist(),
            "type": "line",
            "name": metadata[col]["label"]
        } for col in data.columns],
    }
    return update_options_with_overrides(_default_line_options(), options)
