import snmpmanagement_v2




h1 = snmpmanagement_v2.Swarco('10.179.58.233')





print(f'h1: {h1.get_stage()}')



print(h1.__dict__)