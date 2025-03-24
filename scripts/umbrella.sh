#!/bin/bash
##
# Umbrella is a shell script written to periodically through 
# crontab check the /var/log/auth.log file and block IP's that 
# are attempting to bruteforce using the UFW firewall
##

INFILE=/var/log/auth.log
RUN=1
UMBRELLA_LOG=~/umbrella.log
DEBUG=$1

while read -r LINE
do
    # Check for line that contain failed attempts using
    # 1: Invalid Users
    # 2: Failed Passwords
    # 3: Failed Key Negotiations
    if [[ $LINE == *"Failed password for"* || $LINE == *"Invalid user"* || $LINE == *"Unable to negotiate"* ]]; then
        IFS=$': '
        for LINESTR in $LINE
        do
            IFS=$' '
            for ITEM in $LINESTR
            do
                if [[ $ITEM == *"."* ]]; then
                    if [[ $DEBUG == "-debug" ]]; then
                        LOGITEM=$"Blocking ${ITEM}" 
                    else
                        LOGITEM=$(sudo ufw deny from $ITEM to any)
                    fi
                    echo $LOGITEM >> $UMBRELLA_LOG
                fi
            done
        done
        
    fi
done < "$INFILE"