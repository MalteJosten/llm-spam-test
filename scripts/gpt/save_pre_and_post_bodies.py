import codecs
import json
import os
import re
import sys
from pathlib import Path

DIRNAME = os.path.dirname(__file__)
sys.path.append(os.path.dirname(DIRNAME))
from my_utils import ts_time

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(DIRNAME)), "data")
RES_DIR = os.path.join(os.path.dirname(os.path.dirname(DIRNAME)), "results")

GT_FILE = sys.argv[1]
GT_FILE = os.path.join(RES_DIR, GT_FILE)
GPT_FILE = sys.argv[2]
GPT_FILE = os.path.join(DATA_DIR, "gpt", "gpt-results", GPT_FILE)
MAIL_DIR = os.path.join(DATA_DIR, "mails", "spam-in")
PRE_DIR = os.path.join(DATA_DIR, "gpt", "pre-bodies")
POST_DIR = os.path.join(DATA_DIR, "gpt", "post-bodies")


def check_dirs():
    Path(PRE_DIR).mkdir(parents=True, exist_ok=True)
    Path(POST_DIR).mkdir(parents=True, exist_ok=True)

    for file in os.listdir(PRE_DIR):
        os.remove(os.path.join(PRE_DIR, file))

    for file in os.listdir(POST_DIR):
        os.remove(os.path.join(POST_DIR, file))


def load_results():
    with open(GPT_FILE, mode="r") as res_file:
        results = json.loads(res_file.read())["results"]

        return results


def load_m_ids():
    with open(GT_FILE, mode="r") as gt_file:
        ids = json.loads(gt_file.read())["ids"]
        return ids


def iterate_pre_mails(ids):
    for m_id in ids:
        with codecs.open(os.path.join(MAIL_DIR, m_id), "r", encoding="utf-8", errors="ignore") as original_file:
            content = original_file.read()
            spam_split_idx = re.search(r"\n\n", content)
            spam_body = content[spam_split_idx.end():]

            with open(os.path.join(PRE_DIR, m_id), "w") as spam_file:
                spam_file.write(spam_body)

    print(f"  >> [{ts_time()}] Extracted pre bodies to {PRE_DIR}.")


def iterate_post_mails(results):
    for m_id, answer in results.items():
        try:
            if answer["is_success"]:
                with open(os.path.join(POST_DIR, m_id + ".eml"), "w") as spam_file:
                    spam_file.write(answer["body"])
        except KeyError:
            continue

    print(f"  >> [{ts_time()}] Extracted post bodies to {POST_DIR}.")


print(f"---- [{ts_time()}] Saving pre- and post-bodies.")
results = load_results()
print(f"  >> [{ts_time()}] Loaded results.")
m_ids = load_m_ids()
print(f"  >> [{ts_time()}] Loaded IDs.")

check_dirs()
iterate_pre_mails(m_ids)
iterate_post_mails(results)
print(f"  >> [{ts_time()}] Done.")
