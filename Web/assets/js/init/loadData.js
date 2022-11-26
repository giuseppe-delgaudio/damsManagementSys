

async function loadData(){

    result = await fetch('http://20d06a4348a8741c530c3c6b100ffcb5.lambda-url.us-east-1.localhost.localstack.cloud:4566/', {
      method: 'get', 
      mode: 'no-cors',
      referrerPolicy: 'no-referrer',
    });
    json = await result.json();

    return json;
};
   
