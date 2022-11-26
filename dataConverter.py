import boto3
import json
from datetime import datetime
from boto3.dynamodb.conditions import Attr
import statistics

def lambda_handler(event, context):

    #inizialize resource variable 
    dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:4566")

    #obtain dams information 
    damsTable : dict = dynamodb.Table(name="Dams")
    sensorsTable : dict = dynamodb.Table(name="Sensors")
    dataStatTable : dict = dynamodb.Table(name="DataStat")
    regionTable : dict = dynamodb.Table(name="Regions")

    dams : dict = damsTable.scan()["Items"]
    sensors : dict =  sensorsTable.scan(FilterExpression= Attr("region").ne("all") & Attr("type").ne("dam_producer"))["Items"]
    
    damsMark : list = list()
    sensorsMark : list = list()
    

    for dam in dams : 
        tmpDict : dict = {}
        page = "<h4>"+dam["name"]+"</h4>"\
            "<table>"\
                "<tr>"\
                    "<th>Parameter</th>"\
                    "<th>Value</th>"\
                "</tr>"\
                "<tr>"\
                    "<td>Type</td><td>producer</td>"\
                "</tr>"\
                "<tr>"\
                    "<td>Valve</td><td>"+dam["valve"]+"</td>"\
                "</tr>"\
                "<tr>"\
                    "<td>Pump</td><td>"+dam["pump"]+"</td>"\
                "</tr>"\
                "<tr>"\
                    "<td>Level</td><td>"+dam["level"]+"</td>"\
                "</tr>"\
                "<tr>"\
                    "<td>Production</td><td>"+dam["production"]+"</td>"\
                "</tr>"\
                "<tr>"\
                    "<td>Region</td><td>"+dam["region"]+"</td>"\
                "</tr>"\
            "</table>"
        tmpDict["infoPage"] = page
        tmpDict["name"] = dam["name"]
        tmpDict["latitude"] = dam["latitude"]
        tmpDict["longitude"] = dam["longitude"]
        
        damsMark.append(tmpDict)
    
    for sensor in sensors :
        tmpDict : dict = {}
        page = "<h4>"+sensor["type"]+"</h4>"\
            "<table>"\
                "<tr>"\
                    "<th>Parameter</th>"\
                    "<th>Value</th>"\
                "</tr>"\
                "<tr>"\
                    "<td>Region</td><td>"+sensor["region"]+"</td>"\
                "</tr>"\
                "<tr>"\
                    "<td>Sensor id</td><td>"+sensor["sensor_id"]+"</td>"\
                "</tr>"\
                "<tr>"\
                    "<td>Last sending value</td><td>"+str(sensor["value"])+" kw</td>"\
                "</tr>"\
            "</table>"
        tmpDict["infoPage"] = page
        tmpDict["name"] = sensor["sensor_id"]
        tmpDict["type"] = sensor["type"]
        tmpDict["latitude"] = sensor["latitude"]
        tmpDict["longitude"] = sensor["longitude"]
        
        sensorsMark.append(tmpDict)


    regions : dict = regionTable.scan()["Items"]

    stats : dict = {}

    for region in regions: 

        label = []
        production = []
        consumption = []
        avgProd=[]
        avgCons=[]
        try :  
            
            for measure in region["measurement"]: 
                label.append(measure["datetime"])
                consumption.append(int(measure["consumption"]))
                production.append(int(measure["production"]))
        except :
            
            production.append(0)
            consumption.append(0)
         
        avgProd = round(statistics.mean(production),1)
        avgCons = round(statistics.mean(consumption),1)
        stats[region["region_name"]] = {}
        stats[region["region_name"]]["label"] = label
        stats[region["region_name"]]["production"] = production
        stats[region["region_name"]]["consumption"] = consumption
        stats[region["region_name"]]["avgConsumption"] = avgCons
        stats[region["region_name"]]["avgProduction"] = avgProd
        if (  stats[region["region_name"]]["avgProduction"] == 0  and  stats[region["region_name"]]["avgConsumption"] == 0 ):
            stats[region["region_name"]]["time"] = str("")
        else: 
            stats[region["region_name"]]["time"] = str(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        
            



    data : dict = {}
    data["dams"] = damsMark
    data["sensors"] = sensorsMark
    data["dataSensor"] = sensors
    data["dataDams"] = dams
    data["dataGraph"] = stats

    responseObj = {}
    responseObj["statusCode"]  = "200"
    responseObj["headers"] = {}
    responseObj["headers"]["Content-Type"] = "application/json"
    responseObj["headers"]["Access-Control-Allow-Headers"] = "*"
    responseObj["headers"]["Access-Control-Allow-Methods"] = "*"
    responseObj["headers"]["Access-Control-Allow-Origin"] = "*"
    responseObj["headers"]["Accept"] = "*/*"
    


    responseObj["body"] = json.dumps(data)

    responseObj["headers"] = json.dumps(responseObj["headers"])
    


    return {
        'statusCode' : 200,
        'body' : json.dumps(data)
    }
