import os
import sys

import grpc
from chirpstack_api import api

# Configuration.

# This must point to the API interface.
server = "localhost:8080"

# The DevEUI for which you want to enqueue the downlink.
dev_eui = "6a84ea000ba30400"

# The API token (retrieved using the web-interface).
api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjaGlycHN0YWNrIiwiaXNzIjoiY2hpcnBzdGFjayIsInN1YiI6IjcxYmNlYTZkLTBmMTMtNGM1MS05NjJhLTM5ZmRiNTYwZmMxMCIsInR5cCI6ImtleSJ9.jyDBs_S6J64vNwJvS8degchPu5_ynoP0GLxgGFGiw4Q"

if __name__ == "__main__":
  # Connect without using TLS.
  channel = grpc.insecure_channel(server)

  # Device-queue API client.
  client = api.DeviceServiceStub(channel)

  # Define the API key meta-data.
  auth_token = [("authorization", "Bearer %s" % api_token)]
  for n in range(0,5):
    # Construct request.
    req = api.EnqueueDeviceQueueItemRequest()
    req.queue_item.confirmed = False
    req.queue_item.data = bytes([0x01, 0x02, 0x03])
    req.queue_item.dev_eui = dev_eui
    req.queue_item.f_port = 10

    resp = client.Enqueue(req, metadata=auth_token)

    # Print the downlink id
    print(resp.id)
