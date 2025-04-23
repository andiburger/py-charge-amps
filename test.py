from chargeampsclient import Client
from chargeampscfgparser import ChargeAmpsCfgParser
from xlsxresultwriter import XlsxResult
from utils.utils import get_or_create_encryption_key, decrypt

import unittest
from unittest.mock import patch, mock_open
import configparser

from utils.cfg_file_generator import prompt_cfg_interactive


class TestCfgFileGenerator(unittest.TestCase):
    @patch("builtins.input")
    @patch("getpass.getpass")
    @patch("utils.cfg_file_generator.encrypt")
    @patch("utils.cfg_file_generator.get_or_create_encryption_key")
    @patch("builtins.open", new_callable=mock_open)
    def test_prompt_cfg_interactive(
        self, mock_file, mock_get_key, mock_encrypt, mock_getpass, mock_input
    ):
        # Simulate user input
        mock_input.side_effect = [
            "test@example.com",  # email input
            "",  # baseUrl (default used)
            "0.25",  # price per kWh
            "test_cfg.ini"  # file path
        ]
        mock_getpass.side_effect = [
            "supersecret",  # password
            "apikey123",    # api key
        ]

        mock_get_key.return_value = b"fakekey"
        mock_encrypt.side_effect = lambda val, key: f"ENCRYPTED({val})"

        # Run the function
        prompt_cfg_interactive()

        # Get the written content
        handle = mock_file()
        written_content = "".join(call.args[0] for call in handle.write.call_args_list)
        config = configparser.ConfigParser()
        config.read_string(written_content)

        self.assertEqual(config["USERDATA"]["email"], "ENCRYPTED(test@example.com)")
        self.assertEqual(config["USERDATA"]["password"], "ENCRYPTED(supersecret)")
        self.assertEqual(config["USERDATA"]["apiKey"], "apikey123")
        self.assertEqual(config["GENERAL"]["baseUrl"], "https://api.chargeamps.com")
        self.assertEqual(config["GENERAL"]["pricekWh"], "0.25")


class TestCfgLoader(unittest.TestCase):


    def setUp(self):
        self.key = get_or_create_encryption_key()
        self.assertIsNotNone(self.key, "Encryption key should not be None")

    def testCfg1(self):
        """Test1 configuration reader"""
        cfgParser = ChargeAmpsCfgParser()
        userData = cfgParser.get_user_data()
        self.assertEqual(userData["email"], 'None')

    def testCfg2(self):
        """Test2 configuration reader"""
        cfgParser = ChargeAmpsCfgParser("../mycfg.ini")
        userData = cfgParser.get_user_data()
        self.assertEqual(userData["email"], "gAAAAABoB9PepOgdxVn8UklN3Z-9ofOp71qVF0du3r651xRlSY2n9c5WyK6wBPC6xEx6hXNSuy4enBChHYrW0I6fnk6Fk5T99_XnyKf7luERp1UhNDD3jXo=")
    
    def testCfg3(self):
        """Test2 configuration reader"""
        cfgParser = ChargeAmpsCfgParser("../mycfg.ini")
        general_data = cfgParser.get_general_data()
        self.assertIn('pricekWh',general_data.keys())

class TestPyChargeAmpsAPI(unittest.IsolatedAsyncioTestCase):
        def setUp(self):
            self.key = get_or_create_encryption_key()
            self.assertIsNotNone(self.key, "Encryption key should not be None")

        async def testAPI(self):
            """Test Python API for ChargeAMPs"""
            cfgParser = ChargeAmpsCfgParser("../mycfg.ini")
            userData = cfgParser.get_user_data()
            general_data= cfgParser.get_general_data()
            myclient = Client(decrypt(userData["email"], self.key),decrypt(userData["password"],self.key),userData["apiKey"],general_data["baseUrl"])
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
                user = await myclient.get_user(myclient._user._userid) 
                print(user)
                self.assertEqual(user.email,userData["email"])
            await myclient.close_session()


if __name__ ==  '__main__':
    unittest.main(verbosity=2)
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(testAPI())