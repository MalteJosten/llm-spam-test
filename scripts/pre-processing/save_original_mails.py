import os
import shutil
import sys
from pathlib import Path

DIRNAME = os.path.dirname(__file__)
sys.path.append(os.path.dirname(DIRNAME))
from my_utils import ts_time

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(DIRNAME)), "data")

IN_DIR = os.path.join(DATA_DIR, "mails/spam-in")
OUT_DIR = os.path.join(DATA_DIR, "mails/spam-mod/original")

print(f"---- [{ts_time()}] Copying mails to {OUT_DIR}")

try:
    shutil.rmtree(OUT_DIR)
except Exception:
    pass

Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

for file_name in os.listdir(IN_DIR):
    shutil.copy(os.path.join(IN_DIR, file_name), os.path.join(OUT_DIR, file_name))

print(f"  >> [{ts_time()}] Done. Saved mails to {OUT_DIR}")
