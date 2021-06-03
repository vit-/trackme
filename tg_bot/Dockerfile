FROM python:3.8-slim

COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY ./src /src
WORKDIR /src
CMD ["python", "-m", "trackme_bot"]
