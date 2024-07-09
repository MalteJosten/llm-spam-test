import os
import shutil
import sys
from pathlib import Path

DIRNAME = os.path.dirname(__file__)
sys.path.append(os.path.dirname(DIRNAME))
from my_utils import ts_time

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(DIRNAME)), "data")

IN_DIR = os.path.join(DATA_DIR, "mails/spam-in")
OUT_DIR = os.path.join(DATA_DIR, "mails/spam-mod/minimal")

print(f"---- [{ts_time()}] Removing SMTP headers of mails in {IN_DIR}")

try:
    shutil.rmtree(OUT_DIR)
except Exception:
    pass

Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

for file in os.listdir(IN_DIR):
    new_content = ""
    is_header = True

    try:
        with open(os.path.join(IN_DIR, file), mode="r") as src_file:
            for line in src_file:
                if is_header:
                    if line == "\n":
                        is_header = False

                    if not (line.startswith("From:") or line.startswith("To:") or line.startswith("Bcc") or line.startswith("Subject") or line.startswith("\n")):
                        continue

                new_content = new_content + line

        with open(os.path.join(OUT_DIR, file), mode="w") as dest_file:
            dest_file.write(new_content)
    except UnicodeDecodeError:
        continue

print(f"  >> [{ts_time()}] Done. Saved mails to {OUT_DIR}")
