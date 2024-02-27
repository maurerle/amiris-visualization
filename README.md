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