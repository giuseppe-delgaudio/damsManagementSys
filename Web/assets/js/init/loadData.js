

async function loadData(){

    result = await fetch('http://fe4ef6014fd9a1913764802c259d706a.lambda-url.us-east-1.localhost.localstack.cloud:4566/', {
      method: 'get', 
      mode: 'no-cors',
      referrerPolicy: 'no-referrer',
    });
    json = await result.json();

    return json;
};
   
