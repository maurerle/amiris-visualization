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


def line(series: pd.Series, column_metadata: Dict[str, str]) -> Dict:
    """
    Plots a single line from given series

    Args:
        series: the series to be plotted with one index
        column_metadata: associated with the series; required keys are 'label' & 'unit'

    Returns:
        ECharts options dictionary
    """
    series = series.squeeze()
    if not isinstance(series, pd.Series):
        raise TypeError("Line plot takes a single column only!")

    label = column_metadata["label"]
    unit = column_metadata["unit"]
    scaling_factor = column_metadata.get("scaling_factor", "")

    options = {
        "xAxis": {
            "type": "category",
            "data": series.index.tolist(),
        },
        "yAxis": {
            "type": "value",
            "name": f"{label} in {scaling_factor}{unit}",
            "nameLocation": "middle",
            "nameGap": 75
        },
        "series": [{
            "data": series.tolist(),
            "type": "line",
            "name": label
        }],
    }
    return update_options_with_overrides(_default_line_options(), options)


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


def twolinetwoyaxes(data, metadata, axesmapping) -> Dict:
    options = {
        "legend": {"data": [metadata[col]["label"] for col in axesmapping]},
        "dataZoom": [
            {
                "show": True,
                "realtime": True,
                "start": 1,
                "end": 2,
                "xAxisIndex": [0, 1]
            },
            {
                "type": 'inside',
                "realtime": True,
                "start": 1,
                "end": 2,
                "xAxisIndex": [0, 1]
            }
        ],
        "grid": [
            {
                "left": 150,
                "right": 50,
                "height": '35%'
            },
            {
                "left": 150,
                "right": 50,
                "top": '50%',
                "height": '35%'
            }
        ],
        "xAxis": [
            {
                "type": 'category',
                "gridIndex": axisindex,
                "boundaryGap": False,
                "axisLine": {"onZero": True},
                "axisTick": {"show": False} if axisindex == 0 else {},
                "axisLabel": {"show": False} if axisindex == 0 else {},
                "data": data.index.tolist()
            } for axisindex in axesmapping.values()
        ],
        "yAxis": [
            {
                "gridIndex": axisindex,
                "name": f'{metadata[col]["label"]} in {metadata[col]["unit"]}',
                "nameLocation": "middle",
                "nameGap": 75,
                "type": 'value',
            } for col, axisindex in axesmapping.items()
        ],
        "series": [
            {
                "name": metadata[col]["label"],
                "type": 'line',
                "symbolSize": 8,
                "xAxisIndex": axesmapping[col],
                "yAxisIndex": axesmapping[col],
                "data": data[col].tolist()
            } for col in axesmapping
        ]
    }
    return update_options_with_overrides(_default_line_options(), options)


def twolinestwoyaxesonesubplot(data, metadata, axesmapping) -> Dict:
    options = {
        "tooltip": {
            "trigger": 'axis',
            "axisPointer": {
                "type": 'cross',
                "crossStyle": {
                    "color": '#999'
                }
            }
        },
        "toolbox": {
            "feature": {
                "dataView": {"show": True, "readOnly": False},
                "magicType": {"show": True, "type": ['line', 'bar']},
                "restore": {"show": True},
                "saveAsImage": {"show": True}
            }
        },
        "legend": {"data": [metadata[col]["label"] for col in axesmapping]},
        "xAxis": [
            {
                "type": 'category',
                "data": data.index.tolist(),
            }
        ],
        "yAxis": [
            {
                "type": 'value',
                "name": f'{metadata[col]["label"]} in {metadata[col]["unit"]}',
                "nameLocation": "middle",
                "nameGap": 75,
                "alignTicks": True
            } for col in axesmapping
        ],
        "series": [
            {
                "name": metadata[col]["label"],
                "type": 'line',
                "yAxisIndex": axisindex,
                "data": data[col].tolist()
            } for col, axisindex in axesmapping.items()
        ]
    }
    return update_options_with_overrides(_default_line_options(), options)


def stacked(data, metadata, area: bool = True) -> Dict:
    """
    Plots all columns from given dataframe as stacked (area) lines

    Args:
        data: containing multiple columns and one index
        metadata: associated with the columns; shape: {<column_name>: {'label': <label>}}
        area: if True, area between lines is filled

    Returns:
        ECharts options dictionary
    """
    options = {
        "legend": {
            "data": [col for col in data.columns],
            "selector": True,
        },
        "grid": {"left": "3%", "right": "4%", "bottom": "15%", "containLabel": True},
        "xAxis": {
            "type": "category",
            "boundaryGap": True,
            "axisLine": {"onZero": True},
            "data": data.index.tolist(),
        },
        "yAxis": {
            "type": "value"
        },
        "series": [{
            "data": data[col].tolist(),
            "type": "line",
            "name": col,
            "stack": "stack0",
            "emphasis": {"focus": "series"},
        } for col in data.columns],
    }
    if area:
        for series in options["series"]:
            series.update({"areaStyle": {}})
    return update_options_with_overrides(_default_line_options(), options)
