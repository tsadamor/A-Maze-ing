from parser import parse_config

CONF_FILE_NAME = "config.txt"


def main():
    conf_parse = parse_config(CONF_FILE_NAME)
    try:
        if not conf_parse[0]:
            raise Exception("Bad Configuration File")
    except Exception as err:
        print(f"Aborting: {err}")
    for key, value in conf_parse[1].items():
        print(key, value)


if __name__ == "__main__":
    main()
