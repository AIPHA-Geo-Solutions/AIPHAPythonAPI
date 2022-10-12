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

  ao.list_running_services(client)
  res = ao.hello_world(client)
  ao.wait_for_completion(client, [res['pid']])

