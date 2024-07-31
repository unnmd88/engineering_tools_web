'use strict';

// Ловим событие изменения состояния radio типов дк
$('input[type=radio][name=controller_type]').change(function() {
  if ($('#undefind').is(':checked')) {
          $('#make_config').prop('checked', false);
          $('#binval_swarco').prop('checked', false);
          $('#binval_swarco').attr('disabled', true);
          $('#make_config').attr('disabled', true);
          $('#config_file').attr('disabled', true);   
  }
  else if ($('#swarco').is(':checked')) {
      $('#binval_swarco').attr('disabled', false);
      $('#make_config').attr('disabled', false);      
  }
  else {
      console.log('else');
      $('#binval_swarco').attr('disabled', true);
      $('#make_config').attr('disabled', false);
      $('#binval_swarco').prop('checked', false);
  }; 
});

// Ловим событие изменения чекбокса Создать файл конфигурации
$('#make_config').change( function() {
  if ($(this).is(':checked')){
    $('#config_file').attr('disabled', false);
  }
  else {
      $('#config_file').attr('disabled', true);
    };
    
});

// При нажатии на кнопку выбор файлов, установим необходимое раширение(для выбранного типа ДК) в браузере
$('#config_file').click( function (){
  if ($('#swarco').is(':checked')) {
    $(this).attr('accept', '.PTC2');
  }
  else if ($('#peek').is(':checked')){
    $(this).attr('accept', '.DAT');
  }

});
