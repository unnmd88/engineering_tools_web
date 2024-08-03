

class ProcessingDataConflicts:
    upload_name_id = 'upload_config_file'
    name_textarea = 'table_stages'
    def __init__(self, request):
        self.request = request
        self.py_dict = request.POST.dict()
        self.files_dict = request.FILES.dict()
        self.file = request.FILES.get(self.upload_name_id)
        self.filename = self.file.name



    @staticmethod
    def make_id(filename: str) -> int:
        """"
        Метод определяет какой номер 'id'(группа) присвоить для записи в модель UploadFiles2
        id_for_db = 1 -> конфиг swarco
        id_for_db = 2 -> конфиг peek
        id_for_db = 3 -> txt файл
        id_for_db = 3 -> отсальные расширения
        :arg filename -> название файла
        :return id_for_db -> номер id
        """
        file_ext = filename[-4:].lower()
        if file_ext == 'ptc2':
            id_for_db = 1
        elif file_ext == '.dat':
            id_for_db = 2
        elif file_ext == '.txt':
            id_for_db = 3
        else:
            id_for_db = 4
        return id_for_db


        file = request.FILES.get(upload_name_id)
        filename = file.name
        print(f'request.FILES: {filename}')
        print(f'request.FILES: {type(filename)}')
        id_for_db = Common.make_id(filename)
        # fp = UploadFiles2(file=file, group=id_for_db, status_file='source')
        # fp.save()
        obj = UploadFiles2(file=file, group=id_for_db, status_file='source')

