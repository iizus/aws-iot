from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)

from src.iot import IoT

iot:IoT = IoT(config_path='test1.json')