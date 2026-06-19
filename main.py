from parser import parse_config
from parser.parse import convert_config_data, is_valid_dict

CONF_FILE_NAME = "config.txt"


def main():
    conf_parse = parse_config(CONF_FILE_NAME)
    try:
        if not conf_parse[0]:
            raise Exception("Bad Configuration File")
    except Exception as err:
        print(f"Aborting: {err}")
        return

    try:
        convert_parse = convert_config_data(conf_parse[1])
        if not convert_parse[0]:
            raise Exception("Bad Configuration File")
    except Exception as err:
        print(f"Aborting {err}")
        return

    if not is_valid_dict(convert_parse[1]):
        print("Aborting: Bad Configuration File")
        return

    for k, v in convert_parse[1].items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
