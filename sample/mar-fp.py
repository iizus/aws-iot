from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)


from src.client.account import check_fp_on

check_fp_on(account_name='test')
check_fp_on(account_name='multi')