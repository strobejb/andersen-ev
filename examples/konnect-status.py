# prepend the path of the src directory. only needed for testing
# within this repo - remove these lines for your own projects 
import sys; sys.path.insert(0, "../src")

""" 
  Example python client that subscribes to the
  Andersen device status events
"""  
from andersen_ev import AndersenA2

import config
import json

a2 = AndersenA2()
a2.authenticate(email=config.EMAIL, password=config.PASSWORD)

#
# Retrieve the first device registered in this account
#
devices = a2.get_current_user_devices()
deviceId = devices[0]['id']

##
## Subscribe to the device status updates, and sit 
## in a simple blocking loop waiting for each event
##
for result in a2.subscribe_device_updates(deviceId):
  status = json.dumps(result, indent=2)
  print(status)

  deviceStatus = result['deviceStatusUpdated']

  print(f"Charge Level:     {deviceStatus['chargeStatus']['chargePower']}")
  print(f"Charging Enabled: {deviceStatus['sysChargingEnabled']}")
  print(f"User Locked:      {deviceStatus['sysUserLock']}")
  print(f"Schedule Enabled: {deviceStatus['sysSchEnabled']}")
  print(f"Schedule Locked:  {deviceStatus['sysScheduleLock']}")
  print(f"EVSE State:       {deviceStatus['evseState']}")

