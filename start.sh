#!/bin/bash

source /opt/bin/activate

cd /opt/oad

service elasticsearch restart

sleep 20

supervisord -n -c conf/supervisor.conf
