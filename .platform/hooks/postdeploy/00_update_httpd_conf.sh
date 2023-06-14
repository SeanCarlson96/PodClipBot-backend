#!/bin/bash

# Create and write to websocket_proxy.conf
echo "LoadModule proxy_wstunnel_module modules/mod_proxy_wstunnel.so
ProxyPass /socket.io/ ws://127.0.0.1:8000/socket.io/
ProxyPassReverse /socket.io/ ws://127.0.0.1:8000/socket.io/" >> /etc/httpd/conf.d/websocket_proxy.conf
