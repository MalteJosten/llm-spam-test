import codecs
import json
import os
import re
import sys
import shutil
from pathlib import Path

# 1. read in mails based on ground truth
# 2. iterate mails
#   2.1 Extract mail body
#   2.2 Reformulate body with dictionary
#   2.4 Save new body in data/dictionary/post-bodies


DIRNAME = os.path.dirname(__file__)
sys.path.append(os.path.dirname(DIRNAME))
from my_utils import ts_time

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(DIRNAME)), "data")
RES_DIR = os.path.join(os.path.dirname(os.path.dirname(DIRNAME)), "results")
GT_FILE_NAMES = sys.argv[1:]

DICT = {}
new_bodies = {}
success_cnt = 0

try:
    shutil.rmtree(os.path.join(DATA_DIR, "dictionary", "pre-bodies"))
    shutil.rmtree(os.path.join(DATA_DIR, "dictionary", "post-bodies"))
except Exception:
    pass

Path(os.path.join(DATA_DIR, "dictionary", "pre-bodies")).mkdir(parents=True, exist_ok=True)
Path(os.path.join(DATA_DIR, "dictionary", "post-bodies")).mkdir(parents=True, exist_ok=True)

for gt_file_name in GT_FILE_NAMES:
    try:
        shutil.rmtree(os.path.join(DATA_DIR, "dictionary", "mails", gt_file_name))
    except Exception:
        pass

    Path(os.path.join(DATA_DIR, "dictionary", "mails", gt_file_name)).mkdir(parents=True, exist_ok=True)

print(f"---- [{ts_time()}] Starting to swap out spam-like words with the dictionary for mails contained in GT.json")
with open(os.path.join(DATA_DIR, "dictionary", "meteor_dict.json"), "r") as dict_file:
    DICT = json.loads(dict_file.read())["reformulations"]

with codecs.open(os.path.join(RES_DIR, "GT.json"), "r", encoding="utf-8", errors="ignore") as gt_file:
    ids = json.loads(gt_file.read())["ids"]

    for m_id in ids:
        with codecs.open(os.path.join(DATA_DIR, "mails", "spam-in", m_id), "r", encoding="utf-8", errors="ignore") as mail_file:
            content = mail_file.read()
            split_idx = re.search(r"\n\n", content)
            body = content[split_idx.end():]

            for spam, replacement in DICT.items():
                new_body = re.sub(spam, replacement, body, flags=re.IGNORECASE)

            with open(os.path.join(DATA_DIR, "dictionary", "pre-bodies", m_id), "w") as body_file:
                body_file.write(body)

            with open(os.path.join(DATA_DIR, "dictionary", "post-bodies", m_id), "w") as body_file:
                body_file.write(new_body)
                new_bodies[m_id] = new_body
                success_cnt += 1

print(f"  >> [{ts_time()}] Modified {success_cnt}/{len(ids)} mail bodies.")

for gt_file_name in GT_FILE_NAMES:
    gt_ids = []
    merge_cnt = 0
    with open(os.path.join(RES_DIR, f"gt_{gt_file_name}.json"), "r") as gt_file:
        gt_ids = json.loads(gt_file.read())["ids"]

    for m_id, new_body in new_bodies.items():
        if m_id in gt_ids:
            with codecs.open(os.path.join(DATA_DIR, "mails", "spam-mod", gt_file_name, m_id), "r", encoding="utf-8", errors="ignore") as old_mail_file:
                content = old_mail_file.read()
                split_idx = re.search(r"\n\n", content)
                headers = content[:split_idx.end()]

                new_mail = headers + "\n\n" + new_body

                with open(os.path.join(DATA_DIR, "dictionary", "mails", gt_file_name, m_id), "w") as new_mail_file:
                    new_mail_file.write(new_mail)
                    merge_cnt += 1

    print(f"  >> [{ts_time()}] Merged ({merge_cnt}) mail bodies with their headers in '{gt_file_name}' (having ({len(gt_ids)}) mails).")
