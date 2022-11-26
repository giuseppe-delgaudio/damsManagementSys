
(function($){

var map;
const    damIcon = {

    url : 'https://cdn-icons-png.flaticon.com/512/3574/3574309.png',
    scaledSize: new google.maps.Size(50, 50), // scaled size
    origin: new google.maps.Point(0,0), // origin
    anchor: new google.maps.Point(0, 0) // anchor
};
const    panelIcon = {

    url : 'https://cdn-icons-png.flaticon.com/512/861/861111.png',
    scaledSize: new google.maps.Size(50, 50), // scaled size
    origin: new google.maps.Point(0,0), // origin
    anchor: new google.maps.Point(0, 0) // anchor
};
const    gridIcon = {

  url : 'https://cdn-icons-png.flaticon.com/512/5359/5359025.png',
  scaledSize: new google.maps.Size(50, 50), // scaled size
  origin: new google.maps.Point(0,0), // origin
  anchor: new google.maps.Point(0, 0) // anchor
};

$(document).ready(function(){
    
  map = new GMaps({
        el: '#map',
        zoom: 5.1,
        lat: 41.17329,
        lng: 12.31250
    });

    showData();




});

function showData(){
  
  loadData().then(
    function(data){
      let dams = [];
      let sensors = [];
      let stat = new Array();   

      for( i in data["dams"] ){
  
        //Populate dams array 
        dams[i] = {lat : data["dams"][i].latitude,
                      lng : data["dams"][i].longitude,
                      title :data["dams"][i].name,
                      icon : damIcon,
                      infoWindow : {
                        content : data["dams"][i].infoPage
                      }}
  
  
      }; 
    
      sensors = [];

      for (i in data["sensors"]){
        let icon; 
        
        if(data["sensors"][i].type == "producer") icon = panelIcon;
        else icon =  gridIcon; 
        
        sensors[i] = {lat : data["sensors"][i].latitude,
          lng : data["sensors"][i].longitude,
          title :data["sensors"][i].name,
          icon : icon,
          infoWindow : {
            content : data["sensors"][i].infoPage
          }}

      };

      //Populate region charts 
      for( i in data["dataGraph"] ){
  
        
        stat.push({   region : i,
                      avgProduction : data["dataGraph"][i].avgProduction,
                      avgConsumption :data["dataGraph"][i].avgConsumption,
                      time : data["dataGraph"][i].time
                      });
      };
  


      map.addMarkers(dams);
      map.addMarkers(dams);
      map.addMarkers(dams);
      map.addMarkers(sensors);
      map.addMarkers(sensors);
      map.addMarkers(sensors);


      $('#regionAllStatTable').DataTable( {
        data : stat,
        
        columns: [
            { data : 'region' },
            { data: 'avgProduction' },
            { data: 'avgConsumption' },
            { data: 'time' } 
        ]
      } );
      
      $('#sensorsListTable').DataTable( {
        data : data["dataSensor"],
        
        columns: [
            { data : 'region' },
            { data: 'sensor_id' },
            { data: 'type' },
            { data: 'value' } 
        ]
      } );

      $('#damsListTable').DataTable( {
        data : data["dataDams"],
        
        columns: [
            { data : 'region' },
            { data: 'name' },
            { data: 'production' },
            { data: 'pump' },
            { data: 'valve' },
            { data: 'level' } 
        ]
      } );
     
    }
  ); 
}

})(jQuery);

