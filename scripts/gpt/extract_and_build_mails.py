import codecs
import json
import os
import re
import sys
import shutil

DIRNAME = os.path.dirname(__file__)
sys.path.append(os.path.dirname(DIRNAME))
from my_utils import ts_time

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(DIRNAME)), "data")
RES_DIR = os.path.join(os.path.dirname(os.path.dirname(DIRNAME)), "results")

GT_FILE = sys.argv[1]
GT_FILE = os.path.join(RES_DIR, GT_FILE)
GPT_FILE = sys.argv[2]
GPT_FILE = os.path.join(DATA_DIR, "gpt", "gpt-results", GPT_FILE)
NAME = GT_FILE.split("_")[1].split(".")[0]
MAIL_DIR = os.path.join(DATA_DIR, "mails", "spam-mod", NAME)
DEST_DIR = os.path.join(DATA_DIR, "gpt", "mails", NAME)


def check_dir():
    if os.path.isdir(DEST_DIR):
        shutil.rmtree(DEST_DIR)

    os.mkdir(DEST_DIR)


def assemble_mail(r_id, body):
    for file in os.listdir(MAIL_DIR):
        if os.path.basename(file) == r_id:
            with codecs.open(os.path.join(MAIL_DIR, file), "r", encoding="utf-8", errors="ignore") as spam_file:
                content = spam_file.read()
                spam_split_idx = re.search(r"\n\n", content)
                spam_header = content[:spam_split_idx.start()]

                assembled_mail = f"{spam_header}\n\n{body}"

                return assembled_mail


def save_mail(r_id, mail):
    with open(os.path.join(DEST_DIR, f"{r_id}"), mode="w") as dest_file:
        dest_file.write(mail)


def save_rejected(rejected):
    with open(os.path.join(DATA_DIR, "gpt", "gpt-results", f"rejected_{NAME}.json"), mode="w") as reject_file:
        reject_file.write(json.dumps({"rejections": rejected}, indent=4))


def load_results():
    with open(GPT_FILE, mode="r") as res_file:
        results = json.loads(res_file.read())["results"]

        return results


def load_m_ids():
    with open(GT_FILE, mode="r") as gt_file:
        ids = json.loads(gt_file.read())["ids"]
        return ids


def iterate_results(ids, results):
    rejected = {}

    for m_id in ids:
        if m_id[:-4] in list(results.keys()):
            answer = results[m_id[:-4]]

            try:
                if answer["is_success"]:
                    mail = assemble_mail(m_id, answer["body"])
                    save_mail(m_id, mail)
                else:
                    rejected[m_id] = answer
            except KeyError:
                with open(os.path.join(DATA_DIR, "gpt", "gpt-results", f"{NAME}_wf.txt"), mode="a") as wrong_format_file:
                    wrong_format_file.write(m_id + "\n")

    print(f"  >> [{ts_time()}] Merged and saved mails to {DEST_DIR}.")

    if len(rejected) > 0:
        save_rejected(rejected)
        print(f"  >> [{ts_time()}] Saved GPT rejections to {os.path.join(DATA_DIR, 'gpt', 'gpt-results', 'rejected_' + NAME + '.json')}")


print(f"---- [{ts_time()}] Starting to extract and build GPT mails.")
results = load_results()
print(f"  >> [{ts_time()}] Loaded results.")
m_ids = load_m_ids()
print(f"  >> [{ts_time()}] Loaded IDs.")

check_dir()
iterate_results(m_ids, results)
print(f"  >> [{ts_time()}] Done.")
