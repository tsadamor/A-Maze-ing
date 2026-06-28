import os
from typing import Any

MANDATORY_KEYS = [
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
]

ERROR_MSG = "Aborted: Bad Configuration File"


def parse_file(file_name: str) -> tuple[bool, dict[str, str]]:

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


def convert_config_data(conf: dict[str, str]) -> tuple[bool, dict[str, Any]]:
    converted_res: dict[str, Any] = {}
    for key, value in conf.items():
        if key == "WIDTH" or key == "HEIGHT":
            try:
                converted_res[key] = int(value)
            except ValueError:
                return (False, {})
        elif key == "ENTRY" or key == "EXIT":
            try:
                x, y = value.split(",")
                converted_res[key] = (int(x), int(y))
            except ValueError:
                return (False, {})
        elif key == "PERFECT":
            is_perfect = value.lower() in ["true", "1", "yes"]
            converted_res[key] = is_perfect
        else:
            converted_res[key] = value
    return (True, converted_res)


def is_valid_dict(conf: dict[str, Any]) -> bool:
    maze_width = conf["WIDTH"]
    maze_height = conf["HEIGHT"]
    entry_width, entry_height = conf["ENTRY"][0], conf["ENTRY"][1]
    exit_width, exit_height = conf["EXIT"][0], conf["EXIT"][1]

    if maze_width <= 1 or maze_height <= 1:
        return False
    if entry_width < 0 or entry_height < 0:
        return False
    if exit_width < 0 or exit_height < 0:
        return False
    if maze_width <= entry_width or maze_width <= exit_width:
        return False
    if maze_height <= entry_height or maze_height <= exit_height:
        return False
    if conf["ENTRY"] == conf["EXIT"]:
        return False

    return True


def parser(file_name: str) -> tuple[bool, dict[str, Any]]:
    initial_parse_result = parse_file(file_name)
    if not initial_parse_result[0]:
        print(ERROR_MSG)
        return (False, {})

    converted_parse_result = convert_config_data(initial_parse_result[1])
    if not converted_parse_result[0]:
        print(ERROR_MSG)
        return (False, {})

    if not is_valid_dict(converted_parse_result[1]):
        print(ERROR_MSG)
        return (False, {})

    return (True, converted_parse_result[1])
