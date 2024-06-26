# SPDX-FileCopyrightText: Florian Maurer
#
# SPDX-License-Identifier: Apache-2.0

FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
