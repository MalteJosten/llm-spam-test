#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
RAW_DIRS=("mails/raw/20021010_spam" "mails/raw/20030228_spam" "mails/raw/20050311_spam_2")

python "${SCRIPT_DIR}/pre-processing/make_input_usable.py" "${RAW_DIRS[@]}"
wait $!

python "${SCRIPT_DIR}/pre-processing/anonymize_mails.py"
wait $!

python "${SCRIPT_DIR}/pre-processing/save_original_mails.py"
wait $!

python "${SCRIPT_DIR}/pre-processing/minimize_smtp_headers.py"
wait $!
