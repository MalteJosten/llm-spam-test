import csv
import json
import os
import requests
import sys

DIRNAME = os.path.dirname(__file__)
sys.path.append(os.path.dirname(DIRNAME))
from my_utils import ts_time, ts_file

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(DIRNAME)), "data")
SAVE_PATH = os.path.join(os.path.dirname(os.path.dirname(DIRNAME)), "results")
MAILPIT_URI = sys.argv[1]
MAILPIT_API = f"{MAILPIT_URI}:8025/api/v1"
MAIL_DIR = sys.argv[2]
MAIL_DIR = os.path.join(DATA_DIR, MAIL_DIR)
MAIL_COUNT = len([file for file in os.listdir(MAIL_DIR) if os.path.isfile(os.path.join(MAIL_DIR, file))])
RUN = sys.argv[3]


def get_mail_id(local_id):
    get_id_query = f"http://{MAILPIT_API}/search?query=tag%3A{local_id}"
    id_res = requests.get(get_id_query)
    id_res_json = id_res.json()

    try:
        return id_res_json["messages"][0]["ID"]
    except IndexError:
        return None


def get_label(id):
    is_spam_query = f"http://{MAILPIT_API}/message/{id}/sa-check"
    spam_res = requests.get(is_spam_query)
    spam_res_json = spam_res.json()
    is_spam = spam_res_json["IsSpam"]
    spam_label = "1" if is_spam else "0"

    return spam_label


def test_label(msg_id):
    mail_db_id = get_mail_id(msg_id)

    if mail_db_id:
        spam_label = get_label(mail_db_id)
        return spam_label


def create_summary(labels):
    sent_count = len(labels)
    sent_ratio = sent_count / MAIL_COUNT

    classifications = {"0": labels.count("0"), "1": labels.count("1")}

    summary = {
        "mail_count": MAIL_COUNT,
        "sent_count": sent_count,
        "sent_ratio": sent_ratio,
        "classifications": classifications,
        "success_rate": labels.count("0") / sent_count
    }

    return summary


def save_summary(summary, save_name):
    save_file_path = os.path.join(SAVE_PATH, f"sum_mod_{save_name}.json")
    with open(save_file_path, "w") as summary_json:
        json.dump(summary, summary_json, indent=2)

    print(f"  >> [{ts_time()}] Saved results at {save_file_path}")


def start_test():
    classifications = []
    save_name = f"{RUN}_{os.path.basename(MAIL_DIR)}"
    save_file_path = os.path.join(SAVE_PATH, f"{save_name}.csv")

    with open(save_file_path, "w") as labels:
        res_writer = csv.writer(labels, delimiter=',')
        res_writer.writerow(["ID", "label"])

        for file in os.listdir(MAIL_DIR):
            msg_id = os.path.basename(file)
            label = test_label(msg_id)

            if label is not None:
                classifications.append(label)

            res_writer = csv.writer(labels, delimiter=',')
            res_writer.writerow([os.path.basename(file), label if label is not None else "-"])

        print(f"  >> [{ts_time()}] Saved spam labels at {save_file_path}")

        summary = create_summary(classifications)
        save_summary(summary, save_name)


print(f"---- [{ts_time()}] Starting to test labels of mails in {MAIL_DIR}")
start_test()
