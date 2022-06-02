# from awscrt.http import HttpProxyOptions
# from src.client.account import Endpoint


# class Port(Endpoint):
#     def __init__(self, name:str, ca:str, number:int=8883) -> None:
#         self.name:str = name
#         self.ca:str = ca
#         self.port:int = number
#         self.proxy:HttpProxyOptions = None
#         print(f"[Endpoint] Set to {self.name}:{self.port}")


#     def set_proxy(self, host:str, port:int=443):
#         proxy:HttpProxyOptions = HttpProxyOptions(host, port)
#         print(f"[Endpoint ]Set HTTP proxy as {host}:{port} for {self.name}:{self.port}")
#         return Proxy(self.name, self.ca, self.port, proxy)



# class Proxy(Port):
#     def __init__(self, name:str, ca:str, number:int=8883, proxy:HttpProxyOptions=None) -> None:
#         self.name:str = name
#         self.ca:str = ca
#         self.port:int = number
#         self.proxy:HttpProxyOptions = proxy