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


// Проверка валидности введенных/заполненных данных
$("form").submit(function () {
  const text_area = {
    text: $('#stages_from_area').val(),
    lines: $('#stages_from_area').val().split('\n'),
    num_lines: $('#stages_from_area').val().split('\n').length,
  };

  console.log(text_area);
  console.log(text_area.text);
  console.log(text_area.lines);
  console.log(text_area.num_lines);

  if (text_area.num_lines < 2) {
    alert('Количество фаз не может быть менее 2');
    return false;
  }

  if ($('#make_config').is(':checked')) {
    let file_name = $('#config_file')[0].files[0].name;
    console.log(file_name);
    if (!$('#config_file').val()){
      alert('Вы не выбрали файл конфигурации');
      return false;
    }
    else if ($('#swarco').is(':checked') && file_name.slice(-5).toUpperCase() != '.PTC2'){
      alert('Вы выбрали неверный формат файла конфигурации для Swarco');
      return false;
    }
    else if ($('#peek').is(':checked') && file_name.slice(-4).toUpperCase() != '.DAT'){
      alert('Вы выбрали неверный формат файла конфигурации для Peek');
      return false;
    }
  }
  
});


