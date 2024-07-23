
//alert("Not checked");


$("#SetToHost_1").click(function (){

    $.ajax({

    type: "GET",
    url: "test_ajax/",
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
    document.getElementById("datahost_1").textContent=data;
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

function intUser(a,b) {
  let i = setInterval(() => {
    console.log(a++);
    if (a > b) clearInterval(i);
  }, 1000)
}

intUser(5, 10);



