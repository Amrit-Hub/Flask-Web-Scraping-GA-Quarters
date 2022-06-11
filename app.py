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

def fetchdata(unit, quarter = '-Select-'):
    with requests.session() as s:
        s.get(html_link)  # load cookies
        soup = BeautifulSoup(s.get(html_link).content, "html.parser")
        data = {
            "ctl00$ContentPlaceHolder1$ToolkitScriptManager1": "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$ddlUnit",
            "__EVENTTARGET": "ctl00$ContentPlaceHolder1$ddlUnit",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": "",
            "__VIEWSTATEGENERATOR": "",
            "__VIEWSTATEENCRYPTED": "",
            "__EVENTVALIDATION": "",
            "ctl00$ContentPlaceHolder1$ddlUnit": "",
        }
        # print(soup.select("input[value]"))
        for inp in soup.select("input[value]"):
            data[inp["name"]] = inp["value"]

        data["ctl00$ContentPlaceHolder1$ddlUnit"] = unit
        data["ctl00$ContentPlaceHolder1$ToolkitScriptManager1"] = "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$ddlQrtrType"
        data["__EVENTTARGET"] = "ctl00$ContentPlaceHolder1$ddlQrtrType"
        soup = BeautifulSoup(s.post(html_link, data=data).content, "html.parser")

        quarters = [
            opt["value"]
            for opt in soup.select("#ctl00_ContentPlaceHolder1_ddlQrtrType option")
        ]
        if unit != "-Select-":
            quarters[0] = "-Select-"
        data["ctl00$ContentPlaceHolder1$ddlQrtrType"] = quarter
        for inp in soup.select("input[value]"):
            data[inp["name"]] = inp["value"]

        soup = BeautifulSoup(s.post(html_link, data=data).content, "html.parser")
        buildings = [
            opt["value"]
            for opt in soup.select("#ctl00_ContentPlaceHolder1_ddlBldgNo option")
        ]
        if quarter != "-Select-":
            buildings[0] = "-Select-"
        return (quarters, buildings)


@app.route('/<unit>', methods = ["POST", "GET"])
def quarter_type(unit):
    quarters, buildings = fetchdata(unit)
    quarterArray = []
    for quarter in quarters:
        quarterObj = {}
        quarterObj["name"] = quarter
        quarterArray.append(quarterObj)
    return jsonify({"quarters": quarterArray})

@app.route('/<unit>/<quarter>', methods=['GET', 'POST'])
def building_no(unit, quarter):
    quarters, buildings = fetchdata(unit, quarter)
    buildingArray = []
    for building in buildings:
        buildingObj = {}
        buildingObj["name"] = building
        buildingArray.append(buildingObj)
    return jsonify({"buildings": buildingArray})


@app.route('/search', methods=['GET', 'POST'])
def searchBuilding():
    pass

if __name__ == '__main__':
    app.run(debug=True)