FROM python:3.11-slim

# TODO: Convery to a requiremnts.txt file.
RUN python -m pip install fastapi uvicorn[standard] pymongo httpx pytest requests python-dateutil

WORKDIR /app