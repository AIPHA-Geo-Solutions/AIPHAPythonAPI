import grequests
import requests
import argparse
import urllib
import json
import ssl
import time

class AiphaClient:
    def __init__(self, username, token, server_address, verifySSL=True):
      self.username = username
      self.token = token
      self.server_address = server_address
      self.verifySSL = verifySSL

    def get_username(self):
        return self.username

    def get_token(self):
        return self.token
    
    def get_server_address(self):
        return self.server_address
    
    def get_verify_ssl(self):
        return self.verifySSL


def check_command_arguments(
        command, 
        parameters, 
        command_dict
    ):
    if not command in command_dict:
      raise RuntimeError("Invalid command request: " + command + " does not exist")
    
    if 'in_parameters' in command_dict[command] and 'out_parameters' in command_dict[command]:
      valid_parameters = dict(**(command_dict[command]['in_parameters']), **(command_dict[command]['out_parameters']))
    elif 'in_parameters' in command_dict[command]:
      valid_parameters = command_dict[command]['in_parameters']
    elif 'out_parameters' in command_dict[command]:
      valid_parameters = command_dict[command]['out_parameters']
    else:
      valid_parameters = {}

    all_parameters = {}
    image_name = command_dict[command]['image']
    instance_parameters = {}
    if 'instance_type' in parameters:
        instance_parameters['instance_type'] = parameters['instance_type']
    elif 'instance_type' in command_dict[command]:
        instance_parameters['instance_type'] = command_dict[command]['instance_type']['default_value']
    for parameter in valid_parameters:
        if parameter in parameters:
            all_parameters[parameter] = str(parameters[parameter])
            if len(all_parameters[parameter]) > 0 and all_parameters[parameter][0] != "'":
                all_parameters[parameter] = "'" + all_parameters[parameter]
            if len(all_parameters[parameter]) > 0 and all_parameters[parameter][-1] != "'":
                all_parameters[parameter] = all_parameters[parameter] + "'"
            all_parameters[parameter] = all_parameters[parameter].replace('"', '\\"')
        else:
            all_parameters[parameter] = str(valid_parameters[parameter]['default_value'])
    return all_parameters, instance_parameters, image_name

glob_commands = {}
def import_commands(server_address,
                    verifySSL = True):
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
        server_address,
        verifySSL = True):
  available_commands = import_commands(server_address, verifySSL)
  all_parameters, instance_parameters, image_name = check_command_arguments(command, parameters_dictionary, available_commands)
  payload = { \
          'customerId': username, \
          'customerPassword': password, \
          'command': image_name, \
          'parameters': all_parameters, \
          'operator_name': command, \
          'instance_parameters': instance_parameters \
            }
  print("instance", instance_parameters)
  url = 'https://' + server_address +':443/run-operator'
  print(payload)
  r = grequests.post(url, json=payload, verify=verifySSL, timeout=90.)
  return r

def execute(requests):
    return grequests.map(requests, size=25)

def running_services_request(
        username,
        password,
        server_address,
        verifySSL = True):
  payload = { \
          'customerId': username, \
          'customerPassword': password, \
            }
  url = 'https://' + server_address +':443/get-running-services'
  r = requests.post(url, json=payload, verify=verifySSL)
  try:
    result = json.loads(r.text)
    if 'error' in result:
      for idx in range(10): #10 times retry
        time.sleep(60)
        r = requests.post(url, json=payload, verify=verifySSL)
        result = json.loads(r.text)
        if not 'error' in result:
            break
      if 'error' in result:
        raise RuntimeError('AIPHAProcessingError: ' + str(result['error']))
  except:
      raise RuntimeError('AIPHAProcessingError: ' + r.text)
  return result

def finished_services_request(
        username,
        password,
        service_ids,
        server_address,
        verifySSL = True):
  payload = { \
          'customerId': username, \
          'customerPassword': password, \
          'taskNames': service_ids, \
            }
  url = 'https://' + server_address +':443/tasks-are-finished'
  for idx in range(200): #max 200 times retry with 3 seconds delay
    try:
        r = requests.post(url, json=payload, verify=verifySSL)
        if r.status_code == 200:
          break
        time.sleep(3)
    except:
        time.sleep(3)
  try:
    result = json.loads(r.text)
    if 'error' in result:
        raise RuntimeError('AIPHAProcessingError: ' + str(result['error']))
  except:
      raise RuntimeError('AIPHAProcessingError: ' + r.text)
  return result



def check_services_completed(
        username,
        password,
        server_address,
        services,
        verifySSL = True):
  try:
    running_services =  running_services_request(
        username,
        password,
        server_address,
        verifySSL
    )
    services_dict = json.loads(running_services['running_processes'])
    for service_promise in services:
      service_id = service_promise
      print(service_id)
      this_complete = True #ignore services that have been deleted
      for running_service in services_dict:
        if service_id.startswith(running_service['ID']):
          this_complete = False
          if '1/1 completed' in running_service['Replicas']:
              this_complete = True
              break
      if this_complete == False:
          return False
    return True
  except:
    return False

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--username', type=str, default="", help='input folder')
  parser.add_argument('--password', type=str, default = "", help='input folder')
  parser.add_argument('--command', type=str, default = "hello world", help='output folder')
  parser.add_argument('--parameters_dictionary_str', type=str, default = '{"instance_type": "nano"}', help='command parameters as string in json format')
  parser.add_argument('--server_address', type=str, default = "18.198.190.23", help='Server address')
  args = parser.parse_args()

  parameters_dictionary = json.loads(args.parameters_dictionary_str)
  result = command_request(
        args.username,
        args.password,
        args.command,
        parameters_dictionary,
        args.server_address)
  print(result)
  completed = False
  while not completed:
    time.sleep(10)
    completed = check_services_completed(
        args.username,
        args.password,
        args.server_address,
        [result['pid']])
    print(completed)

