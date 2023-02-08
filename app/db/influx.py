
from typing import Any, Dict, List

import requests
import datetime
import logging


class InfluxDB:

    log = logging.getLogger()

    def __init__(self, influxDB_host="http://influxdb:8086"):
        self.influxDB_host = influxDB_host

    def save(self, db_name, data: List):
        # Values should be a list of {"measurment",[tags],[values]}
        # EG: data = [{"measurement":"power","tags":{"house":"isbe","source":"solar"},"values":{"instant_power":5},"timestamp":datetime.datetime(2020,1,1,12,0,0)}]

        line_protocall_string = ""
        for x in data:
            if type(x) is dict:
                line_protocall_string += self._format_line_dict(x)
            elif type(x) is Measurement:
                line_protocall_string += str(x)

        self.log.info(db_name)
        # self.log.info(line_protocall_string)
        host = self.influxDB_host + '/write'
        params = {"db": db_name, "precision": "s"}  # Note, this precision value informs influx what precision the timestamp is in. It should almost always be seconds.
        try:
            r = requests.post(host, params=params, data=line_protocall_string, timeout=1)
            r.raise_for_status()
            self.log.debug('Pushed data to influx.')
            self.log.debug(f'{host}')
            self.log.debug(f'{params}')
            self.log.debug(f'{line_protocall_string}')
            self.log.debug(r)
        except Exception as e:
            self.log.exception("Error", e)
            self.log.error(params)
            self.log.error(line_protocall_string)
            try:
                self.log.error(r.content)
            except Exception:
                pass



    def _format_line_dict(self, data: list[dict[any,any]]):
        # <measurement>[,<tag_key>=<tag_value>[,<tag_key>=<tag_value>]] <field_key>=<field_value>[,<field_key>=<field_value>] [<timestamp>]

        ret_string = ""
        for line in data:
            ret_string += f"{line['measurement']}"
            if len(line['tags']):
                ret_string += ","
            ret_string += ",".join([f"{tag_key}={line['tags'][tag_key]}" for tag_key in line['tags']])
            # for tag_key in line['tags']:
            #     ret_string += f",{tag_key}={line['tags'][tag_key]}"
            ret_string += " "

            ret_string += ",".join([f"{tag_key}={line['values'][tag_key]}" for tag_key in line['values']])

            ret_string += " "
            ret_string += f"{int(line['timestamp'].timestamp())}"
            ret_string += "\n"
        return ret_string


class Measurement:

    reserved_names = [
        "ALL",           "ALTER",         "ANY",           "AS",            "ASC",           "BEGIN",       # noqa: E241
        "BY",            "CREATE",        "CONTINUOUS",    "DATABASE",      "DATABASES",     "DEFAULT",     # noqa: E241
        "DELETE",        "DESC",          "DESTINATIONS",  "DIAGNOSTICS",   "DISTINCT",      "DROP",        # noqa: E241
        "DURATION",      "END",           "EVERY",         "EXPLAIN",       "FIELD",         "FOR",         # noqa: E241
        "FROM",          "GRANT",         "GRANTS",        "GROUP",         "GROUPS",        "IN",          # noqa: E241
        "INF",           "INSERT",        "INTO",          "KEY",           "KEYS",          "KILL",        # noqa: E241
        "LIMIT",         "SHOW",          "MEASUREMENT",   "MEASUREMENTS",  "NAME",          "OFFSET",      # noqa: E241
        "ON",            "ORDER",         "PASSWORD",      "POLICY",        "POLICIES",      "PRIVILEGES",  # noqa: E241
        "QUERIES",       "QUERY",         "READ",          "REPLICATION",   "RESAMPLE",      "RETENTION",   # noqa: E241
        "REVOKE",        "SELECT",        "SERIES",        "SET",           "SHARD",         "SHARDS",      # noqa: E241
        "SLIMIT",        "SOFFSET",       "STATS",         "SUBSCRIPTION",  "SUBSCRIPTIONS", "TAG",         # noqa: E241
        "TO",            "USER",          "USERS",         "VALUES",        "WHERE",         "WITH",        # noqa: E241
        "WRITE",                                                                                            # noqa: E241
    ]

    def __init__(self,
                 measurement: str,
                 tags: Dict[str, str],
                 values: Dict[str, Any],
                 timestamp: datetime.datetime = None
                 ):
        self.measure_name = measurement
        self.tags = tags
        self.values = values
        self.timestamp = timestamp or datetime.datetime.now()

        if not isinstance(self.tags, dict):
            raise TypeError("`tags` must be of type `dict`.")
        if not isinstance(self.values, dict):
            raise TypeError("`values` must be of type `dict`.")
        if len(values) < 1:
            raise ValueError(f"`values` must have data, got len of {len(values)}")
        if len(tags) < 1:
            raise ValueError(f"`tags` must have data, got len of {len(tags)}")
        if not isinstance(self.measure_name, str):
            raise TypeError("`measurement` must be of type `str`")
        if len(self.measure_name) < 1:
            raise ValueError("`measurement` must have length")
        if any(x in self.measure_name for x in [' ', ',', '=']):
            raise ValueError(f"`measurement` has invalid characters: {self.measure_name}")
        if any(x.upper() in self.reserved_names for x in self.tags.keys()):
            raise ValueError("Invalid keyword in tags")
        if any(x in [' '] for x in self.tags.keys()):
            raise ValueError("Invalid character value in tags")
        if any(x.upper() in self.reserved_names for x in self.values.keys()):
            raise ValueError("Invalid keyword in tags")


    def __repr__(self):
        return self.__str__()


    def __str__(self):
        ret_string = ""
        ret_string += f"{self.measure_name}"
        if len(self.tags):
            ret_string += ","
        ret_string += ",".join([f"{tag_key}={self.tags[tag_key]}" for tag_key in self.tags])
        ret_string += " "
        ret_string += ",".join([f"{tag_key}={self.values[tag_key]}" for tag_key in self.values])
        ret_string += " "
        ret_string += f"{int(self.timestamp.timestamp())}"
        ret_string += "\n"
        return ret_string
