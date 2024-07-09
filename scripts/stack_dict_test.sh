#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
MAILPIT_URI="192.168.7.73"

# Modify mail bodies
python "${SCRIPT_DIR}/dictionary/modify_mails.py" "original" "minimal"
wait $!

# original data set
curl -s -X DELETE "${MAILPIT_URI}:8025/api/v1/messages" > /dev/null
echo "   o Cleared mailbox"

python "${SCRIPT_DIR}/mailpit/send_mod_mails.py" "${MAILPIT_URI}" "dictionary/mails/original" 
wait $!

python "${SCRIPT_DIR}/mailpit/retrieve_mod_labels.py" "${MAILPIT_URI}" "dictionary/mails/original" "dict"
wait $!

# minimal data set
curl -s -X DELETE "${MAILPIT_URI}:8025/api/v1/messages" > /dev/null
echo "   o Cleared mailbox"

python "${SCRIPT_DIR}/mailpit/send_mod_mails.py" "${MAILPIT_URI}" "dictionary/mails/minimal" 
wait $!

python "${SCRIPT_DIR}/mailpit/retrieve_mod_labels.py" "${MAILPIT_URI}" "dictionary/mails/minimal" "dict"
wait $!

# clear mailbox
curl -s -X DELETE "${MAILPIT_URI}:8025/api/v1/messages" > /dev/null
echo "   o Cleared mailbox"
