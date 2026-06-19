import os

MANDATORY_KEYS = [
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
]


def parse_config(file_name: str) -> tuple[bool, dict]:

    if not os.path.isfile(file_name):
        return (False, {})
    conf_result = {}
    with open(file_name, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                continue
            equal_count = line.count("=")
            if equal_count != 1:
                return (False, {})
            key, value = line.split("=")
            conf_result[key] = value
    for key in MANDATORY_KEYS:
        if key not in conf_result:
            return (False, {})
    return (True, conf_result)
