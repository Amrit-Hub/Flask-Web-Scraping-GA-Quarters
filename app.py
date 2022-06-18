from flask import Flask, render_template, redirect, request, url_for, jsonify
from bs4 import BeautifulSoup
import requests
html_link = "http://www.equarters.nic.in/http_Public/Qtr_Current_Info_Ledger.aspx"
source = requests.get(html_link)



app = Flask(__name__)

@app.route('/')
def home():
    with requests.session() as s:
        s.get(html_link)
        soup = BeautifulSoup(s.get(html_link).content, "html.parser")
        units = soup.find(id="ctl00_ContentPlaceHolder1_ddlUnit")
        unit_list = [unit.text for unit in units.find_all('option')]
        return render_template("home.html", unit_list=unit_list)

def fetchdata(unit, quarter = '-Select-', building = '-Select-'):
    with requests.session() as s:
        s.get(html_link)  # load cookies
        soup = BeautifulSoup(s.get(html_link).content, "html.parser")
        data = {
            "ctl00$ContentPlaceHolder1$ToolkitScriptManager1": "",
            "ctl00_ContentPlaceHolder1_ToolkitScriptManager1_HiddenField": "",  #input
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": "",                                      #input
            "__VIEWSTATEGENERATOR": "",                             #input
            "__VIEWSTATEENCRYPTED": "",                             #input
            "__EVENTVALIDATION": "",                                 #input
        }
        # Get quarters list for unit

        for inp in soup.select("input[value]"):
            data[inp["name"]] = inp["value"]
        data["ctl00$ContentPlaceHolder1$ddlUnit"] = unit
        data["__EVENTTARGET"] = "ctl00$ContentPlaceHolder1$ddlUnit"
        data["ctl00$ContentPlaceHolder1$ToolkitScriptManager1"] = "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$ddlUnit"
        soup = BeautifulSoup(s.post(html_link, data=data).content, "html.parser")

        quarters = [
            opt["value"]
            for opt in soup.select("#ctl00_ContentPlaceHolder1_ddlQrtrType option")]
        if len(quarters)>0:
            quarters[0] = "-Select-"

        # Get building list for quarter
        
        for inp in soup.select("input[value]"):
            data[inp["name"]] = inp["value"]
        data["ctl00$ContentPlaceHolder1$ddlQrtrType"] = quarter
        data["__EVENTTARGET"] = "ctl00$ContentPlaceHolder1$ddlQrtrType"
        data["ctl00$ContentPlaceHolder1$ToolkitScriptManager1"] = "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$ddlQrtrType"
        soup = BeautifulSoup(s.post(html_link, data=data).content, "html.parser")

        buildings = [
            opt["value"]
            for opt in soup.select("#ctl00_ContentPlaceHolder1_ddlBldgNo option")]
        if len(buildings)>0:
            buildings[0] = "-Select-"

        return (quarters, buildings)

@app.route('/unit/<path:unit>', methods = ["POST", "GET"])
def quarter_type(unit):
    print(unit)
    quarters, buildings = fetchdata(unit)
    quarterArray = []
    for quarter in quarters:
        quarterObj = {}
        quarterObj["name"] = quarter
        quarterArray.append(quarterObj)
    return jsonify({"quarters": quarterArray})

@app.route('/quarter/<path:unit>/<path:quarter>', methods=['GET', 'POST'])
def building_no(unit, quarter):
    quarters, buildings = fetchdata(unit, quarter)
    print(unit, quarter)
    buildingArray = []
    for building in buildings:
        buildingObj = {}
        buildingObj["name"] = building
        buildingArray.append(buildingObj)
    return jsonify({"buildings": buildingArray})


@app.route('/Search', methods=['GET', 'POST'])
def searchBuilding():
    if request.method == "POST":
        unit = request.form["unitStatus"]
        quarter = request.form["quarterStatus"]
        building = request.form["buildingStatus"]


if __name__ == '__main__':
    app.run(debug=True)