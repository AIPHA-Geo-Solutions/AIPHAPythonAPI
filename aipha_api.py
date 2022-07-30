import requests
import argparse
import urllib
import json
import ssl

verifySSL = False #TODO: verifySSL=True

def check_command_arguments(
        command, 
        parameters, 
        command_dict
    ):
    if not command in command_dict:
      raise RuntimeError("Invalid command request: " + command + " does not exist")
    valid_parameters = dict(**(command_dict[command]['in_parameters']), **(command_dict[command]['out_parameters']))
    all_parameters = {}
    image_name = command_dict[command]['image']
    instance_parameters = {}
    if 'instance_type' in command_dict[command]:
        instance_parameters['instance_type'] = command_dict[command]['instance_type']['default_value']
    for parameter in valid_parameters:
        if parameter in parameters:
            all_parameters[parameter] = parameters[parameter]
        elif 'parameter' == instance_type:
            instance_parameteters['instance_type'] = parameters[parameter]
        else:
            all_parameters[parameter] = valid_parameters[parameter]['default_value']
    return all_parameters, instance_parameters, image_name

glob_commands = {}
def import_commands(server_address):
    url = "https://" + server_address + "/default_functions.json"
    global glob_commands
    if glob_commands != {}:
        return glob_commands
    if not verifySSL:
      ctx = ssl.create_default_context()
      ctx.check_hostname = False
      ctx.verify_mode = ssl.CERT_NONE
      commands_string = urllib.request.urlopen(url, context=ctx).read()
    else:
      commands_string = urllib.request.urlopen(url).read()
    commands = json.loads(commands_string)
    glob_commands = commands
    return commands

def command_request(
        username,
        password,
        command,
        parameters_dictionary,
        server_address):
  available_commands = import_commands(server_address)
  all_parameters, instance_parameters, image_name = check_command_arguments(command, parameters_dictionary, available_commands)
  payload = { \
          'customerId': username, \
          'customerPassword': password, \
          'command': image_name, \
          'parameters': all_parameters, \
          'operator_name': command, \
          'instance_parameters': instance_parameters \
            }
  url = 'https://' + server_address +':443/run-operator'
  r = requests.post(url, json=payload, verify=verifySSL)
  try:
    result = json.loads(r.text)
    if 'error' in result:
      raise RuntimeError('AIPHAProcessingError: ' + result['error'])
  except:
      raise RuntimeError('AIPHAProcessingError: ' + r.text)
  return result

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--username', type=str, default="", help='input folder')
  parser.add_argument('--password', type=str, default = "", help='input folder')
  parser.add_argument('--command', type=str, default = "hello world", help='output folder')
  parser.add_argument('--parameters_dictionary_str', type=str, default = '{"instance_type": "nano"}', help='command parameters as string in json format')
  parser.add_argument('--server_address', type=str, default = "18.156.36.243", help='Server address')
  args = parser.parse_args()

  parameters_dictionary = json.loads(args.parameters_dictionary_str)
  command_request(
        args.username,
        args.password,
        args.command,
        parameters_dictionary,
        args.server_address)
