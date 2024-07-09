import os
import sys

DIRNAME = os.path.dirname(__file__)
sys.path.append(os.path.dirname(DIRNAME))
from my_utils import ts_time

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(DIRNAME)), "data")

IN_DIR = os.path.join(DATA_DIR, "mails/spam-in")
OUT_DIR = os.path.join(DATA_DIR, "mails/spam-in")

print(f"---- [{ts_time()}] Anonymizing mails in {IN_DIR}")

for file in os.listdir(IN_DIR):
    new_content = ""
    is_header = True

    try:
        with open(os.path.join(IN_DIR, file), mode="r") as mail_file:
            for line in mail_file:
                if is_header:
                    if line == "\n":
                        is_header = False

                    if line.startswith("From:"):
                        line = "From: from@example.com\n"
                    elif line.startswith("To:"):
                        line = "To: to@example.com\n"
                    elif line.startswith("Bcc:"):
                        line = "Bcc: bcc@example.com\n"

                    new_content = new_content + line
                    continue

                new_content = new_content + line

        with open(os.path.join(OUT_DIR, file), mode="w") as mail_file:
            mail_file.write(new_content)
    except UnicodeDecodeError:
        continue

print(f"  >> [{ts_time()}] Done (saved to {OUT_DIR})")
