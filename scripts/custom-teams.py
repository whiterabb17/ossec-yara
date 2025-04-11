#!/usr/bin/env python3
# Created by Shuffle, AS. <frikky@shuffler.io>.
# Based on the Slack integration using Webhooks

import json
import sys
import time
import os

try:
    import requests
    from requests.auth import HTTPBasicAuth
except Exception:
    print("No module 'requests' found. Install: pip install requests")
    sys.exit(1)

# ADD THIS TO ossec.conf configuration:
#  <integration>
#      <name>custom-shuffle</name>
#      <hook_url>http://<IP>:3001/api/v1/hooks/<HOOK_ID></hook_url>
#      <level>3</level>
#      <alert_format>json</alert_format>
#  </integration>

# Global vars
debug_enabled = False
pwd = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
json_alert = {}
now = time.strftime("%a %b %d %H:%M:%S %Z %Y")

# Set paths
log_file = f"{pwd}/logs/integrations.log"

def debug(msg):
    if debug_enabled:
        msg = f"{now}: {msg}\n"
        print(msg)
        with open(log_file, "a") as f:
            f.write(msg)

def filter_msg(alert):
    # Skips container kills to stop self-recursion
    skip = [
        "87924", "87900", "87901", "87902", "87903", "87904",
        "86001", "86002", "86003", "87932", "80710", "87929",
        "87928", "5710"
    ]
    return alert["rule"]["id"] not in skip

def generate_msg(alert):
    level = alert['rule']['level']
    if level <= 4:
        color = "38F202"
    elif 5 <= level <= 7:
        color = "F2EB02"
    else:
        color = "F22A02"

    msg = {
        '@type': "MessageCard",
        'themeColor': color,
        'summary': "Sentury Alert: " + alert['rule'].get('description', "N/A"),
        'sections': []
    }

    facts = []

    if 'agent' in alert:
        facts.append({
            'name': 'Agent',
            'value': f"({alert['agent']['id']}) - {alert['agent']['name']}"
        })

    if 'agentless' in alert:
        facts.append({
            'name': 'Agentless host',
            'value': alert['agentless']['host']
        })

    facts.append({
        'name': 'Location',
        'value': alert['location']
    })

    facts.append({
        'name': 'Rule ID',
        'value': f"{alert['rule']['id']} _(Level {level})_"
    })

    if 'Secure Token Service (STS) logon events in Azure Active Directory' in alert['rule']['description']:
        facts.append({
            'name': 'UserId',
            'value': alert['data']['office365']['UserId']
        })

    if alert['data']['office365'].get('Operation') == 'UserLoginFailed':
        facts.append({
            'name': 'Location',
            'value': alert['GeoLocation']['country_name']
        })

    facts.append({
        'name': 'Log',
        'value': alert.get('full_log')
    })

    msg['sections'].append({
        'activityTitle': "Sentury Alert"
    })

    if 'description' in alert['rule']:
        msg['sections'].append({
            'title': alert['rule']['description']
        })

    msg['sections'].append({
        'facts': facts,
        'markdown': 'true'
    })

    return json.dumps(msg)

def send_msg(msg, url):
    headers = {
        'content-type': 'application/json',
        'Accept-Charset': 'UTF-8'
    }
    res = requests.post(url, data=msg, headers=headers)
    debug(res)

def main(args):
    debug("# Starting")
    alert_file_location = args[1]
    webhook = args[3]

    debug("# Webhook")
    debug(webhook)
    debug("# File location")
    debug(alert_file_location)

    # Load alert. Parse JSON object.
    with open(alert_file_location) as alert_file:
        json_alert = json.load(alert_file)

    debug("# Processing alert")
    debug(json_alert)

    if not filter_msg(json_alert):
        debug("# Alert filtered out")
        return

    debug("# Generating message")
    msg = generate_msg(json_alert)
    if isinstance(msg, str) and len(msg) == 0:
        return

    debug("# Sending message")
    send_msg(msg, webhook)

if __name__ == "__main__":
    try:
        bad_arguments = False

        if len(sys.argv) >= 4:
            msg = f"{now} {sys.argv[1]} {sys.argv[2]} {sys.argv[3]} {sys.argv[4] if len(sys.argv) > 4 else ''}"
            debug_enabled = (len(sys.argv) > 4 and sys.argv[4] == 'debug')
        else:
            msg = f"{now} Wrong arguments"
            bad_arguments = True

        with open(log_file, 'a') as f:
            f.write(msg + '\n')

        if bad_arguments:
            debug("# Exiting: Bad arguments.")
            sys.exit(1)

        main(sys.argv)
    except Exception as e:
        debug(str(e))
        raise
