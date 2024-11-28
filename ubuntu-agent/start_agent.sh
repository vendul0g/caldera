#!/bin/bash

############################################
###          Script: Start Agent         ###
############################################

set -x  # Enable debugging

cd /tmp

# Verificar permisos de escritura y espacio en disco
touch /tmp/testfile && echo "Permisos de escritura en /tmp: Correctos" || { echo "Permisos de escritura en /tmp: Incorrectos"; exit 1; }
df -h /tmp

# Wait for caldera to start
sleep 60

# Execute the agent
server="http://caldera:8888"
echo "Attempting to download agent from $server/file/download"

if curl -svk -X POST -H "file: sandcat.go" -H "platform: linux" $server/file/download -o sandcat.go-linux; then
    echo "Agent descargado exitosamente: sandcat.go-linux"
else
    echo "Error al descargar el agente." >&2
    exit 1
fi

chmod +x sandcat.go-linux || { echo "Failed to chmod sandcat.go-linux"; exit 1; }
nohup ./sandcat.go-linux -server "$server" &

echo "Agent started"

# Remove the default nginx configuration
rm /etc/nginx/sites-enabled/default

# Start the web server
nginx -g 'daemon off;'
