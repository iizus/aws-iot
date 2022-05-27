from region import Region

from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)

from utils.util import load_json



class Account:
    def __init__(self, name:str='test', config_path:str='endpoint.json') -> None:
        # '''
        # >>> test:Account = Account(name='test')
        # Account: test
        # '''
        endpoints:dict = load_json(config_path)
        self.__endpoint_prefix:str = endpoints.get(name)
        print(f"Account: {name}")


    def use_region(self, name:str='us-east-1') -> Region:
        # '''
        # >>> test:Account = Account(name='test')
        # Account: test
        # >>> tokyo:Region = test.use_region(name='ap-northeast-1')
        # '''
        endpoint:str = f'{self.__endpoint_prefix}-ats.iot.{name}.amazonaws.com'
        region:Region = Region(endpoint)
        return region



# if __name__ == '__main__':
#     from doctest import testmod
#     testmod()