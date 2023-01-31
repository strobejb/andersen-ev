# prepend the path of the src directory. only needed for testing
# within this repo - remove these lines for your own projects 
import sys; sys.path.insert(0, "../src")

""" 
  Example python client to Authenticate with the AndersenEV cloud API
  and exercise various queries 
"""  
from andersen_ev import AndersenA2

import json
import config

a2 = AndersenA2()
a2.authenticate(email=config.EMAIL, password=config.PASSWORD)


#
# Retrieve the first device registered in this account
#
devices = a2.get_current_user_devices()
deviceId = devices[0]['id']
#deviceId = devices['getCurrentUserDevices'][0]['id']

deviceInfo = a2.get_device(deviceId)
print(json.dumps(deviceInfo, indent=2))

result = a2.get_device_charge_rates(deviceId)
print(json.dumps(deviceInfo, indent=2))

deviceLora = a2.get_device_lora(deviceId)
print(json.dumps(deviceLora, indent=2))

message = a2.get_support_message()
print(json.dumps(message, indent=2))

deviceSolar = a2.get_device_solar(deviceId)
print(json.dumps(deviceSolar, indent=2))

##xx
deviceInfo = a2.get_device(deviceId)
print(json.dumps(deviceInfo, indent=2))

chargeRates = a2.get_device_charge_rates(deviceId)
print(json.dumps(chargeRates, indent=2))

deviceLora = a2.get_device_lora(deviceId)
print(json.dumps(deviceLora, indent=2))


sys.exit(0)

# mutation examples that will change the charger state:

#
#   Unlock - requires that we run the 'userUnlock' 
#   AEV command, and also disable all schedules 
#
message = a2.user_unlock(deviceId)
print(json.dumps(message, indent=2))

#
# Cancel Schedules (whilst paused) - requires that we use the
# single set_all_schedules_disabled query
#
message = a2.set_all_schedules_disabled(deviceId)
print(json.dumps(message, indent=2))

# Disable (whlst charging) - requires that we 
# use the userLock command
message = a2.user_lock(deviceId)
print(json.dumps(message, indent=2))
