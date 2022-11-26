from time import sleep
import emulateSensor
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb_res  = boto3.resource('dynamodb', endpoint_url="http://localhost:4566")

sensorTable = dynamodb_res.Table(name='Sensors')
sensorList = sensorTable.scan(FilterExpression= Attr("region").ne("all"))

sensorObj : list = list()
i = 0

for sensor in sensorList["Items"]: 
    sensorObj.append( emulateSensor.Sensors(sensor , i) )
    i+=1

while True:
    for obj in sensorObj : 
        
        obj.emulate()
        sleep(5)
 
