import boto3
import random
import json



class Sensors():

    sensorTable  = boto3.resource('dynamodb', endpoint_url="http://localhost:4566").Table(name='Sensors')
    
    
    def __init__(self , sensorObj : dict , seed : int ):
        
        self.res_sqs = boto3.resource('sqs', endpoint_url="http://localhost:4566")
        self.sensorObj = sensorObj
        self.seed = seed
    
    def sendMessage( self , queue  ):
        newMessage = dict()
        newMessage["sensor"] = self.sensorObj
        
        if (self.sensorObj["type"] == "producer"):
            value = random.randrange(start=0 , stop = 2000 )
        else : 
             value = random.randrange(start=1000 , stop = 5000 )
        
        newMessage["data"] = str( value )
        self.sensorObj["value"] = str(value) 
        self.sensorTable.put_item(Item=self.sensorObj)
        queue.send_message(MessageBody = json.dumps(newMessage) )
        print("Message ->",self.sensorObj["region"]+"  "+ self.sensorObj["type"]+" "+newMessage["data"]+"\n")

    def emulate(self):
        random.seed(self.seed)
        queue = self.res_sqs.Queue(self.sensorObj["url_queue"])
        self.sendMessage(queue=queue)

        
        
        
        
        