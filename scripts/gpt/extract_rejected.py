import json
import os
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
NAME = GT_FILE.split("_")[1].split(".")[0]
MAIL_DIR = os.path.join(DATA_DIR, "mails", "spam-in")
SAVE_DIR = os.path.join(DATA_DIR, "gpt", "gpt-results")


Path(SAVE_DIR).mkdir(parents=True, exist_ok=True)


def save_rejected(rejected):
    with open(os.path.join(SAVE_DIR, f"rejected_{NAME}.json"), mode="w") as reject_file:
        reject_file.write(json.dumps({"rejections": rejected}, indent=4))


def load_results():
    with open(GPT_FILE, mode="r") as res_file:
        results = json.loads(res_file.read())["results"]

        return results


def load_m_ids():
    with open(GT_FILE, mode="r") as gt_file:
        ids = json.loads(gt_file.read())["ids"]
        return ids


def iterate_mails(ids, results):
    rejected = {}

    for m_id in ids:
        if m_id[:-4] in list(results.keys()):
            answer = results[m_id[:-4]]

            try:
                if not answer["is_success"]:
                    rejected[m_id] = answer
            except KeyError:
                with open(os.path.join(SAVE_DIR, f"{NAME}_wf.txt"), mode="a") as wrong_format_file:
                    wrong_format_file.write(m_id + "\n")

    if len(rejected) > 0:
        save_rejected(rejected)
        print(f"  >> [{ts_time()}] Saved GPT rejections to {os.path.join(SAVE_DIR, 'rejected_' + NAME + '.json')}")


def iterate_and_save_all_rejections(results):
    rejected = {}

    for m_id, answer in results.items():
        try:
            if not answer["is_success"]:
                rejected[m_id] = answer
        except KeyError:
            continue

    with open(os.path.join(SAVE_DIR, "rejected_all.json"), mode="w") as reject_file:
        reject_file.write(json.dumps({"rejections": rejected}, indent=2))


print(f"---- [{ts_time()}] Extracting rejections.")
results = load_results()
print(f"  >> [{ts_time()}] Loaded results.")
m_ids = load_m_ids()
print(f"  >> [{ts_time()}] Loaded IDs.")

#iterate_mails(m_ids, results)
iterate_and_save_all_rejections(results)
print(f"  >> [{ts_time()}] Done.")
