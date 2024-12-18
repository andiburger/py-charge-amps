from chargeampsclient import Client
from chargeampscfgparser import ChargeAmpsCfgParser
import asyncio


def testCfg1()->bool:
    print("Test1 configuration reader ...")
    cfgParser = ChargeAmpsCfgParser()
    userData = cfgParser.get_user_data()
    if userData["email"] == 'None':
        print("successful")
        return True
    else:
        print("failed")
        return False

def testCfg2()->bool:
    print("Tes2 configuration reader ...")
    cfgParser = ChargeAmpsCfgParser("../mycfg.ini")
    userData = cfgParser.get_user_data()
    if userData["email"] == "andiburger@gmail.com":
        print("successful")
        return True
    else:
        print("failed")
        return False

async def testToken():
    print("Test authentification and token retrieval ... ")
    cfgParser = ChargeAmpsCfgParser("../mycfg.ini")
    userData = cfgParser.get_user_data()
    myclient = Client(userData["email"],userData["password"],userData["apiKey"],cfgParser.get_general_data["baseUrl"])
    await myclient.init_session()
    if myclient._session._token != None:
        print(myclient._session._token)
        myclient._user.print_user_info()
        await myclient.close_session()
        print("successful")
        return True
    else:
        await myclient.close_session()
        print("failed")
        return False


if __name__ ==  '__main__':
    testCfg1()
    testCfg2()
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(testToken())