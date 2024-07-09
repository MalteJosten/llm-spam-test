#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
MAILPIT_URI="127.0.0.1"

curl -s -X DELETE "${MAILPIT_URI}:8025/api/v1/messages" > /dev/null
echo "   o Cleared mailbox"

python "${SCRIPT_DIR}/mailpit/send_mails.py" "${MAILPIT_URI}" "mails/spam-mod/original" 
wait $!

python "${SCRIPT_DIR}/mailpit/retrieve_original_labels.py" "${MAILPIT_URI}" "mails/spam-mod/original"
wait $!

curl -s -X DELETE "${MAILPIT_URI}:8025/api/v1/messages" > /dev/null
echo "   o Cleared mailbox"

python "${SCRIPT_DIR}/mailpit/send_mails.py" "${MAILPIT_URI}" "mails/spam-mod/minimal"
wait $!

python "${SCRIPT_DIR}/mailpit/retrieve_original_labels.py" "${MAILPIT_URI}" "mails/spam-mod/minimal"
wait $!

curl -s -X DELETE "${MAILPIT_URI}:8025/api/v1/messages" > /dev/null
echo "   o Cleared mailbox"

python "${SCRIPT_DIR}/mailpit/create_summary.py" "gt_original.json" "gt_minimal.json"
wait $!
echo "  >> Done."
