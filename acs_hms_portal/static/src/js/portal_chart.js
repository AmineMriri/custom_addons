$(document).ready(function () {  
    var PatientPortalData = $("input[name='patient_portal_line_graph']").val();

    if (PatientPortalData){
        ACSPatientChartData = JSON.parse(PatientPortalData);
        new Chart(document.getElementById("ACSPatientLineChart"), {
            type: 'line',
            data: ACSPatientChartData,
            options: {
              scales: {
                xAxes: [{
                    ticks: {
                        autoSkip: false,
                        maxRotation: 45,
                        minRotation: 45,
                    }
                }]
              }
            }
        });

    }
});