from flask import Flask, render_template, request
from chargeampsclient import Client
from chargeampscfgparser import ChargeAmpsCfgParser
from xlsxresultwriter import XlsxResult
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
async def index():
    if request.method == "POST":
        rfid = request.form["rfid"]
        start_date =  datetime.strptime(request.form["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d")
        path = request.form["save_location"]
        print(f"RFID: {rfid}, Start: {start_date}, End: {end_date}")
        cfgParser = ChargeAmpsCfgParser("../mycfg.ini")
        userData = cfgParser.get_user_data()
        general_data= cfgParser.get_general_data()
        myclient = Client(userData["email"],userData["password"],userData["apiKey"],general_data["baseUrl"])
        await myclient.init_session()
        chargePoints = await myclient.get_chargepoints()
        if chargePoints:
            chargePoint = chargePoints[0]
            connector_id = 1
            charging_sessions = await myclient.get_rfid_chargingsessions(charge_point_id=chargePoint.id, connector_id=connector_id, rfid=rfid, start_time=start_date, end_time=end_date)
            result_writer = XlsxResult()
            result_writer.gen_output_file(charging_sessions, general_data["pricekWh"],path)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)