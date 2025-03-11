import os
import subprocess
import json
import re
import requests

API_KEY = '<API_KEY>'
OPENAI_MODEL='gpt-4o-mini' #for example gpt-4-turbo

# Determine OS architecture and set log file path
if os.environ['PROCESSOR_ARCHITECTURE'].endswith('86'):
    log_file_path = os.path.join(os.environ['ProgramFiles'], 'ossec-agent', 'active-response', 'active-responses.log')
else:
    log_file_path = os.path.join(os.environ['ProgramFiles(x86)'], 'ossec-agent', 'active-response', 'active-responses.log')

def log_message(message):
    with open(log_file_path, 'a') as log_file:
        log_file.write(message + '\n')

def read_input():
    return input()

def get_syscheck_file_path(json_file_path):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
        return data['parameters']['alert']['syscheck']['path']

def run_yara_scan(yara_exe_path, yara_rules_path, syscheck_file_path):
    try:
        result = subprocess.run([yara_exe_path, '-m', yara_rules_path, syscheck_file_path], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        log_message(f"Error running Yara scan: {str(e)}")
        return None

def extract_description(yara_output):
    match = re.search(r'description="([^"]+)"', yara_output)
    if match:
        return match.group(1)
    else:
        return None

def query_chatgpt(description):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': OPENAI_MODEL,
        'messages': [{'role': 'system', 'content': f'In one paragraph, tell me about the impact and how to mitigate {description}'}],
        'temperature': 1,
        'max_tokens': 256,
        'top_p': 1,
        'frequency_penalty': 0,
        'presence_penalty': 0
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    elif response.status_code == 401:  # Unauthorized (invalid API key)
        log_message("wazuh-YARA: ERROR - Invalid ChatGPT API key")
        return None
    else:
        log_message(f"Error querying ChatGPT: {response.status_code} {response.text}")
        return None

def main():
    json_file_path = r"C:\Program Files (x86)\ossec-agent\active-response\stdin.txt"
    yara_exe_path = r"C:\Program Files (x86)\ossec-agent\active-response\bin\yara\yara64.exe"
    yara_rules_path = r"C:\Program Files (x86)\ossec-agent\active-response\bin\yara\rules\yara_rules.yar"

    input_data = read_input()

    with open(json_file_path, 'w') as json_file:
        json_file.write(input_data)

    syscheck_file_path = get_syscheck_file_path(json_file_path)

    yara_output = run_yara_scan(yara_exe_path, yara_rules_path, syscheck_file_path)
    if yara_output is not None:
        description = extract_description(yara_output)

        if description:
            chatgpt_response = query_chatgpt(description)
            if chatgpt_response:
                combined_output = f"wazuh-YARA: INFO - Scan result: {yara_output} | chatgpt_response: {chatgpt_response}"
                log_message(combined_output)
            else:
                # Log the Yara scan result without the ChatGPT response
                log_message(f"wazuh-YARA: INFO - Scan result: {yara_output} | chatgpt_response: None")

            # Delete the scanned file if a description is found
            try:
                os.remove(syscheck_file_path)
                if not os.path.exists(syscheck_file_path):
                    log_message(f"wazuh-YARA: INFO - Successfully deleted {syscheck_file_path}")
                else:
                    log_message(f"wazuh-YARA: INFO - Unable to delete {syscheck_file_path}")
            except Exception as e:
                log_message(f"Error deleting file: {str(e)}")
        else:
            log_message("Failed to extract description from Yara output.")
    else:
        log_message("Yara scan returned no output.")

if __name__ == "__main__":
    main()