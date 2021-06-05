FROM python:3.6.8

WORKDIR /app
RUN apt-get update && apt-get install --yes unzip postgresql postgresql-contrib
# RUN pip install --upgrade pip
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . .
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]