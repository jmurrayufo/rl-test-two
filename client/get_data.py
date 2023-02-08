import requests

server_base_url = "http://server:8000"

response = requests.get(server_base_url + "/data", params = { "limit": 10}) # "apid": 2200, "measurement": "OEM_SCRATE_BDYY",
print(response)
print(response.text)

print(requests.get(server_base_url).text)