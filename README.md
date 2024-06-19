<!--
SPDX-FileCopyrightText: Florian Maurer

SPDX-License-Identifier: Apache-2.0
-->

# AMIRIS visualization scripts

This repository contains visualizations created for results of various studies.
It currently contains

* the AMIRIS-ASSUME study from the EEM2024

This repository can be used as following:

0. make sure you have access to a postgresql server and enter the db_uri into a newly created `config.py`
1. clone [Amiris-Examples](https://gitlab.com/dlr-ve/esy/amiris/examples) into a folder next to this repository:
`git clone https://gitlab.com/dlr-ve/esy/amiris/examples ../amiris-examples`
1. run `pip install -r requirements.txt`
2. run amiris and assume run to produce the dataset `python amiris_run.py`
3. run the evaluation scripts using `python amiris_eval.py`

# Preprocessing

Now you should have all data in the output/csv folder.
If not, you can checkout the branch including csv data using `git checkout including_data`.

You can then run `python dashboard_data_processing.py` to create the compare.hdf5 file.

This is the main data file used by the streamlit dashboard, which we run in the next step.

# Streamlit Dashboard

To run the streamlit dashboard, you can use the existing compare.hdf5 file and simply run `streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0` to have the dashboard accessible for everyone.

That's it.