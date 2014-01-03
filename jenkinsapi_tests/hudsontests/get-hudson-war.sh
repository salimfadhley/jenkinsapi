#!/bin/sh
HUDSON_WAR_URL="http://eclipse.org/downloads/download.php?file=/hudson/war/hudson-3.1.0.war&r=1"
wget $HUDSON_WAR_URL --output-document hudson.war
