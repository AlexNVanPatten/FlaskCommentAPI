FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y --no-install-recommends python3 python3-pip sqlite3
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["app.py"]