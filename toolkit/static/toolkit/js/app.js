'use strict';
//alert("Not checked");

//$("#getdatahost_1").on("click", function (){
//if (getdatahost_1.checked){
//setTimeout(get_data, 2000);
//
//}
//
//}  
//)

let intervalID = [false, false, false, false]

// Отслеживаем нажатие чекбокса, который отвечает за постоянный запрос данных с дк по snmp
$("#getdatahost_1").change(function() {
    console.log(intervalID)

    const num_host = "#getdatahost_1".split('_')[1]
    console.log(`num_host = ${num_host}`)

    if (getdatahost_1.checked && !intervalID[0]){
        let id_getData = setInterval(getData, 4000, num_host);
        intervalID[0] = id_getData;

    console.log('if');

    }
    else{
        clearInterval(intervalID[0])
        intervalID[0] = false;
    console.log('else');
    document.getElementById(`datahost_${num_host}`).textContent="--";

    }
    console.log(intervalID)
    }

)


// Отслеживаем нажатие чекбокса, который отвечает за постоянный запрос данных с дк по snmp У хоста 2
$("#getdatahost_2").change(function() {
    console.log(intervalID)

    const num_host = "#getdatahost_2".split('_')[1]
    console.log(`num_host = ${num_host}`)

    if (getdatahost_2.checked && !intervalID[1]){
        let id_getData = setInterval(getData, 4000, num_host);
        intervalID[1] = id_getData;

    console.log('if');

    }
    else{
        clearInterval(intervalID[1])
        intervalID[1] = false;
    console.log('else');
    document.getElementById(`datahost_${num_host}`).textContent="--";

    }
    console.log(intervalID)

    }

)



// Функция запроса и получения текущего режима/плана/фазы по snmp
let getData = function (num_host){

    $.ajax({

    type: "GET",
    url: "test_ajax/",
    data:{
        'ip_adress': $('#ip_' + num_host).val(),
        'protocol': $(`#protocol_${num_host} option:selected`).text(),
        },

    dataType: 'text',
    cache: false,
    success: function (data) {
    console.log(data)
    const postStringify = JSON.parse(data)
    console.log(postStringify)
    document.getElementById(`datahost_${num_host}`).textContent=data;
    if (data == 'yes'){
    console.log(data);
    }
    else if (data == 'no'){
    }
        }
    }
);
}





//Функция получения данных при нажатии кнопки
$("#SetToHost_1").click(function (){
    console.log('Tetss');
    $.ajax({

    type: "GET",
    url: "set_snmp_ajax/",
    data:{
        'ip_adress': $('#ip_1').val(),
        'protocol': $("#protocol_1 option:selected").text(),
        },

    dataType: 'text',
    cache: false,
    success: function (data) {
    console.log(data)
    const postStringify = JSON.parse(data)
    console.log(postStringify)

    if (data == 'yes'){
    console.log(data);
    }
    else if (data == 'no'){
    }
        }
    }
);
}
)

// function intUser(a,b) {
//   let i = setInterval(() => {
//     console.log(a++);
//     if (a > b) clearInterval(i);
//   }, 1000)
// }

// intUser(5, 10);



