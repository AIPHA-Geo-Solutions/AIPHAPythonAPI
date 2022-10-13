import argparse
from aipha_geo_solutions.webservice_api import AiphaClient
import aipha_geo_solutions.operators as ao

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--username', type=str, default="", help='user name for AIPHA webservices')
  parser.add_argument('--token', type=str, default = "", help='Token for AIPHA webservices. Please not that passing tokens via command line is insecure. Consider using enviroment variables or reading from config files instead')
  parser.add_argument('--server_address', type=str, default = "18.198.190.23", help='Server address')
  args = parser.parse_args()

  client = AiphaClient(args.username, args.token, args.server_address)

  print('list all running processes')
  running_processes = ao.list_running_services(client)
  print(running_processes)
  print('starting new process')
  res = ao.create_directory_in_cloud(client, '/api_test')
  print('started process ' + res['pid'])

  print('waiting for process to complete...')
  ao.wait_for_completion(client, [res['pid']])
  print('completed')
