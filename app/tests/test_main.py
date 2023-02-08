
import requests

from ..main import app

from fastapi.testclient import TestClient
from dateutil.parser import parse as dt_parse

client = TestClient(app)

class TestMain:

    # In the interest of full coverage and concince code, the influx service is allowed to run within these test to save and respond with data as with production.
    # A more verbose test suite would do real unit testing with mocks (as per in `test_influx.py`) as well as intergration tests as we see here.


    def setup_method(self, test_method):
        requests.post("http://influxdb:8086/query", {"q": "CREATE DATABASE data"})


    def teardown_method(self, test_method):
        requests.post("http://influxdb:8086/query", {"q": "DROP DATABASE data"})


    def test_root_404(self):
        # No root is defined, we should expect a 404 here.
        response = client.get("/")
        assert response.status_code == 404
        assert response.json() == {"detail":"Not Found"}


    def test_data_put(self):
        # Valid data should input correctly and return a 201, item created.
        response = client.post("/data", content = "OEM_SCRATE_BDYX,2022-05-13T18:51:10Z,-5.0690708335691E-06,2200")
        assert response.status_code == 201


    def test_data_get(self):
        # Check if we can get a valid response when we ask for data, even if influx is currently empty.
        response = client.get("/data", params = {"apid": 2200, "limit": 50})
        assert response.status_code == 200
        assert response.text == "null" # Nothing should be in the DB


    def test_data_retreval(self):
        # Data should come back in a very similar form to what we put in.
        client.post("/data", content = "OEM_SCRATE_BDYX,2022-05-13T18:51:10Z,-5.0690708335691E-06,2200")

        response = client.get("/data")

        measurement,time,value,apid  = response.text.replace("\\n","").replace("\"","").split(",")

        measurement = str(measurement)
        time = dt_parse(time)
        value = float(value)
        apid = int(apid)

        assert measurement == "OEM_SCRATE_BDYX"
        assert time == dt_parse("2022-05-13T18:51:10Z")
        assert value == float("-5.0690708335691E-06")
        assert apid == int(2200)


    def test_avoid_duplicates(self):
        # Influx doesn't support duplicate timestamps. Anything within 1 second of another entry with equal metadata will overwrite the saved value.
        client.post("/data", content = "OEM_SCRATE_BDYX,2022-05-13T18:51:10Z,-5.0690708335691E-06,2200")
        client.post("/data", content = "OEM_SCRATE_BDYX,2022-05-13T18:51:10Z,-5.0690708335691E-06,2200")
        client.post("/data", content = "OEM_SCRATE_BDYX,2022-05-13T18:51:10Z,-5.0690708335691E-06,2200")
        client.post("/data", content = "OEM_SCRATE_BDYX,2022-05-13T18:51:10Z,-5.0690708335691E-06,2200")

        response = client.get("/data")

        text = response.text.replace("\"","")

        assert len(text.split("\\n")) == 2 # Null string expected on end, should have value of two.
        assert text.split("\\n")[1] == ""


    def test_bad_data(self):
        # We need to give full entries, partials should return 400's,
        response = client.post("/data", content = "OEM_SCRATE_BDYX,2022-05-13T18:51:10Z,-5.0690708335691E-06")
        assert response.status_code == 400


    def test_no_data(self):
        # We need to give full entries, partials should return 400's,
        response = client.post("/data")
        assert response.status_code == 400


    def test_bad_timestamp(self):
        # Valid data should input correctly and return a 201, item created.
        response = client.post("/data", content = "OEM_SCRATE_BDYX,NOT_EVEN_CLOSE_TO_TIME_STAMP,-5.0690708335691E-06,2200")
        assert response.status_code == 400


    def test_multi_entry(self):
        sim_data = """OEM_SCRATE_BDYX,2022-05-13T18:51:10Z,-5.0690708335691E-06,2200
OEM_SCRATE_BDYX,2022-05-13T18:51:20Z,-4.89050479960237E-06,2200
OEM_SCRATE_BDYX,2022-05-13T18:51:30Z,-4.64796773182267E-06,2200"""
        client.post("/data", content = sim_data)

        response = client.get("/data")

        text = response.text.replace("\"","")

        assert len(text.split("\\n")) == 4 # Four entries, and null from split.
