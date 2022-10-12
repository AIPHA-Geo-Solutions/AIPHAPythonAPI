import argparse
from aipha.webservice_api import AiphaClient
import aipha.operators as ao

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--username', type=str, default="", help='input folder')
  parser.add_argument('--token', type=str, default = "", help='input folder')
  parser.add_argument('--server_address', type=str, default = "18.198.190.23", help='Server address')
  args = parser.parse_args()

  client = AiphaClient(args.username, args.token, args.server_address)

  print('list all running processes')
  running_processes = ao.list_running_services(client)
  print(running_processes)
  print('starting new process')
  res = ao.hello_world(client)
  print('started process ' + res['pid'])

  print('waiting for process to complete...')
  ao.wait_for_completion(client, [res['pid']])
  print('completed')
