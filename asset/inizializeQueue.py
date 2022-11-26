from filecmp import dircmp
import boto3
import botocore
import json
from boto3.dynamodb.conditions import Attr

# create aws client
dynamodb_res  = boto3.resource('dynamodb', endpoint_url="http://localhost:4566")
sqs_res  = boto3.resource('sqs', endpoint_url="http://localhost:4566")

regionTable = dynamodb_res.Table(name='Regions')
damsTable = dynamodb_res.Table(name='Dams')
regions : dict = regionTable.scan( AttributesToGet=['region_name'], Select = "SPECIFIC_ATTRIBUTES" )
sensorTable = dynamodb_res.Table(name='Sensors')
listOfQueue : dict = dict()
sensors : dict = sensorTable.scan()

for region  in regions['Items']: 
    region["region_name"] = region['region_name'].replace(" ","")
    queue = sqs_res.create_queue (QueueName= region['region_name'] )

    print("Queue ",region['region_name'],"created\n")
    region["url_queue"] = queue.url
    listOfQueue[region['region_name']] = region["url_queue"]
    regionTable.put_item(Item=region)
    
dams = damsTable.scan()["Items"]

for dam in dams :
    dam["productionQueue"] = listOfQueue[dam["region"]]
    damsTable.put_item(Item=dam)


for sensor in sensors["Items"]: 
    sensor["url_queue"] = listOfQueue.get(sensor["region"])
    sensorTable.put_item(Item = sensor)

    
sns_res  = boto3.resource('sns', endpoint_url="http://localhost:4566")


topic = sns_res.create_topic(Name="pump_notify")
print("topic pump notify created\n")
sensorTable  = dynamodb_res.Table(name='Sensors')

#topic.subscribe( Protocol='http', Endpoint='http://172.19.0.3:1880/start' )
#print("/start subscribed to topic\n")

sensorPump = dict()
sensorPump["sensor_id"] = "0"
sensorPump["region"] = "all"
sensorPump["arn"] = topic.arn
#sensorPump["endpoint"] = 'http://172.19.0.3:1880/start'
sensorTable.put_item(Item=sensorPump)

