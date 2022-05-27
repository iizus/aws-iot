from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)

from utils.util import load_json

from dev import Region



class Account:
    def __init__(self, name:str='test', config_path:str='endpoint.json') -> None:
        '''
        >>> test:Account = Account(name='test')
        '''
        endpoints:dict = load_json(config_path)
        self.__endpoint_prefix:str = endpoints.get(name)


    def use_region(self, name:str='us-east-1') -> Region:
        '''
        >>> test:Account = Account(name='test')
        >>> tokyo:Region = test.use_region(name='ap-northeast-1')
        '''
        region:Region = Region(endpoint_prefix=self.__endpoint_prefix, region=name)
        return region



if __name__ == '__main__':
    from doctest import testmod
    testmod()