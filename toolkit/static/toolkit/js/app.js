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

let intervalID = [false, false, false, false, false, false, false, false, false]

const chkbx = [getdatahost_1, getdatahost_2, getdatahost_3, getdatahost_4, getdatahost_5,
    getdatahost_6, getdatahost_7, getdatahost_8, getdatahost_9
]


// Отслеживаем нажатие чекбокса, который отвечает за постоянный запрос данных с дк по snmp у хоста 1
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


// Отслеживаем нажатие чекбокса, который отвечает за постоянный запрос данных с дк по snmp уу хоста 2
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




// Создаем функции на изменения чекбокс внутри каждого хоста
for (let i=1; i < 11; i++) {
    console.log(`Это i: ${i}`)
    $(`#getdatahost_${i}`).change(function() {
        console.log(intervalID)
    
        console.log(`num_host = ${i}`)
    
        if (chkbx[i-1].checked && !intervalID[i]){
            let id_getData = setInterval(getData, 4000, i);
            intervalID[i] = id_getData;
    
        console.log('if');
    
        }
        else{
            clearInterval(intervalID[i])
            intervalID[i] = false;
        console.log('else');
        document.getElementById(`datahost_${i}`).textContent="--";
    
        }
        console.log(intervalID)
    
        }
    
    )
}



// Клик на #display_hosts_snmp -> Отображение количества хостов
$("#display_hosts_snmp").click( function() {
    show_hide_hosts_snmp();
    } 
)

// Функция отображения количества хостов
const show_hide_hosts_snmp = function () {
    console.log('ssssss')
    const select_visible_hosts = document.querySelector('#visible_hosts');
    const num_hosts_to_view = select_visible_hosts.value;
    console.log(`num_hosts_to_view -> ${num_hosts_to_view}`);

    for (let i=1; i < 10; i++) {
        if(i <= num_hosts_to_view) {
            $(`#table_${i}`).show();
        }
        else {
            $(`#table_${i}`).hide();
        }
        }
}

$(`#table_1`).show();










// Функция запроса и получения текущего режима/плана/фазы по snmp
let getData = function (num_host){

    console.log(num_host);
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


