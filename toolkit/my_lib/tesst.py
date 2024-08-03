
from datetime import datetime as dt
from io import BytesIO

time_now = dt.now().strftime('%d %b %Y %H_%M_%S')
def reverse_slashes(path):
    path = path.replace('\\', '/')
    return path
# str_time_now = time_now.strftime('%d %b %Y %H_%M_%S')

print(f'str_time_now: {time_now}')

str1 = 'C:\Programms\py.projects\django_engineering_toolkit\engineering_tools\media\conflicts\configs/New_stripes_67_pokrovskie_vorotl_pokrovka_17_va_ot_2022_12_31_xx_Wlh2KWQ.PTC2'

str1 = reverse_slashes(str1)

print(str1 .split('media/'))
