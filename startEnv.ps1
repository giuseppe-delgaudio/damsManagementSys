

#start localstack container
$localstack = docker start localstack
if ( $localstack -ne "localstack" ){
    
    Write-Output "localstack container dosen't exist, creating one"
    docker run -p 4566:4566 -p 4510-4559:4510-4559 -d   --name localstack localstack/localstack
    Write-Output "localstack created"
}
Write-Output "localstack started"

#start ngnix container
$nginx = docker start nginx
if ( $nginx -ne "nginx" ){
    
    Write-Output "nginx container dosen't exist, creating one"
    docker run --name nginx -v {Get-Location}\damsSys\Web:/usr/share/nginx/html:ro -d -p 8080:80 nginx:stable-alpine
    Write-Output "nginx created"
}
Write-Output "nginx started"

git clone https://github.com/giuseppe-delgaudio/damsManagementSys damsSys

python -m venv ./.venv 

#Prepare python enviroment 
If ($OsType -ne "Linux")
{    
    .\.venv\Scripts\activate
}Else{

    .\.venv\bin\activate

}

pip install -r requirements.txt

#Initialize aws enviroment
python inizializeDb.py
python inizializeQueue.py

Write-Output "environment initialized"

#Define policy to lambda
$lambdaRole = aws iam create-role --role-name lambdarole --assume-role-policy-document file://policy/role_policy.json --query 'Role.Arn' --output json --endpoint-url=http://localhost:4566 | ConvertFrom-Json
aws iam put-role-policy --role-name lambdarole --policy-name lambdapolicy --policy-document file://policy/policy.json --endpoint-url=http://localhost:4566

#Create lambda function dataConverter and lambdaDams zip archive
Compress-Archive  -Update dataConverter.py dataConverter.zip
Compress-Archive  -Update lambdaDams.py lambdaDams.zip

#Create lambda functions
aws lambda create-function --function-name dataConverter --zip-file fileb://dataConverter.zip --handler dataConverter.lambda_handler --runtime python3.6 --role $lambdaRole --endpoint-url=http://localhost:4566
$lambdaDams = aws lambda create-function --function-name lambdaDams --zip-file fileb://lambdaDams.zip --handler lambdaDams.lambda_handler --runtime python3.6 --role $lambdaRole --output json --endpoint-url=http://localhost:4566 | ConvertFrom-Json

#Create for lambda function dataConverter url configuration and update link on js file
$lambdaDataConverter = aws lambda create-function-url-config --function-name dataConverter --auth-type NONE --cors AllowCredentials=true,AllowMethods=*,AllowOrigins=*,AllowHeaders=*,MaxAge=600,ExposeHeaders=* --output json   --endpoint-url=http://localhost:4566 | ConvertFrom-Json
$loadFunction = Get-Content -path .\Web\assets\js\init\loadData.js

$lambdaDataConverter = aws lambda get-function-url-config --function-name dataConverter  --output json   --endpoint-url=http://localhost:4566 | ConvertFrom-Json
$lambdaFunctionUrl = $lambdaDataConverter.FunctionUrl
($loadFunction -replace "'http://(.*)/'" ,  "'$lambdaFunctionUrl'" )  | Set-Content -path .\Web\assets\js\init\loadData.js 

#Refresh lambda functions 
aws lambda update-function-code --function-name lambdaDams --zip-file fileb://lambdaDams.zip --endpoint-url=http://localhost:4566

$rule = aws events put-rule --name damsRoutine --schedule-expression 'rate(1 minutes)' --output json --endpoint-url=http://localhost:4566 | ConvertFrom-Json
aws events list-rules --endpoint-url=http://localhost:4566
aws lambda add-permission --function-name lambdaDams --statement-id actionRoutine --action 'lambda:InvokeFunction' --principal events.amazonaws.com --source-arn $rule.RuleArn --endpoint-url=http://localhost:4566

$target = '[{"Id":"1","Arn":"'+ $lambdaDams.FunctionArn + '"}]'
Set-Content -Path ./asset/target.json -Value $target

aws events put-targets --rule damsRoutine --targets file://asset/target.json   --endpoint-url=http://localhost:4566

Write-Output "Start emulation"

#Start data generation
python .\startEmulation.py

Start-Sleep -Seconds 5

aws lambda invoke --function-name lambdaDams lambdaDams.txt --endpoint-url http://localhost:4566
aws lambda update-function-code --function-name dataConverter --zip-file fileb://dataConverter.zip --endpoint-url=http://localhost:4566
aws lambda update-function-code --function-name lambdaDams --zip-file fileb://lambdaDams.zip --endpoint-url=http://localhost:4566


