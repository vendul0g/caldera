#!/bin/bash

############################################
###          Script: Start Agent         ###
############################################

set -e  # Exit immediately if a command exits with a non-zero status
set -x  # Enable debugging

cd /tmp

# Wait for caldera to start
sleep 30

# Execute the agent
server="http://caldera:8888"
echo "Attempting to download agent from $server/file/download"

response=$(curl -svkOJ -X POST -H "file: sandcat.go" -H "platform: linux" $server/file/download 2>&1)
echo "Curl response:"
echo "$response"

agent=$(echo "$response" | grep -i "Content-Disposition" | grep -io "filename=.*" | cut -d'=' -f2 | tr -d '"\r') 
echo "Downloaded agent: $agent"

if [ -z "$agent" ]; then
    echo "Failed to download agent." >&2
    exit 1
fi

chmod +x "$agent" || { echo "Failed to chmod $agent"; exit 1; }
nohup ./"$agent" -server "$server" &

echo "Agent started"

# Remove the default nginx configuration
rm /etc/nginx/sites-enabled/default

nginx -s reload

# Start the web server
nginx -g 'daemon off;'
