#!/bin/bash

# Get the wlan0 (wifi) ip address and 
# set it as an environment variable
API_HOST_WLAN0=$(ip route list | awk '{print $9}')
export API_HOST_WLAN0=$API_HOST_WLAN0


echo $(ls api)
# Start the server
python api/app.py