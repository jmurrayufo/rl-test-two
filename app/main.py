import requests

from typing import List

from fastapi import FastAPI, HTTPException, status, Response, Request, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from dateutil.parser import parse as dt_parse

from .db.influx import InfluxDB, Measurement

"""
3. The application should expose REST endpoints to:

a. POST data to the server
i. This data should be deserialized into an object
ii. ... mutated in some way
1. ex: time conversion, down-sampled, mathematical aggregation
iii. ... Saved to the database

b. GET data back from the server
i. Based on a Get request, data should be fetched from the database
ii. ... formatted for return based on user input
iii. ... returned to the user in the body of the response

4. The Database can be SQL or NoSQL:
a. SQL Database suggestions (not required): Postgres, SQLite, MySQL, MariaDB, etc...
b. NoSQL Database suggestions (not required): MongoDB, InfluxDB, Prometheus, Cassandra, Redis,
etc...
"""

app = FastAPI()

@app.post("/data", status_code = 201)
async def publish_influx_data(request: Request, response: Response):
    # Invalid data on any line will result in the entire post failing, and no data will be added.

    influx_db = InfluxDB()

    text = (await request.body()).decode()

    influx_measures = []

    for line in text.split("\n"):
        values = line.split(",")
        if len(values) != 4:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return
        measurement,time,value,apid = line.split(",")

        try:
            measurement = str(measurement)
            time = dt_parse(time)
            value = float(value)
            apid = int(apid)
        except:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return


        measure = Measurement(
            "test_measure",
            {
                "measurement_name": measurement,
                "apid": apid,
            },
            {
                "value": value,
            },
            time,
        )

        influx_measures.append(measure)

    influx_db.save("data", influx_measures)

    return

@app.get("/data", status_code = 200)
async def request_influx_data(
        response: Response,
        apid: int = None,
        measurement: str = None,
        limit: int = 5,
    ):

    query_str = "SELECT value FROM test_measure"

    if apid or measurement:
        query_str += " WHERE"

        where_clauses = []

        if apid:
            where_clauses.append(f' "apid"=\'{apid}\'')

        if measurement:
            where_clauses.append(f' "measurement_name"=\'{measurement}\'')

        query_str += " AND ".join(where_clauses)

    query_str += " GROUP BY *"
    query_str += f" LIMIT {limit}"

    # TODO: Not generally needed to pull data from influx via code. Should look at adding a `get()` function to the influx lib to make life easier.
    response = requests.post(
        "http://influxdb:8086/query",
        params = {
            "db": "data",
            "q": query_str
        }
    )

    # Build response to format the same as initial input
    # measurement,time,value,apid
    response_str = ""

    if "series" not in response.json()["results"][0]:
        return None

    for series in response.json()["results"][0]["series"]:
        for value in series["values"]:
            time = dt_parse(value[0])
            response_str += f"{series['tags']['measurement_name']},{time.isoformat()},{value[1]},{series['tags']['apid']}\n"

    return response_str