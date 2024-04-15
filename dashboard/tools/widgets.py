import streamlit as st
from markdownlit import mdlit
import pathlib as pt
import pandas as pd

from dashboard.tools.general import create_qrcode
from base64 import b64encode
from io import BytesIO


def setup_default_tabs(dash_cfg, data, metadata, plots_cfg):
    for itab in dash_cfg.tabs:
        if itab.id in ["references", "contacts"]:
            continue
        if st.session_state["active_tab"] == itab.id:
            mdlit(f"# {itab.label}")
            if itab.display_infobox:
                with st.expander(
                    f"{itab.display_icon} {itab.display_label}",
                    expanded=itab.display_enabled,
                ):
                    st.markdown(
                        itab.text
                        if itab.text is not None
                        else "".join(itab.path.open().readlines())
                    )
            itab.tab_ref.create(data, metadata, plots_cfg)


def add_contact_widget(dash_cfg):
    itab = None
    for i in dash_cfg.tabs:
        if i.id == "contacts":
            itab = i
            break

    if st.session_state["active_tab"] == itab.id:
        st.header(itab.label)
        mdlit("".join(pt.Path("./contact_info.md").open().readlines()))


def add_reference_widget(dash_cfg):
    if dash_cfg.enable_references:
        itab = None
        for i in dash_cfg.tabs:
            if i.id == "references":
                itab = i
                break
        if st.session_state["active_tab"] == itab.id:
            st.header(itab.label)
            txt = "These are the references:\n\n"
            refs = "".join(["- {}\n\n"] * len(dash_cfg.references))
            mdlit(txt + refs.format(*dash_cfg.references))


def add_data_download_button(
    data: pd.DataFrame, file_name="data", label="download data"
):
    st.download_button(
        label,
        data.to_csv().encode("utf-8"),
        f"{file_name}.csv",
        "text/csv",
    )


def insert_sidebar_qrcode(url: str, url_text: str):
    qr = create_qrcode(url)

    img_io = BytesIO()
    qr.resize((200, 200)).save(img_io, "PNG")

    st.markdown(
        f'<p style="text-align: center; color: grey;"><a href="{url}"><img src="data:image/png;base64,{b64encode(img_io.getvalue()).decode("ascii")}" alt="{url_text}"/></p>',
        unsafe_allow_html=True,
    )
