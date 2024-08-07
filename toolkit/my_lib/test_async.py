import asyncio

from toolkit.my_lib import snmpmanagement_acync

async def test():
    print('Всё')

async def main(inner):
    print(inner)
    host1 = snmpmanagement_acync.Swarco('10.179.75.153', )
    # host2 = snmpmanagement_acync.Swarco('10.179.58.145')
    # host3 = snmpmanagement_acync.Swarco('10.179.69.9')

    # asyncio.create_task(host1.get_stage())
    # asyncio.create_task(host2.get_stage())
    # asyncio.create_task(host3.get_stage())

    values = await asyncio.gather(asyncio.create_task(host1.get_test()),
                                  # asyncio.create_task(host2.get_stage()),
                                  # asyncio.create_task(host3.get_stage())
    )

    print(values)
    await asyncio.create_task(test())
    return 'maaaain'

a = asyncio.run(main({1:'121', 2: '323232'}))

print(a)# if __name__ == 'main':


