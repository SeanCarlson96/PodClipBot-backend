#!/bin/bash

echo '# ----------' >> /etc/httpd/conf/httpd.conf
echo 'IncludeOptional /opt/elasticbeanstalk/support/conf.d/*.conf' >> /etc/httpd/conf/httpd.conf
systemctl restart httpd
