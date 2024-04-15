from typing import Dict

import streamlit as st
from streamlit_echarts import st_echarts, JsCode

from dashboard.plots.lines import lines
from dashboard.tools import update_options_with_defaults, update_options_with_overrides
from dashboard.tools.scaling import auto_scale


def relabel_by_model(metadata: Dict[str, Dict[str, str]]):
    """Replaces labels of series by model names"""
    for model, model_metadata in metadata.items():
        model_metadata["label"] = model


def create(data, metadata, cfg):
    filter1, _ = st.columns([0.2, 0.8])
    with filter1:
        series_names = {v["AMIRIS"]["label"]: k for k, v in metadata.items()}

        selected_series = st.selectbox(label=f"Select Column", options=series_names.keys(), key=0,
                                       disabled=(len(series_names) < 2)
                                       )
        data_entry_point = series_names[selected_series]

    data = data[data_entry_point]
    metadata = metadata[data_entry_point]

    y_unit = metadata["AMIRIS"]["unit"]
    y_label = metadata["AMIRIS"]["label"]

    relabel_by_model(metadata)
    with st.container():
        data_plot, factor = auto_scale(data)
        options = lines(data_plot.squeeze(), metadata=metadata)
        options = update_options_with_defaults(options)
        options = update_options_with_overrides(options, cfg['multiline_region_plot'])

        unit_label = f"in {factor}{y_unit}"
        toolbox_formatter = ("function (params) {"
                             f"unscaled_value = params.value * {factor}; "
                             f"header = '<b> {y_label}</b>';"
                             f"series = params.seriesName + ': ' + unscaled_value.toFixed(2) + ' {y_unit}';"
                             f"return header + '<br/>' + series}}")
        options_update = {
            'yAxis': {
                'name': f'{y_label} {unit_label}',
                'nameGap': 30,
            },
            'tooltip': {
                'trigger': 'item',
                'formatter': JsCode(toolbox_formatter).js_code
            }
        }
        options = update_options_with_overrides(options, options_update)
        options["dataZoom"][0].update({"start": 0, "end": 2})

        st_echarts(
            options=options,
            height='500px'
        )
