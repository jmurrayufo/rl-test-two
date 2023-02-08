
import logging
import pytest
import json
import datetime

from app.db import influx

from .fixtures import mock_requests_get, mock_requests_post  # noqa


def test_influx_line_dict_formating():
    x = influx.InfluxDB()

    # We should be able to format a dict into a string
    ret_value = x._format_line_dict([{"measurement": "test", "tags": {"my": "tag"}, "values": {"my": "value"}, "timestamp": datetime.datetime.now(tz=datetime.timezone.utc)}])
    assert "test,my=tag my=value " in ret_value


def test_influx_measures():
    # Creation with value arguments should have no issue.
    influx.Measurement("test", {"my": "tag"}, {"my": "value"}, datetime.datetime.now(tz=datetime.timezone.utc))

    with pytest.raises(TypeError):
        influx.Measurement("test", None, {"my": "value"}, datetime.datetime.now(tz=datetime.timezone.utc))

    with pytest.raises(TypeError):
        influx.Measurement("test", {"my": "tag"}, None, datetime.datetime.now(tz=datetime.timezone.utc))

    with pytest.raises(ValueError):
        influx.Measurement("test", {"my": "tag"}, {}, datetime.datetime.now(tz=datetime.timezone.utc))

    with pytest.raises(TypeError):
       influx.Measurement(123, {"my": "tag"}, {"my": "value"}, datetime.datetime.now(tz=datetime.timezone.utc))

    with pytest.raises(ValueError):
       influx.Measurement("", {"my": "tag"}, {"my": "value"}, datetime.datetime.now(tz=datetime.timezone.utc))

    with pytest.raises(ValueError):
       influx.Measurement("invalid,", {"my": "tag"}, {"my": "value"}, datetime.datetime.now(tz=datetime.timezone.utc))

    with pytest.raises(ValueError):
       influx.Measurement("invalid ", {"my": "tag"}, {"my": "value"}, datetime.datetime.now(tz=datetime.timezone.utc))

    with pytest.raises(ValueError):
       influx.Measurement("invalid=", {"my": "tag"}, {"my": "value"}, datetime.datetime.now(tz=datetime.timezone.utc))

    with pytest.raises(ValueError):
        influx.Measurement("test", {"USER": "tag"}, {"my": "value"}, datetime.datetime.now(tz=datetime.timezone.utc))

    with pytest.raises(ValueError):
        influx.Measurement("test", {" ": "tag"}, {"my": "value"}, datetime.datetime.now(tz=datetime.timezone.utc))

    with pytest.raises(ValueError):
        influx.Measurement("test", {"my": "tag"}, {"USER": "value"}, datetime.datetime.now(tz=datetime.timezone.utc))