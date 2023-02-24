from . import DATA_DIR


def get_names():
    names_path = DATA_DIR.joinpath("names.txt")
    with open(names_path, "r", encoding="utf-8") as names_file:
        return names_file.readlines()
