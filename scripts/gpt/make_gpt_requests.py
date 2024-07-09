import codecs
import json
import os
import re
import sys
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

DIRNAME = os.path.dirname(__file__)
sys.path.append(os.path.dirname(DIRNAME))
from my_utils import ts_time

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(DIRNAME)), "data")
RES_DIR = os.path.join(os.path.dirname(os.path.dirname(DIRNAME)), "results")

load_dotenv()
API_KEY = os.getenv("KEY")
CLIENT = OpenAI(api_key=API_KEY)
GT_FILE = os.path.join(RES_DIR, "gt_minimal.json")
SPAM_SRC = os.path.join(DATA_DIR, "mails", "spam-in")
MODEL = sys.argv[1]
START_TIME = datetime.now()
MAIL_IDS = []
MAIL_COUNT = 0


def load_ids():
    global MAIL_IDS, MAIL_COUNT

    with open(GT_FILE, "r") as id_file:
        MAIL_IDS = json.loads(id_file.read())["ids"]

    MAIL_COUNT = len(MAIL_IDS)


def messages(body):
    return [
        {"role": "system", "content": f"Keep in mind the following text I wrote: \n\n{body}"},
        {"role": "system", "content": "Give your answer as a JSON object, only using the fields defined by the print_result function. I only need the response, no additional text. Don't generate a subject line. Instead of using placeholders, just leave out the placeholder brackets. You're allowed to use line breaks in your answer. Preserve all links."},
        {"role": "user", "content": "Please rephrase the previous content to be less aggressive and replace spam-like words and formulations."}
    ]


def create_and_send_request(body):
    result = CLIENT.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=messages(body),
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "print_result",
                    "description": "Print a reformulated text.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "is_success": {
                                "type": "boolean",
                                "description": "A boolean value indicating whether the text could successfully be reformulated (true) or whether reformulating the text was not possible due to your rules (false)."
                            },
                            "failed-description": {
                                "type": "string",
                                "description": "Detailed description on why the text could not be reformulated."
                            },
                            "failed-keyword": {
                                "type": "string",
                                "description": "One keyword summarizing the main reason why the text could not be reformulated"
                            },
                            "body": {
                                "type": "string",
                                "description": "If is_success is true, this field is filled with the reformulated text. Otherwise, this field is empty."
                            }
                        },
                        "required": ["is_success", "failed-description", "failed-keyword", "body"]
                    }
                }
            }
        ],
        tool_choice="required"
    )

    return json.loads(result.choices[0].message.tool_calls[0].function.arguments)


def delete_intermediate_results():
    rem_file_cnt = 0
    for file in os.listdir(os.path.join(DATA_DIR, "gpt", "gpt-results")):
        if os.path.basename(file).startswith(f"temp-res_{MODEL}-"):
            rem_file_cnt += 1
            os.remove(file)

    print(f"  >> [{ts_time()}] Removed ({rem_file_cnt}) old temporary save files for GPT results.")


def save_intermediate_results(results, part_no):
    file_path = os.path.join(DATA_DIR, "gpt", "gpt-results", f"temp-res_{MODEL}-{part_no}.json")
    with open(file_path, mode="w") as res_file:
        res_file.write(json.dumps({"results": results}, indent=4))

    print(f"  >> [{ts_time()}] Wrote intermediate results (part {part_no}) to {file_path}.")


def merge_intermediate_results():
    file_path = os.path.join(DATA_DIR, "gpt", "gpt-results", f"res_{MODEL}.json")
    results = {}
    part_cnt = 0

    for file in os.listdir(os.path.join(DATA_DIR, "gpt", "gpt-results")):
        if os.path.basename(file).startswith(f"temp-res_{MODEL}-"):
            with open(os.path.join(DATA_DIR, "gpt", "gpt-results", file), "r") as res_file:
                int_res = json.loads(res_file.read())["results"]
                results.update(int_res)
                part_cnt += 1

    with open(file_path, mode="w") as res_file:
        res_file.write(json.dumps({"results": results}, indent=4))

    print(f"  >> [{ts_time()}] Merged ({part_cnt}) intermediate results for to {file_path}.")


def iterate_mails():
    mail_counter = 0
    success_counter = 0
    fail_counter = 0
    part_no = 1
    results = {}

    print(f"---- [{ts_time()}] Starting to create/send requests for {GT_FILE}")

    for file in os.listdir(SPAM_SRC):
        file_name = os.path.basename(file)

        if file_name in MAIL_IDS:

            mail_counter += 1

            with codecs.open(os.path.join(SPAM_SRC, file_name), "r", encoding="utf-8", errors="ignore") as spam_file:
                try:
                    print(f"   o [{ts_time()}] {mail_counter}/{MAIL_COUNT} {file_name}")

                    content = spam_file.read()
                    spam_split_idx = re.search(r"\n\n", content)
                    spam_body = content[spam_split_idx.end():]

                    result = create_and_send_request(spam_body)
                    results[file_name[:-4]] = result

                    success_counter += 1

                    print(f"    > done ({success_counter}/{mail_counter})")

                    if (success_counter % 100 == 0):
                        save_intermediate_results(results, part_no)
                        part_no += 1
                        results = {}
                except Exception:
                    fail_counter += 1
                    print(f"    > failed ({success_counter}/{mail_counter})")
                    continue

    if results:
        save_intermediate_results(results, part_no)

    processing_time = (datetime.now() - START_TIME).total_seconds()
    print(f"  >> [{ts_time()}] Successfully transformed {success_counter} of {mail_counter} ({fail_counter} fails) spam mails. (~ {round(processing_time / mail_counter, 1)}s per mail)")

    merge_intermediate_results()


load_ids()
delete_intermediate_results()
iterate_mails()
