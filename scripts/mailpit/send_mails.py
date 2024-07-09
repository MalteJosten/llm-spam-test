import os
import smtplib
import sys
from datetime import datetime
from email import policy
from email.parser import BytesParser


DIRNAME = os.path.dirname(__file__)
sys.path.append(os.path.dirname(DIRNAME))
from my_utils import ts_time

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(DIRNAME)), "data")

MAILPIT_URI = sys.argv[1]
MAIL_DIR = os.path.join(DATA_DIR, sys.argv[2])
SESSION = smtplib.SMTP(MAILPIT_URI, 1025)


def parse_mail(file_path):
    with open(os.path.join(MAIL_DIR, file_path), 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
        msg["X-Tags"] = str(os.path.basename(file_path))
        if not msg["Date"]:
            msg["Date"] = datetime.today().strftime("%a, %-d %b %Y %-H:%M:%S %z+0100")

        return msg


def send_email(msg, id):
    try:
        SESSION.send_message(msg)
        return True
    except Exception:
        return False


def iterate_mails():
    mail_count = 0
    success_cnt = 0
    failed_cnt = 0

    for mail in os.listdir(MAIL_DIR):
        mail_count += 1
        success = send_email(parse_mail(mail), os.path.basename(mail)[:-4])

        if success:
            success_cnt += 1
        else:
            failed_cnt += 1

    SESSION.quit()

    print(f"  >> [{ts_time()}] Successfully sent {success_cnt} of {mail_count} ({failed_cnt} failed).")


print(f"---- [{ts_time()}] Starting to send mails from {MAIL_DIR}.")
iterate_mails()
