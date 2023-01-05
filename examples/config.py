import configparser
import sys

config = configparser.ConfigParser()

message = "Create this file in this directory with the following format:\n\n"\
  "[KONNECT]\n"\
  "email=user@example.com\n"\
  "password=example\n"

try:
  config.read_file(open('config.cfg', 'r'))
except FileNotFoundError:
  print("./config.cfg not found.")
  print(message)
  sys.exit(1)

try:
  EMAIL    = config['KONNECT']['email']
  PASSWORD = config['KONNECT']['password']
except KeyError:
  print("Missing credentials in ./config.cfg.\n")
  print(message)
  sys.exit(1)
