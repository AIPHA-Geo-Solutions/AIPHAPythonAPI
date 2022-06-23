import requests
import argparse
import urllib
import json
import ssl


def import_commands(server_address):
    url = "https://" + server_address + "/default_functions.json"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE #TODO: enforce checking of ssl certificate
    commands_string = urllib.request.urlopen(url, context=ctx).read()
    commands = json.loads(commands_string)
    return commands

def check_command_arguments(
        command, 
        arguments, 
        command_dict
    ):
    if not command in command_dict:
      #raise RuntimeError("Invalid command request: " + command + " does not exist")
      return {}
    valid_parameters = dict(command_dict['in_parameters'], *command_dict['out_parameters'])
    all_parameters = {}
    for parameter in valid_parameters:
        print(parameter)
    return all_parameters

def command_request(
        username,
        password,
        command,
        parameters_dictionary,
        server_address):
  available_commands = import_commands(server_address)
  all_parameters = check_command_arguments(command, parameters_dictionary, available_commands)
  print(available_commands)
  payload = {'customerId': username, 'customerPassword': password, 'command': command, 'parameters': all_parameters}
  url = 'https://' + server_address +':443/run-operator'
  r = requests.post(url, json=payload, verify=False) #TODO: enforce checking of ssl certificates
  print(r.text)
  return r

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--username', type=str, default="cus_KirpTL8mvhAHRB", help='input folder')
  parser.add_argument('--password', type=str, default = "", help='input folder')
  parser.add_argument('--command', type=str, default = "hello-world", help='output folder')
  parser.add_argument('--parameters_dictionary', type=str, default = "", help='command parameters')
  parser.add_argument('--server_address', type=str, default = "3.122.238.243", help='Server address')
  args = parser.parse_args()

  command_request(
        args.username,
        args.password,
        args.command,
        args.parameters_dictionary,
        args.server_address)
