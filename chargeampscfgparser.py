import configparser


class ChargeAmpsCfgParser:
    """ChargeAmpsCfgParser class to read configuration file for ChargeAmps API client.
    This class is used to read the configuration file and provide user data and general data for the API client.
    """
    def __init__(self, cfgFile:str = None):
        """Constructor for ChargeAmpsCfgParser class.
        Args:
            cfgFile (str): Path to the configuration file. If None, defaults to "cfg.ini".
        """
        self.__config = configparser.ConfigParser()
        self.__config.read(cfgFile or "cfg.ini")
        return None
    
    def get_user_data(self)->dict:
        """Get user data from the configuration file.
        Returns:
            dict: Dictionary containing user data (email, password, apiKey).
        """
        return {"email":self.__config["USERDATA"]["email"], "password":self.__config["USERDATA"]["password"], "apiKey":self.__config["USERDATA"]["apiKey"]}
    
    def get_general_data(self)->dict:
        """Get general data from the configuration file.
        Returns:
            dict: Dictionary containing general data (baseUrl, pricekWh).
        """
        return {"baseUrl":self.__config["GENERAL"]["baseUrl"],"pricekWh":self.__config["GENERAL"]["pricekWh"]}
    