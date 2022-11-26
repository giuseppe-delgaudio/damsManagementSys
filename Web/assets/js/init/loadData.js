

async function loadData(){

    result = await fetch('http://13d797afa95c1f0991f58b4e496d375d.lambda-url.us-east-1.localhost.localstack.cloud:4566/', {
      method: 'get', 
      mode: 'no-cors',
      referrerPolicy: 'no-referrer',
    });
    json = await result.json();

    return json;
};
   
