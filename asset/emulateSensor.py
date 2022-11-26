import boto3
import random
import json



class Sensors():

    sensorTable  = boto3.resource('dynamodb', endpoint_url="http://localhost:4566").Table(name='Sensors')
    
    
    def __init__(self , sensorObj : dict , seed : int ):
        
        self.res_sqs = boto3.resource('sqs', endpoint_url="http://localhost:4566")
        self.sensorObj = sensorObj
        self.seed = seed
        random.seed(self.seed)
    
    def sendMessage( self , queue  ):
        newMessage = dict()
        newMessage["sensor"] = self.sensorObj
        
        if (self.sensorObj["type"] == "producer"):
            value = random.randrange(start=10 , stop = 3000 )
        else : 
             value = random.randrange(start=200 , stop = 4000 )
        
        newMessage["data"] = str( value )
        self.sensorObj["value"] = str(value) 
        self.sensorTable.put_item(Item=self.sensorObj)
        queue.send_message(MessageBody = json.dumps(newMessage) )
        print("Message ->",self.sensorObj["region"]+"  "+ self.sensorObj["type"]+" "+newMessage["data"]+"\n")

    def emulate(self):
        
        queue = self.res_sqs.Queue(self.sensorObj["url_queue"])
        self.sendMessage(queue=queue)

        
        
        
        
        