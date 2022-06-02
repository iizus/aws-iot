from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)


from src.client.account import check_fp_on

check_fp_on(account_name='test', template_name='ec2')
check_fp_on(account_name='multi', template_name='ec2')