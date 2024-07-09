#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
MAILPIT_URI="192.168.7.73"

# conslut GPT to modify bodies
python "${SCRIPT_DIR}/gpt/make_gpt_requests.py" "gpt-3.5-turbo-0125"
wait $!

# extract rejected GPT requests
python "${SCRIPT_DIR}/gpt/extract_rejected.py" "gt_original.json" "res_gpt-3.5-turbo-0125.json"
wait $!

python "${SCRIPT_DIR}/gpt/extract_rejected.py" "gt_minimal.json" "res_gpt-3.5-turbo-0125.json"
wait $!

# extract and save pre- and post-bodies
python "${SCRIPT_DIR}/gpt/save_pre_and_post_bodies.py" "GT.json" "res_gpt-3.5-turbo-0125.json"
wait $!

# extract answers and (re)build emails
python "${SCRIPT_DIR}/gpt/extract_and_build_mails.py" "gt_original.json" "res_gpt-3.5-turbo-0125.json"
wait $!

python "${SCRIPT_DIR}/gpt/extract_and_build_mails.py" "gt_minimal.json" "res_gpt-3.5-turbo-0125.json"
wait $!

# original data set
curl -s -X DELETE "${MAILPIT_URI}:8025/api/v1/messages" > /dev/null
echo "   o Cleared mailbox"

python "${SCRIPT_DIR}/mailpit/send_mod_mails.py" "${MAILPIT_URI}" "gpt/mails/original" 
wait $!

python "${SCRIPT_DIR}/mailpit/retrieve_mod_labels.py" "${MAILPIT_URI}" "gpt/mails/original" "gpt"
wait $!

# minimal data set
curl -s -X DELETE "${MAILPIT_URI}:8025/api/v1/messages" > /dev/null
echo "   o Cleared mailbox"

python "${SCRIPT_DIR}/mailpit/send_mod_mails.py" "${MAILPIT_URI}" "gpt/mails/minimal" 
wait $!

python "${SCRIPT_DIR}/mailpit/retrieve_mod_labels.py" "${MAILPIT_URI}" "gpt/mails/minimal" "gpt"
wait $!

# clear mailbox
curl -s -X DELETE "${MAILPIT_URI}:8025/api/v1/messages" > /dev/null
echo "   o Cleared mailbox"
