import os
import uuid
import sys
import shutil
from pathlib import Path

DIRNAME = os.path.dirname(__file__)
sys.path.append(os.path.dirname(DIRNAME))
from my_utils import ts_time

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(DIRNAME)), "data")

RAW_DIRS = [os.path.join(DATA_DIR, file_path) for file_path in sys.argv[1:]]
DEST_DIR = os.path.join(DATA_DIR, "mails/spam-in")

print(f"---- [{ts_time()}] Starting to convert files")

try:
    shutil.rmtree(DEST_DIR)
except Exception:
    pass

Path(DEST_DIR).mkdir(parents=True, exist_ok=True)

for directory in RAW_DIRS:
    for file in os.scandir(directory):
        if file.is_file():
            file_name = os.path.basename(file)
            new_name = f"{uuid.uuid4()}.eml"
            shutil.copy(os.path.join(directory, file_name), os.path.join(DEST_DIR, new_name))

    print(f"  >> [{ts_time()}] Converted all files to .eml in directory {os.path.basename(directory)}") 
