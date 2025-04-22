from flask import Flask, render_template, request, send_file, jsonify
from chargeampsclient import Client
from chargeampscfgparser import ChargeAmpsCfgParser
from xlsxresultwriter import XlsxResult
from datetime import datetime
from utils.utils import get_or_create_encryption_key, decrypt

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
async def index():
    global myclient 
    key = get_or_create_encryption_key()
    if request.method == "POST":
        rfid = request.form["rfid"]
        start_date =  datetime.strptime(request.form["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d")
        print(f"RFID: {rfid}, Start: {start_date}, End: {end_date}")
        cfgParser = ChargeAmpsCfgParser("mycfg.ini")
        userData = cfgParser.get_user_data()
        general_data= cfgParser.get_general_data()
        myclient = Client(decrypt(userData["email"],key),decrypt(userData["password"],key),userData["apiKey"],general_data["baseUrl"])
        await myclient.init_session()
        chargePoints = await myclient.get_chargepoints()
        if chargePoints:
            chargePoint = chargePoints[0]
            connector_id = 1
            charging_sessions = await myclient.get_rfid_chargingsessions(charge_point_id=chargePoint.id, connector_id=connector_id, rfid=rfid, start_time=start_date, end_time=end_date)
            result_writer = XlsxResult()
            output = result_writer.gen_output_file(charging_sessions, general_data["pricekWh"])
            await myclient.close_session()
            return send_file(
                output,
                as_attachment=True,
                download_name="charging_sessions.xlsx",
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    return render_template("index.html")

@app.route("/get_rfid_tags", methods=["POST"])
async def get_rfid_tags():
    key = get_or_create_encryption_key()
    cfgParser = ChargeAmpsCfgParser("mycfg.ini")
    userData = cfgParser.get_user_data()
    general_data= cfgParser.get_general_data()
    myclient = Client(decrypt(userData["email"],key),decrypt(userData["password"],key),userData["apiKey"],general_data["baseUrl"])
    await myclient.init_session()
    chargePoints = await myclient.get_chargepoints()
    if chargePoints:
        chargePoint = chargePoints[0]
        rfid_tags = await myclient.get_registered_rfid_tags(chargePoint.id)
        await myclient.close_session()
        return jsonify({"tags": rfid_tags})
    await myclient.close_session()
    return jsonify({"error": "No charge points found."})

if __name__ == "__main__":
    app.run(debug=True)