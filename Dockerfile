FROM python:3.5-stretch

WORKDIR /opt/trackme

ADD src/requirements.txt .
RUN pip install -r requirements.txt

ADD . .
RUN pip install -e src/
