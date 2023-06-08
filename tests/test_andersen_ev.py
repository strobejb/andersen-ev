import sys; 
sys.path.insert(0, "../src")      # A2 module
sys.path.insert(0, "../examples") # config loader

# force tests to run from tests/ directory
import os
import pathlib
os.chdir(pathlib.Path(__file__).parent)

##
## TESTING STARTS HERE
##
from andersen_ev import AndersenA2

import pytest
import json
import jsonschema
import config
import jsonref

def load_json_schema(filename):
    """ Loads the given schema file """
    schemadir  = pathlib.Path(__file__).parent / 'schemas'
    schemapath = schemadir / filename
    base_uri   = 'file:///{}/'.format(schemadir)
    
    with open(schemapath) as schema_file:
        return jsonref.loads(schema_file.read(), base_uri=base_uri, jsonschema=True)

def validate_schema(data, schemafile):
    """ Checks whether the given data matches the schema """
    try:
      schema = load_json_schema(schemafile)
      jsonschema.validate(instance=data, schema=schema)
      return True

    except jsonschema.exceptions.ValidationError as err:
      print('Validation Error')
      print(err.message)
      return False
      
    except jsonschema.exceptions.SchemaError as err:
      print('Schema Error')
      print(err.message)      
      return False

##
## FIXTURES
##

@pytest.fixture(scope="session")
def a2():
  """ connect to the Andersen API """
  a2 = AndersenA2()
  a2.authenticate(email=config.EMAIL, password=config.PASSWORD)
  return a2

@pytest.fixture(scope="session")
def deviceId(a2):
  """ retrieve device ID for first device to test """
  devices = a2.get_current_user_devices()
  deviceId = devices[0]['id']
  return deviceId

##
## TESTS
##

def test_get_current_user_devices(a2):

  devices = a2.get_current_user_devices()

  assert type(devices) is list
  assert len(devices) >= 1  
  assert validate_schema(devices, "get_current_user_devices.json")

def test_get_device_status(a2, deviceId):

  deviceStatus = a2.get_device_status(deviceId)

  assert type(deviceStatus) is dict
  assert validate_schema(deviceStatus, "get_device_status.json")

##
## MAIN
##
if __name__ == '__main__':
    pytest.main(['-v'])
