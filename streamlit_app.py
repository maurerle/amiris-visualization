# SPDX-FileCopyrightText: 2024 German Aerospace Center
#
# SPDX-License-Identifier: Apache-2.0

import pathlib as pt

import streamlit as st

from dashboard.data.loaders import load_data
from dashboard.layout.sidebar import create_default_sidebar
from dashboard.tools import (
    DashboardConfiguration,
    add_contact_widget,
    add_reference_widget,
    load_plots_config,
    load_tab_modules,
    setup_default_tabs,
)

DASHBOARD_TITLE = "AMIRIS Dashboard"

if __name__ == "__main__":
    # load app configuration and prepare dependent values
    dash_cfg = DashboardConfiguration.load(pt.Path("./dashboard_config.json"))
    dash_cfg.prepare(load_tab_modules())

    # load plot configurations
    plots_cfg = load_plots_config(pt.Path("./configurations"))

    # init default style
    if "style" not in st.session_state:
        st.session_state["style"] = "light"

    # initialize active tab
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = dash_cfg.tabs[0].id

    # load data and metadata
    data, metadata = load_data(dash_cfg.data_path)

    st.set_page_config(page_title=DASHBOARD_TITLE, layout="wide")

    # create default sidebar
    with st.sidebar:
        create_default_sidebar(dash_cfg)

    root = st.container()

    # add default tabs layout
    with root:
        setup_default_tabs(dash_cfg, data, metadata, plots_cfg)
        add_reference_widget(dash_cfg)
        add_contact_widget(dash_cfg)
