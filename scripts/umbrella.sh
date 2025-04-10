#!/bin/bash
##
# Umbrella is a shell script written to periodically through 
# crontab check the /var/log/auth.log file and block IP's that 
# are attempting to bruteforce using the UFW firewall
##

INFILE=/var/log/auth.log
RUN=1
TMPLOG=/tmp/_umbrella.log
DEBUG=$1
LOG=/tmp/umbrella.log
LOG_FILE=/var/log/umbrella/rain.log
LOCAL_LOG=~/local_umbrella.log

BlockBadIPS() {
    count=0
    while read -r LINE
    do
        (( count++ ))
        # Check for line that contain failed attempts using
        # 1: Invalid Users
        # 2: Failed Passwords
        # 3: Failed Key Negotiations
        echo -e "Blocking ${LINE}" >> $LOCAL_LOG
        ufw deny from $LINE to any
    done < "$LOG"
    echo "sentury-Umbrella: NOTICE - Status: Complete - Malicious_IP_Count: $count - Output: Successfully blocked $count IPAddresses that were deemed malicious" >> ${LOG_FILE}
    rm $LOG
}

ExtractBadIPS(){
    count=0;
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
                        echo $ITEM >> $TMPLOG
                        (( count++ ))
                    fi
                done
            done
        fi
    done < "$INFILE"
    echo "$(sort $TMPLOG | uniq)" >$LOG
    rm $TMPLOG
    echo "sentury-Umbrella: Info - Malicious_Attempt_Count: $count - Status: Running - Output: Umbrella is sorting through $count unauthorized authentication attempts that seem malicious" >> $LOG_FILE
        
}

if [[ $DEBUG == "-extract" ]]; then
    echo "Extracting BadIPs Only"
    ExtractBadIPS
elif [[ $DEBUG == "-block" ]]; then
    echo "Blocking BadIPs Only"
    BlockBadIPS
else
    ExtractBadIPS
    BlockBadIPS
fi
