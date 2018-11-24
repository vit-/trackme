FROM python:3.7

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install -r /tmp/requirements.txt
ADD src /src
