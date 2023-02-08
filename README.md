# rl-test-two
Second Rocket Lab Take Home Test


# Service Design

Making use of simply FastAPI features, combined with my existing influx helper lib, this service implements a very basic one file flow to and from the InfluxDB container. In most circumstances concince execution was favored over a more verbose object oriented approach, though the code can be broken into this approach trivially. This project makes no use of even the most basic security concerns, and will blindly accept valid data into the DB.

Retreval of data is tightly coupled to InfluxDB approaches, and may be an area of easy improovement. As the instructions did not clearly state if the input format is to be respected to the output, minimal changes occur as data transits into and out of the service.


# Execution Instructions

1. Checkout git repo onto a linux host running a version of docker >= `20.10.23`.
1. Run `docker compose build` to pull relevent images and build local services.
1. Run `docker compose up -d` to spinup server, guis, and databases.
1. Run `docker compose exec influxdb bash /influx_setup.sh` to initalize influx DB for execution.
1. Run `docker compose run client python populate_data.py` to populate given sample data into the InfluxDB.
1. Run `docker compose run client python get_data.py` to retrieve data from the DB and print to console.
    - The web server is running a FastAPI server accessable at `http://localhost:8000` (Assuming you are running locally, adjust as needed if running on a remote host!). You can see the docs for this server at  `http://localhost:8000/docs`, which will also enable you interactively explore the service!
    - You can edit the `./client/get_data.py` script to give different parameters to the query, these will be respected.
    - Of note, the returned strings will be in the given format of the sample data with a few key differences:
        - Time stamps will be returned in ISO 8601 format.
        - Floats will be given as they are stored within InfluxDB, capalization and accuray may be effected. Check use case to see if this needs to be corrected.
1. For testing, first run `docker compose down` to assure clean state. Then run `docker compose run server pytest` to see results of pytest tests.

Also of note, the service has not been setup to use any persistant volumes, out of respect for who's environemnt this ends up being run in. Data will not persist between runs unless you create a persistant volume for influxDB. If persistance is desired, you can create a mount into `/var/lib/influxdb` in the influx service container.


# Contributions

Kindly follow https://www.conventionalcommits.org/en/v1.0.0/ for commit messages.