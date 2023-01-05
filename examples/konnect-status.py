""" 
  Example python client that subscribes to the
  Andersen device status events
"""  

# append the path of the parent directory 
import sys  
sys.path.append("..")

# example client starts here
from andersen_ev import AndersenA2

import config
import json

a2 = AndersenA2()
a2.authenticate(email=config.EMAIL, password=config.PASSWORD)

#
# Retrieve the first device registered in this account
#
devices = a2.get_current_user_devices()
deviceId = devices['getCurrentUserDevices'][0]['id']

##
## Subscribe to the device status updates, and sit 
## in a simple blocking loop waiting for each event
##
for result in a2.subscribe_device_updates(deviceId):
  status = json.dumps(result, indent=2)
  print(status)

  print(f"Charge Level:    {result['deviceStatusUpdated']['chargeStatus']['chargePower']}")
  print(f"Locked:          {result['deviceStatusUpdated']['sysUserLock']}")
  print(f"Schedule Active: {result['deviceStatusUpdated']['sysSchEnabled']}")

