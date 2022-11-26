( function ( $ ) {
    "use strict";

    
    //line chart
    loadData().then(
        function(data){
            drawCharts(data["dataGraph"]); 
        }
    ); 

    function drawCharts(data){

        for ( let region in data ){

            let ctx = $("#"+region);
            ctx.height = 150;

            let myChart = new Chart( ctx, {
                type: 'line',
                data: {
                    labels: data[region].label,
                    datasets: [
                        {
                            label: "Consumption",
                            borderColor: "rgba(255, 0, 0, 0.8)",
                            borderWidth: "1",
                            backgroundColor: "rgba(255, 0, 0, 0.4)",
                            data: data[region].consumption
                                    },
                        {
                            label: "Production",
                            borderColor: "rgba(0, 194, 146, 0.9)",
                            borderWidth: "1",
                            backgroundColor: "rgba(0, 194, 146, 0.5)",
                            pointHighlightStroke: "rgba(26,179,148,1)",
                            data: data[region].production
                                    }
                                ]
                },
                options: {
                    responsive: true,
                    tooltips: {
                        mode: 'index',
                        intersect: false
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true
                    }
        
                }
            } );
            

        };


    };



} )( jQuery );