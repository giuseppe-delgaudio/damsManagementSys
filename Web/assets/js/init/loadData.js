

async function loadData(){

    result = await fetch('http://0fe76a581bda761549a997521c9a3f78.lambda-url.us-east-1.localhost.localstack.cloud:4566/', {
      method: 'get', 
      mode: 'no-cors',
      referrerPolicy: 'no-referrer',
    });
    json = await result.json();

    return json;
};
   
