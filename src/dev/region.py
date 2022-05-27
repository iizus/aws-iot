from dev import Project



class Region:
    def __init__(self, endpoint_prefix:str, region:str='us-east-1') -> None:
        self.__endpoint:str = f'{endpoint_prefix}-ats.iot.{region}.amazonaws.com'


    def create_project(self, name:str='test') -> Project:
        return Project(self.__endpoint, name)