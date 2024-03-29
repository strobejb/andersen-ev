# Andersen-EV 

Python package to enable control of the Andersen A2 EV charger. The library routes commands to the charger via Andersen's cloud API. So whilst the A2 cannot be controlled directly, this library could be used to replicate, or even replace the Konnect+ app.

## Installation

Install from PiPy:

```
pip install andersen-ev
```

Alternatively, install directly from this Github repo to get latest version:

```
pip install git+https://github.com/strobejb/andersen-ev
```

### Known Limitations

* Vehicle connection status cannot be reliably determined because this information is not available when the charger is in a locked/scheduled state. A workaround involves temporarily unlocking the charger, querying the EVSE connection state, and then re-enabling the schedules and/or user lock. See the `is-connected.py` example.
* The library currently supports username & password-base authentication, but 'device confirmation' is not yet implemented. This feature of the AWS cognito service would enable token-based authentication, meaning that the user's password does not need to be persisted.

## Authentication

Register your mobile phone with the Andersen Konnect+ app as normal. The email address and password used to register with Andersen are also needed by the python client to authenticate with the cloud API. User credentials should be protected and never hard-coded into scripts or source-control:

```python
from andersen_ev import AndersenA2

a2 = AndersenA2()
a2.authenticate(email=EMAIL, password=PASSWORD)
```

Device confirmation is not implemented yet, but will be soon. When this feature arrives, it will be possible to authenticate with an access token, meaning the password does not need to be persisted. 

## Basic Usage

Now that the python client is authenticated, the Andersen APIs be accessed. Andersen's API is based on GraphQL and returns JSON structures for all queries. This python library acts as a simple wrapper that performs the necessary GraphQL queries, and converts all return values into python dictionaries.

### Retrieve device ID 

This is the first step needed after authentication. Most functions exposed by this library will require the 'device ID' of your Andersen charger. This ID can be found using the `get_current_user_devices` function:

```python
devices = a2.get_current_user_devices()
deviceId = devices[0]['id']
```

The example above retrieves the ID of the first device (charger) registered with your account.
If you have more than one EV charger, then you will need to search by the name or ID of the device, or just use the `device_id_from_name` helper function:

```python
deviceId = a2.device_id_from_name('Charger Name Here')
```

### Enable scheduled charging

Scheduled charging can be resumed by enabling a specific schedule. The 'slot number' (an integer in the range 0-4) identifies the schedule as it appears in the Konnect app:

```python
a2.enable_schedule(deviceId, 0)
```
If the charger is locked, you might also want to unlock it at the same time to allow the schedule to take affect.

### Disable scheduled charging

The charger will most likely be running off an overnight schedule. The Konnect+ app lets you cancel the schedules, allowing any connected vehicle to start charging:

```python
a2.set_all_schedules_disabled(deviceId)
```
The command above disables all schedules and puts the charger into 'ready' (unlocked) state.

### Define a new schedule

A new schedule can be created by providing the schedule data (start & end time, and days applicable to). The slot number (0-4) needs to be specified separately as the 2nd parameter to the function:

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

Andersen chargers can be 'user locked' so that connected vehicles will not charge, and any scheduled charge events will also prevent the vehicle to charge.

```python
a2.user_lock(deviceId)
```

### Unlock the charger

The charger can also be unlocked, which will put it in the 'ready' state. Charging will commence if a vehicle is connected.

```python
a2.user_unlock(deviceId)
```

### Receive device status updates

It is possible to subscribe to device status updates sent by the cloud service, providing near-realtime information about what the charger is doing (what state it is in), and how much power is being used for charging connected vehicles. 

```python
import json

for result in a2.subscribe_device_updates(deviceId):
  j = json.dumps(result, indent=2)
  print(j)
``` 

The results of these notifications contain slightly more information than just querying (polling) the API directly. Specifically, the result includes the current charging status (power level, etc) and can be used to replicate what the Konnect+ app displays. There are lots of values available- just run the `examples/konnect-status.py` sample to see it in action.

Useful fields seem to be:

|Field|Description|
|---|---|
|`sysSchEnabled`|True when a schedule is enabled|
|`sysSchLocked`|True when the device is locked due to a schedule|
|`sysUserLock`|True then the device is user-locked (False when unlocked)|
|`chargePower`|The current charge level|
|`evseState`|device status / locked / charging |

Values for `evseState` are defined below. These appear to be the same values as
defined by the OpenEVSE specification.

|EVSE State|Description|
|---|---|
|1| Ready (disconnected) |
|2| Connected |
|3| Charging |
|4| Error |
|254| Sleeping |
|255| Disabled (locked by user, or schedule) |

There doesn't seem to be a reliable way to determine if a charger is physically connected, but not drawing power because of another reason. For example, if the charger is disabled because of a timed schedule, or locked by the user, the EVSE state always appears as 255 (disabled) even when a vehicle is connected. Only when the device is unlocked and there is no schedule enabled, will `evseState` reflect the connected/charging status.

I've also never observed the Andersen charger reporting the EVSE state as 254 (sleeping) which could be inferred as 'disabled due to a schedule'. These limitations are potentially a bug which could be rectified by future firmware update by Andersen.

### Example device status 

```python
{
  "deviceStatusUpdated": {
    "id": "....",
    "evseState": 255,         # 1=ready, 2=connected, 3=charging, 255=locked
    "online": true,           # Connected to cloud
    "sysRssi": -69,           # Wifi signal strength
    "sysSSID": "SSID HERE",   # SSID   
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
    "scheduleSlotsArray": [  # array of schedule slots
    ],
    "sysSchDSORandom": null  
}

```

## Examples

There are two examples that demonstate some of the functionality of the API:
* `examples/konnect-query.py` demonstrates how to lock & unlock, and enable charging schedules.
* `examples/konnect-status.py` is a basic example to demonstrate how to subscribe to device status events. 

Both examples need your credentials to run. These can be provided by creating a file called `examples/config.cfg`, and speciying your email and password in as follows:

```ini
[KONNECT]
email=user@example.com
password=...
```

## Change List

### v0.1.5
* Breaking change. JSON return values from API are no longer wrapped by the function name. 
* Return latest information available from API with `query_device_status` 
