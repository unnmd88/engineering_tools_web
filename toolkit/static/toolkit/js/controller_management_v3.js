'use strict';



// --------------GET REQUEST SNMP------------------
// Отслеживаем нажатие чекбокса, который отвечает за постоянный запрос данных с дк по snmp у хоста 1

// Создаем функции на изменения чекбокс внутри каждого хоста
// for (let i=1; i < 11; i++) {
//     console.log(`Это i: ${i}`)
//     $(`#getdatahost_${i}`).change(function() {
//         console.log(intervalID)
    
//         console.log(`num_host = ${i}`)
    
//         if (chkbx[i-1].checked && !intervalID[i]){
//             let id_getData = setInterval(getData, 4000, i);
//             intervalID[i] = id_getData;
    
//         console.log('if');
    
//         }
//         else{
//             clearInterval(intervalID[i])
//             intervalID[i] = false;
//         console.log('else');
//         document.getElementById(`datahost_${i}`).textContent="--";
    
//         }
//         console.log(intervalID)
    
//         }
    
//     )
// }

// Функция запроса и получения текущего режима/плана/фазы по snmp








// --------------SET REQUEST SNMP------------------
//Функция отправки запроса команды при нажатии кнопки
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

let interval = 4000;
let intervalID_get_data = setInterval(sendReqGetData, interval);

function collect_data_from_hosts (){
    let num_visible_hosts = $(`#visible_hosts`).val();
    let data = {};
    let num_checked_checkbox = $('.receive_data:checked').length;
    console.log(`num_checked_checkbox из collect data ${num_checked_checkbox}`)
    if (num_checked_checkbox > 0) {
        for(let num_host = 1, all_hosts = 0; num_host <= num_visible_hosts; num_host++) {   
            if ($(`#getdatahost_${num_host}`).is(':checked')){
                data[num_host] = `${$('#ip_' + num_host).val()};${$(`#protocol_${num_host} option:selected`).text()};${$(`#scn_${num_host}`).val()}`;
                data.num_hosts_in_request = ++all_hosts;
            }           
        }
    }
         console.log(data);
    return data;
    }

function sendReqGetData () {
    let num_checked_checkbox = $('input:checkbox.receive_data:checked').length;

    console.log(`num_checked_checkbox = ${num_checked_checkbox}`);
    
    if (num_checked_checkbox === 0) {
        console.log(`num_checked_checkbox === 0`);
        return false;
    }       

    console.log('sendReqGetData');
    $.ajax({

    type: "GET",
    url: `get-data-snmp/1/`,
    data: collect_data_from_hosts(),

    dataType: 'text',
    cache: false,
    success: function (data) {
    console.log(data)
    let postStringify = JSON.parse(data);
    console.log(postStringify);

    $.each(postStringify, function(num_host, write_data) {
        $(`#datahost_${num_host}`).text(write_data);
    });

    // $(`#datahost_${num_host}`).text(data);
    // document.getElementById(`datahost_${num_host}`).textContent=data;
    if (data == 'yes'){
    console.log(data);
    }
    else if (data == 'no'){
    }
        }
    }
);
}




// function intUser(a,b) {
//   let i = setInterval(() => {
//     console.log(a++);
//     if (a > b) clearInterval(i);
//   }, 1000)
// }

// intUser(5, 10);




