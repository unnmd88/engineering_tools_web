
alert("Not checked");

//function stickyheaddsadaer(obj) {
//  if($(obj).is(":checked")){
//    alert("Yes checked"); //when checked
//    $("#page-header-inner").addClass("sticky");
//  }else{
//    alert("Not checked"); //when not checked
//  }
//
//}

//function intUser(a,b) {
//  let i = setInterval(() => {
//    console.log(a++);
//    if (a > b) clearInterval(i);
//  }, 1000)
//}
//
//intUser(5, 10);





// script.js function myJavaScriptFunction () { // Ваш код JavaScript здесь }


function callPythonFunction () {
    fetch ( '/my_python_function/' ) . then ( response => response . json ()) . then ( data => {
            console . log ( data . message );}); }