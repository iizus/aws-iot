from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)


# from src.client.account import Account
# from src.client.endpoint import Endpoint
from src.client.project import Project

# account:Account = Account()
# endpoint:Endpoint = Endpoint()
project:Project = Project()