#!/bin/bash

{
echo "Adding new line and IncludeOptional to httpd.conf"
echo '#----------' >> /etc/httpd/conf/httpd.conf
echo 'IncludeOptional /opt/elasticbeanstalk/support/conf.d/*.conf' >> /etc/httpd/conf/httpd.conf
echo "Finished adding lines. Here's the end of the httpd.conf file:"
tail -n 5 /etc/httpd/conf/httpd.conf

echo "Restarting httpd"
systemctl restart httpd
echo "Finished restarting httpd"
} >> /tmp/debug.log 2>&1
