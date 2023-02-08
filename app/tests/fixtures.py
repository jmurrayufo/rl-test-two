import datetime

import pytest
from unittest.mock import AsyncMock, patch, Mock

@pytest.fixture
def mock_influx():
    with patch('app.db.influx.InfluxDB', spec=True) as mock:
        mock.save = Mock(return_value=1)
        yield mock

@pytest.fixture
def mock_influx_measure():
    with patch('app.db.influx.Measurement', spec=True) as mock:
        mock.save = Mock(return_value=1)
        yield mock


@pytest.fixture
def mock_requests_get():
    with patch('requests.get', spec=True) as mock:
        yield mock


@pytest.fixture
def mock_requests_post():
    with patch('requests.post', spec=True) as mock:
        yield mock