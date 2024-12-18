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

async def testAPI():
    print("Test authentification and token retrieval ... ")
    cfgParser = ChargeAmpsCfgParser("../mycfg.ini")
    userData = cfgParser.get_user_data()
    myclient = Client(userData["email"],userData["password"],userData["apiKey"],cfgParser.get_general_data()["baseUrl"])
    await myclient.init_session()
    if myclient._session._token != None:
        print(myclient._session._token)
        myclient._user.print_user_info()
        print("successful")
    else:
        await myclient.close_session()
        print("failed")
        return False
    try:
        print("Test get chargepoints ...")
        chargePoints = await myclient.get_chargepoints()
        await myclient.get_chargepoint_status(chargePoints[0].id)
        print("succesful")
        print("Test user data retrieval ...")       
        user = await myclient.get_user(myclient._user._userid)
        print(user.email)
        print("succesful")
        print("Test charging sessions retrieval ...")
        charging_sessions = await myclient.get_connector_chargingsessions(charge_point_id=chargePoints[0].id,connector_id=1)
        print(charging_sessions[0].total_consumption_kwh)
        print("successful")
        await myclient.close_session()
    except Exception as e:
        print(e)
        print("failed")
        await myclient.close_session()


if __name__ ==  '__main__':
    testCfg1()
    testCfg2()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(testAPI())