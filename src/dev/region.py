from project import Project



class Region:
    def __init__(self, endpoint:str) -> None:
        self.endpoint:str = endpoint
        

    # def create_project(self, name:str='test') -> Project:
    #     return Project(name)