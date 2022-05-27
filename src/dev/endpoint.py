import certs



class Endpoint:
    def __init__(self, endpoint:str) -> None:
        self.endpoint:str = endpoint
        self.ca = certs.get_ca_path()