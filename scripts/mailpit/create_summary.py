import json
import os
import sys

DIRNAME = os.path.dirname(__file__)
sys.path.append(os.path.dirname(DIRNAME))
from my_utils import ts_time

RES_DIR = os.path.join(os.path.dirname(os.path.dirname(DIRNAME)), "results")
GTS = sys.argv[1:]
ids = []

for gt in GTS:
    with open(os.path.join(RES_DIR, gt), "r") as gt_file:
        gt_ids = json.loads(gt_file.read())["ids"]

        for gt_id in gt_ids:
            if gt_id in ids:
                continue

            ids.append(gt_id)

with open(os.path.join(RES_DIR, "GT.json"), "w") as gt_file:
    gt_file.write(json.dumps({"ids": ids}, indent=2))

print(f"---- [{ts_time()}] Saved Ground Truth file at {os.path.join(RES_DIR, 'GT.json')}.")
