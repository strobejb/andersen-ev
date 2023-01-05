# Andersen-EV 

Python package to enable control of the Andersen A2 EV charger. This library provides a client-side interface to the cloud API used by the Andersen Konnect+ mobile app.

The underlying Andersen API is implemented using GraphQL. 

## Installation

```
pip install andersen-ev
```

Alternatively install directly from this Github repo:

```
pip install git+https://github.com/strobejb/andersen-ev
```

## Authentication

Register your mobile phone with the Andersen charger (if not already done), using the Konnect+ app as normal. The email address and password used to register with Andersen must be used with the python client to authenticate with the cloud API. User credentials should be protected and not hard-coded into scripts or source-control:

```python
from andersen_ev import AndersenA2
import json

a2 = AndersenA2()
a2.authenticate(email=EMAIL, password=PASSWORD)
```

Now that the python client is authenticated, the Andersen API service can be accessed. The API is based on GraphQL and returns JSON structures for all queries. The python library converts all return values into python dictionaries.

Device confirmation is not implemented yet, but will be soon. When this feature arrives, it will be possible to authenticate with an access token, meaning the password does not need to be persisted. 

## Basic Usage
### Retrieve device ID 

Most functions require the 'device ID' of your Andersen charger. This ID
can be found using the `get_current_user_devices` function:

```python
devices = a2.get_current_user_devices()
deviceId = devices[0]['id']
```

The example above retrieves the ID of the first device (charger) registered with the account.
If you have more than one EV charger, then you will need to need to search by the name or ID of the device, or use the `device_id_from_name` helper function:

```python
deviceId = a2.device_id_from_name('Charger Name Here')
```

### Enable scheduled charging

Scheduled charging can be resumed by enabling a specific schedule. The 'slot number' (an integer in the range 0-4) identifies the schedule as it appears in the Konnect app:

```python
a2.enable_schedule(deviceId, 0)
```
If the charger is locked, you would also want to unlock it at the same time to allow the schedule to take affect:

### Disable scheduled charging

The charger will most likely be running off an overnight schedule. The Konnect+ app lets you cancel the schedules, and a connected vehicle wil start charging:

```python
a2.set_all_schedules_disabled(deviceId)
```
The command above disables all schedules and puts the charger into 'ready' (unlocked) state.

### Define a new schedule

A new schedule can be created by providing the schedule data (start & end time, and days applicable to). The slot number (0-4) needs to be specified separately:

```python
schedule = {
  'startHour': 0,
  'startMinute': 30,
  'endHour': 4,
  'endMinute': 30,
  'enabled': True,
  "dayMap": {
    "monday": True,
    "tuesday": True,
    "wednesday": True,
    "thursday": True,
    "friday": True,
    "saturday": True,
    "sunday": True
  }
}
a2.create_schedule(deviceId, 0, schedule)
```

### Lock the charger

Andersen chargers can be locked so that connected vehicles will not charge, and any scheduled charge events will not cause the vehicle to charge.

```python
a2.user_lock(deviceId)
```

### Unlock the charger

The charger can also be unlocked, which will put it in the 'ready' state. Charging will commence if a vehicle is connected.

```python
a2.user_unlock(deviceId)
```

### Receive device status updates

It is possible to subscribe to device status updates. Websockets are used to receive notifications
from the Andersen cloud service:

```python
for result in a2.subscribe_device_updates(deviceId):
  j = json.dumps(result, indent=2)
  print(j)
``` 

The results of these notifications contain slightly more information than just querying (polling) the API directly. Specifically, the result includes the current charging status (power level, etc) and can be used to replicate what the Konnect app displays.

Useful fields seem to be:
|Field|Description|
|---|---|
|`sysSchEnabled`|True when a schedule is active|
|`sysUserLock`|True then the device is locked (False when unlocked)|
|`chargePower`|The current charge level|
|`evseState`|255 for ready, 1 (device locked), 3 (connected) |

There are lots of other values - just run the `examples/konnect-updates.py` sample, or look inside `andersen_ev/andersen.graphql` to see them all.

There doesn't seem to be any way to determine if a charger is physically connected - only that the device is drawing power, which can be used to infer that a vehicle is connected and charging.   

```python
{
  "deviceStatusUpdated": {
    "id": "....",
    "evseState": 255,     # 255=ready, 1=locked
    "online": true,
    "sysRssi": -69,
    "sysSSID": "WIFI SSID",
    "sysSchEnabled": True,    # True when a schedule is active
    "sysUserLock": False,     # Is device Locked
    "sysScheduleLock": True,  # True when schedule is active
    "sysSolarPower": null,
    "sysGridPower": null,
    "solarMaxGridChargePercent": 100,
    "solarChargeAlways": true,
    "solarOverride": false,
    "cfgCTConfig": 1,
    "chargeStatus": {
      "start": "2023-01-05T00:30:00Z",
      "chargeEnergyTotal": 9.128312,
      "chargePower": 0,      # current charge level
      "duration": 8472
    },
}

```

## Examples

There are two examples that demonstate some of the functionality of the API:
* `examples/konnect-query.py` demonstrates how to lock & unlock, and enable charging schedules.
* `examples/konnect-status.py` is a basic example to demonstrate how to subscribe to device update events. 

Both exmples need your credentials to run. Create file called `examples/config.cfg` and put your email and password in this file:

```ini
[KONNECT]
email=user@example.com
password=...
```
