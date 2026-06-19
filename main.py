from parser import parser
CONF_FILE_NAME = "config.txt"


def main():
    parse_result = parser(CONF_FILE_NAME)
    if not parse_result[0]:
        return


if __name__ == "__main__":
    main()
