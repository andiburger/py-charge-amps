import configparser


class ChargeAmpsCfgParser:
    def __init__(self, cfgFile:str = None):
        self.__config = configparser.ConfigParser()
        self.__config.read(cfgFile or "cfg.ini")
        return None
    
    def get_user_data(self)->dict:
        return {"email":self.__config["USERDATA"]["email"], "password":self.__config["USERDATA"]["password"], "apiKey":self.__config["USERDATA"]["apiKey"]}
    
    def get_general_data(self)->dict:
        return {"baseUrl":self.__config["GENERAL"]["baseUrl"],"pricekWh":self.__config["GENERAL"]["pricekWh"]}
    