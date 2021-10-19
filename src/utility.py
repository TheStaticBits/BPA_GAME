"""
This is the file in which resides the 
functions which manage the save data.
"""

def get_file() -> str:
    with open("save.txt", "r") as file:
        text = file.read()
    
    return text


def get_level() -> int:
    file = get_file()


def get_position():
    file = get_file()