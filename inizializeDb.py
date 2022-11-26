import boto3
import json

# create aws client
dynamodb_res  = boto3.resource('dynamodb', endpoint_url="http://localhost:4566")

# inizialize table for sensors if not exists
try: 
    
    tableSensors = dynamodb_res.Table(name='Sensors')
    tableSensors.table_status
    print("Already Created -> Sensors")

except Exception:
    
    tableSensors  = dynamodb_res.create_table(
        TableName='Sensors',
        KeySchema=[
            {
                'AttributeName': 'sensor_id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'region',
                'KeyType': 'RANGE'
            }
            
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'sensor_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'region',
                'AttributeType': 'S'
            },


        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    
    #check if tables are ready 
    tableSensors.wait_until_exists()
    
    print(tableSensors.name," created")

# inizialize table for regions if not exists
try: 
    
    tableRegions = dynamodb_res.Table(name='Regions')
    tableRegions.table_status
    print("Already Created -> Regions")

except Exception:

    tableRegions  = dynamodb_res.create_table(
        TableName='Regions',
        KeySchema=[
            {
                'AttributeName': 'region_name',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'region_name',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    #check if tables are ready
    tableRegions.wait_until_exists()

    print(tableRegions.name," created")

# inizialize table for dams if not exists
try: 
    
    tableDams = dynamodb_res.Table(name='Dams')
    tableDams.table_status
    print("Already Created -> Dams")

except Exception:

    tableDams = dynamodb_res.create_table(
        TableName='Dams',
        KeySchema=[
            {
                'AttributeName': 'dam_id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'region',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'dam_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'region',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    #check if tables are ready
    tableDams.wait_until_exists()

    print(tableDams.name," created")

# inizialize table for dataStat if not exists
try: 
    
    dataStatTable = dynamodb_res.Table(name='DataStat')
    dataStatTable.table_status
    print("Already Created -> DataStat")

except Exception:
    
    dataStatTable  = dynamodb_res.create_table(
        TableName='DataStat',
        KeySchema=[
            {
                'AttributeName': 'code',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'region',
                'KeyType': 'range'
            }
            
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'code',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'region',
                'AttributeType': 'S'
            },


        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    
    #check if tables are ready 
    dataStatTable.wait_until_exists()
    
    print(dataStatTable.name," created")


#load data from json file  
with open('asset/data.json', 'r') as f:
  data : dict = json.load(f)

#put data in dynamoDB Table
for region in data['Regions'] :
    region["region_name"] = region['region_name'].replace(" ","") 
    tableRegions.put_item(Item=region)

for sensor in data['Sensors'] : 
    tableSensors.put_item(Item=sensor)

for dam in data['Dams'] : 
    tableDams.put_item(Item=dam)

#check loaded data
datas  = tableRegions.scan()
print("Table Regions populated with :",datas["Count"], " items\n")

datas = tableSensors.scan()
print("Table Sensors populated with :",datas["Count"], " items\n")

datas = tableDams.scan()
print("Table Dams populated with :",datas["Count"], " items\n")

