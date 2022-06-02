from json import load
from os.path import dirname, abspath
from sys import path



def print_log(subject:str, message:str) -> None:
    print(f"[{subject}] {message}")
    

def load_json(json_path:str) -> dict:
    with open(json_path) as json_file:
        contents:dict = load(json_file)
        return contents


def get_path_of_parent_dir_of(cild_path:str, num:int) -> str:
    num -= 1
    if num <= 0:
        return cild_path
    else:
        parent_dir:str = dirname(cild_path)
        return get_path_of_parent_dir_of(parent_dir, num)


def add_parent_dir_path_from(num:int) -> str:
    this_file_path:str = abspath(__file__)
    parent_dir:str = get_path_of_parent_dir_of(this_file_path, num)
    path.append(parent_dir)
    return parent_dir



if __name__ == '__main__':
    from doctest import testmod
    testmod()