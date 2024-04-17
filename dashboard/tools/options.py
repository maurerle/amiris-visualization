# SPDX-FileCopyrightText: 2024 German Aerospace Center
#
# SPDX-License-Identifier: Apache-2.0
import streamlit as st
import collections.abc


def __update(org, up):
    for k, v in up.items():
        if isinstance(v, collections.abc.Mapping):
            org[k] = __update(org.get(k, {}), v)
        else:
            org[k] = v
    return org


def __delete(org, dels):
    for k, v in dels.items():
        if k not in org:
            continue
        if v is None:
            del org[k]
        if isinstance(v, collections.abc.Mapping):
            org[k] = __delete(org[k])
    return org


def delete_barred_user_overrides(options, deletes=None):
    deletes = deletes if deletes is not None else {}
    options = __delete(options, deletes)
    return options


def update_options_with_overrides(options, user):
    return __update(options, user)


def update_options_with_defaults(options):
    defaults = {
        "backgroundColor": "#FFFFFF"
        if st.session_state["style"] != "dark"
        else "#0E1117",
        "toolbox": {
            "orient": "vertical",
            "show": True,
            "feature": {
                "dataView": {"readOnly": False},
                "restore": {},
            },
        },
    }
    return __update(options, defaults)
