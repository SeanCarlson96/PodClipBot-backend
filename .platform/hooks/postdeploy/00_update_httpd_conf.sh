#!/bin/bash

echo -e '\nIncludeOptional /opt/elasticbeanstalk/support/conf.d/*.conf' >> /etc/httpd/conf/httpd.conf
systemctl restart httpd
