import configparser
import sys
import pathlib

config = configparser.ConfigParser()

message = "Create this file in this directory with the following format:\n\n"\
  "[KONNECT]\n"\
  "email=user@example.com\n"\
  "password=example\n"

try:
  configpath = pathlib.Path(__file__).parent / 'config.cfg'
  config.read_file(open(configpath, 'r'))
except FileNotFoundError:
  print(f"{configpath} not found.")
  print(message)
  sys.exit(1)

try:
  EMAIL    = config['KONNECT']['email']
  PASSWORD = config['KONNECT']['password']
except KeyError:
  print(f"Missing credentials in {configpath}\n")
  print(message)
  sys.exit(1)
