from topic import Topic



class Connection:
    def __init__(self) -> None:
        pass

    def use_topic(self, name:str='test/test') -> Topic:
        return Topic(name)

    def disconnect(self) -> dict:
        return response