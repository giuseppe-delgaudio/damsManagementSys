from calendar import day_abbr
from time import sleep
import boto3
import json
from boto3.dynamodb.conditions import Attr
from threading import Event, Thread
from flask import Flask , make_response , request

class damsDatas:
    def __init__(self , dams , region) -> None:
        self.dams = dams 
        self.region = region
    

kill = Event()

app = Flask("damsEndpoint")
dynamodb_res  = boto3.resource('dynamodb', endpoint_url="http://localhost:4566")
sns  = boto3.resource('sns', endpoint_url="http://localhost:4566")

tableDams = dynamodb_res.Table("Dams")
tableRegions = dynamodb_res.Table("Regions")


dams = tableDams.scan()["Items"]
regions = tableRegions.scan()["Items"]

damsData = damsDatas(dams, regions)


#Function to emulate dams behavior 
def emultion( data : damsDatas ):

    res_sqs = boto3.resource('sqs', endpoint_url="http://localhost:4566")
    
    while True:
        if kill.is_set(): 
            break

        for dam in data.dams:
            
            
            #check if dam is in production mode
            if (dam["pump"] == "off") and (dam["valve"]=="open"):
                
                #check if level is upper than 10
                if(int(dam["level"]) >= 30 ) : 
                    
                    #create message for queue
                    newMessage = dict()
                    newMessage["sensor"] = dam
                    newMessage["sensor"]["type"] = "producer"

                    value = str(2000)
                    dam["production"] = value
                    
                    queue = res_sqs.Queue(dam["productionQueue"])
                    newMessage["data"] = value
                    
                    dam["level"] = str(int(dam["level"])-1)
                    queue.send_message(MessageBody = json.dumps(newMessage) )
                    
                    print("Production ON - DAM: "+dam["region"]+"production : "+dam["production"]+"level : "+str(dam["level"]))
                else : 

                    #stop pump and close valve
                    dam["pump"] = "off"
                    dam["valve"]="close"
                    dam["production"] = "0"
                    print("Production Impossible level too low - DAM: "+dam["region"]) 

            #check if dam is in storage mode 
            elif (dam["pump"] == "on") and (dam["valve"]=="close"):
                
                #check if level is lower than 90
                if(int(dam["level"]) <= 90 ):

                    #create message for queue
                    newMessage = dict()
                    newMessage["sensor"] = dam
                    newMessage["sensor"]["type"] = "consumer"

                    value = str(1200)
                    dam["production"] = value
                    queue = res_sqs.Queue(dam["productionQueue"])
                    newMessage["data"] = value
                    
                    queue.send_message(MessageBody = json.dumps(newMessage) )
                
                    dam["level"] = str(int(dam["level"])+1)
                    print("Storage ON - DAM: "+dam["region"]+"level : "+str(dam["level"]))
                else : 
                    
                    dam["pump"] = "off"
                    dam["valve"]="close"
                    dam["production"] = "0"
                    print("Storage impossible level too high - DAM: "+dam["region"]+" level : "+str(dam["level"]))

            #check if dam is in standby mode
            elif (dam["pump"] == "off") and (dam["valve"]=="close"):

                print("Standby State : "+dam["region"])

            else : 
                print("Impossibile State : "+dam["region"] + " Valve : "+dam["valve"]+ " Pump : "+dam["pump"])
            
            tableDams.put_item(Item=dam)
            
        sleep(2)


@app.route('/start', methods=['GET','POST'])
def getMessage():
   
    data = json.loads(request.data)
    region = data["MessageAttributes"]["region"]["Value"]

    for dam in damsData.dams :    
        if(region == dam["region"] ) : #check if region is correct at message receveid
            
            if (data["Message"] == "ON-PRODUCTION" ) : #if the messsage is "ON-PRODUCTION" dam open valve to produce energy

                dam["pump"] = "off"
                dam["valve"]="open"
                
            if (data["Message"] == "ON-STORAGE" ) : #if the message is "ON-STORAGE" dam power on the pump to storage water
                    
                dam["pump"] = "on"
                dam["valve"]="close"
    
    return make_response({}, 200)



#retrive pumpArn
pumpArn = dynamodb_res.Table(name="Sensors").scan(Select='ALL_ATTRIBUTES', FilterExpression = Attr(name="region").eq("all"))["Items"][0]
                
#retrive TOPIC resources 
topic = sns.Topic(pumpArn["arn"])
topic.subscribe( Protocol='http', Endpoint='http://host.docker.internal:4554/start' )
print("/start subscribed to topic\n")



damsThread : Thread = Thread(target=emultion , args={damsData} )

damsThread.start()
app.run(port=4554)

print("Server stopped")
kill.set()


damsThread.join(timeout=5)

if damsThread.is_alive():
    print("Error during emulation stop")
else :
    print("Emulation stopped")

exit()