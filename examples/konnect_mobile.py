# prepend the path of the src directory. only needed for testing
# within this repo - remove these lines for your own projects 
import sys; sys.path.insert(0, "../src")

""" 
  Example python client to use the Mobile API. It is unclear
  why this API is needed; all functionality appears to be contained
  in the GraphQL API
"""  
from andersen_ev import AndersenMobile
import json
import config

#
# Andersen Mobile API
# 
am =AndersenMobile()
am.authenticate(email=config.EMAIL, password=config.PASSWORD)

# get the device ID. this seems to be the only API
devices = am.get_devices()
print(json.dumps(devices, indent=2))

deviceId = devices['devices'][0]['id']
print(f'deviceId: {deviceId}')

