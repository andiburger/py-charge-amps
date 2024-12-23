from chargeampsclient import Client
from chargeampscfgparser import ChargeAmpsCfgParser
from xlsxresultwriter import XlsxResult

import unittest

class TestCfgLoader(unittest.TestCase):

    def testCfg1(self):
        """Test1 configuration reader"""
        cfgParser = ChargeAmpsCfgParser()
        userData = cfgParser.get_user_data()
        self.assertEqual(userData["email"], 'None')

    def testCfg2(self):
        """Test2 configuration reader"""
        cfgParser = ChargeAmpsCfgParser("../mycfg.ini")
        userData = cfgParser.get_user_data()
        self.assertEqual(userData["email"], "andiburger@gmail.com")
    
    def testCfg3(self):
        """Test2 configuration reader"""
        cfgParser = ChargeAmpsCfgParser("../mycfg.ini")
        general_data = cfgParser.get_general_data()
        self.assertIn('pricekWh',general_data.keys())

class TestPyChargeAmpsAPI(unittest.IsolatedAsyncioTestCase):
        async def testAPI(self):
            """Test Python API for ChargeAMPs"""
            cfgParser = ChargeAmpsCfgParser("../mycfg.ini")
            userData = cfgParser.get_user_data()
            general_data= cfgParser.get_general_data()
            myclient = Client(userData["email"],userData["password"],userData["apiKey"],general_data["baseUrl"])
            await myclient.init_session()
            self.assertNotEqual(myclient._session._token, None)
            with self.subTest(msg="Test chargepoints"):
                chargePoints = await myclient.get_chargepoints()
                self.assertGreater(len(chargePoints),0)
            with self.subTest(msg="Test chargepoint status"):
                status = await myclient.get_chargepoint_status(chargePoints[0].id)
                self.assertEqual(status.status, "Online")
            with self.subTest(msg="Test user data retrieval"):       
                user = await myclient.get_user(myclient._user._userid)
                cfgParser = ChargeAmpsCfgParser("../mycfg.ini")
                userData = cfgParser.get_user_data()
                self.assertEqual(user.email,userData["email"])
            with self.subTest(msg="Test charging sessions retrieval"):
                charging_sessions = await myclient.get_connector_chargingsessions(charge_point_id=chargePoints[0].id,connector_id=1)
                self.assertGreater(charging_sessions[0].total_consumption_kwh,0)
            with self.subTest(msg="Test charging session retrieval for specific rfid"):
                charging_sessions = await myclient.get_rfid_chargingsessions(charge_point_id=chargePoints[0].id,connector_id=1,rfid="9C8BE8DF")
                self.assertGreater(len(charging_sessions),0)
                result_writer = XlsxResult()
                result_writer.gen_output_file(charging_sessions,general_data["pricekWh"])
            await myclient.close_session()


if __name__ ==  '__main__':
    unittest.main(verbosity=2)
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(testAPI())