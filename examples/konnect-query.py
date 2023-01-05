""" 
  Example python client to Authenticate with the AndersenEV cloud API
"""  

# append the path of the parent directory 
import sys  
sys.path.append("..")

# example client starts here
from andersen_ev import AndersenA2

import json
import config

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

#a2.subscribe_device_updates(deviceId)
sys.exit(0)

#a2.confirm_device('my-device-name')

#a2.register_mobile_




#
#   Unlock - requires that we run the 'userUnlock' 
#   AEV command, and also disable all schedules 
#
message = a2.run_aev_command(deviceId, "userUnlock")
print(json.dumps(message, indent=2))





#
# Cancel Schedules (whilst paused) - requires that we use the
# single set_all_schedules_disabled query
#
message = a2.set_all_schedules_disabled(deviceId)
print(json.dumps(message, indent=2))

# Disable (whlst charging) - requires that we 
# use the userLock command
message = a2.run_aev_command(deviceId, "userLock")
print(json.dumps(message, indent=2))


#message = a2.enable_schedule(deviceId, 0)
#print(json.dumps(message, indent=2))

#message = a2.get_solar(deviceId)
#print(json.dumps(message, indent=2))


#xx
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



#u.verify_tokens()

#import boto3
#cognito = boto3.client('cognito-identity', 'eu-west-1')
#response = cognito.get_credentials_for_identity(IdentityId = "23s0olnnniu5472ons0d9uoqt9")
#cognito.confirm_device()
#print(response)
#u.get_credentials_for_identity(IdentityId = "")