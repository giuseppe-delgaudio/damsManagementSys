import boto3
import json
import statistics
from datetime import datetime
from boto3.dynamodb.conditions import Attr

def lambda_handler(event, context):

    #inizialize resource variable 
    sqs = boto3.resource('sqs', endpoint_url='http://localhost:4566')
    sns = boto3.resource('sns', endpoint_url='http://localhost:4566')
    dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:4566")

    #obtain urls queue 
    regionsTable : dict = dynamodb.Table(name="Regions")
    regions : dict = regionsTable.scan()["Items"]

    for region in regions: 

        queue = sqs.Queue(region["url_queue"])
        messageList = queue.receive_messages(MaxNumberOfMessages=200)

        if len(messageList) > 0 :

            dataProduction = []
            dataConsumption=[]

            for message in messageList: 
                message_body = json.loads(message.body)
                sensor = message_body["sensor"]
                data = message_body["data"]
                
                if sensor["type"] == "producer" : 
                    dataProduction.append(int(data))
                else: 
                    if sensor["type"] == "consumer":
                        dataConsumption.append(int(data))
                
                message.delete()
            
            try :
                consumption = int(statistics.mean(dataConsumption))
                   
            except Exception : 

                consumption = 0 
            
            try :
                production = int(statistics.mean(dataProduction))
            
            except Exception : 

                production = 0
            

            try :
                measurements : list = region["measurement"]
            
            except Exception : 

                measurements : list = list()
            
            measure = dict()
            measure["consumption"] = str(consumption)
            measure["production"] = str(production)
            measure["datetime"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            measurements.append(measure)
            region["measurement"] = measurements

            #obtain arn of TOPIC pump stored in Sensors Table
            sensors = dynamodb.Table(name="Sensors").scan(Select='ALL_ATTRIBUTES')["Items"]

            for sensor in sensors:
                if(sensor["region"] == "all") :
                    pumpArn = sensor
                    break
            
            #retrive TOPIC resources 
            topic = sns.Topic(pumpArn["arn"])

            
            #create message's attributes
            attributes = {}
            attributes["region"] = {"DataType" : "String" , "StringValue" : region["region_name"]}
            
            action = ""

            #check the condition to store energy 
            if production > consumption:
                action = "ON-STORAGE"
            else : 
                action = "ON-PRODUCTION"
                
    
            topic.publish(Message=action, MessageAttributes= attributes )
            regionsTable.put_item(Item = region)

