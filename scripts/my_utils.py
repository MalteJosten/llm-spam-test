import json
from datetime import datetime


def ts():
    return f"{datetime.today().strftime('%Y-%m-%d %-H:%M:%S')}"


def ts_time():
    return f"{datetime.today().strftime('%-H:%M:%S')}"


def ts_file():
    return f"{datetime.today().strftime('%Y-%m-%d_%-H:%M:%S')}"


def fetch_bodies(path):
    pre_bodies = {}
    post_bodies = {}

    with open(path, "r") as gt_file:
        body_collection = json.loads(gt_file.read())["bodies"]

        for m_id, bodies in body_collection.items():
            pre_bodies[m_id] = bodies["data_original"]
            post_bodies[m_id] = bodies["data_modified"]

        return pre_bodies, post_bodies
