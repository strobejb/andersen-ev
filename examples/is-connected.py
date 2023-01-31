#import paho.mqtt.client as mqtt #import the client1 
import sys; sys.path.insert(0, "../src")

from andersen_ev import AndersenA2

import config
import json
import time

def is_car_connected(a2, deviceId):

  device = a2.get_device(deviceId)
  print(json.dumps(device, indent=2))

  status = device['deviceStatus']
  evseState = status['evseState']

  # if EVSE state is locked, we can't tell if the car
  # is connected or not.
  if evseState == 255:
    print(f'{status["evseState"]} (locked); temporarily unlocking:')
    
    if status['sysUserLock']:
      a2.user_unlock(deviceId)
    
    if status['sysScheduleLock']:
      a2.set_all_schedules_disabled(deviceId)

    # wait for the device status to reflect unlocked state
    while evseState == 255:
      status0 = a2.get_device_status(deviceId)
      evseState = status0['deviceStatus']['evseState']
      if evseState == 255:
        time.sleep(5)

    # restore userLock
    if status['sysUserLock']:
      print('restoring userLock')
      a2.user_lock(deviceId)
    
    # restore schedules
    if status['sysScheduleLock']:
      slots = { f'sch{slot}': schedule 
        for slot,schedule in 
          enumerate(status['scheduleSlotsArray'])
          }
      print('restoring schedules')
      a2.set_schedules(deviceId, slots)

  #
  print(f'evseState: {evseState}')
  if evseState == 2 or evseState == 3:
    return True
  else:
    return False

a2=AndersenA2()
a2.authenticate(email=config.EMAIL, password=config.PASSWORD)

devices = a2.get_current_user_devices()
deviceId = devices[0]['id']
print(deviceId)

print(f'Connected: { is_car_connected(a2, deviceId) }')

