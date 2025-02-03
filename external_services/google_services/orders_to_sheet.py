import gspread


from .upload_image_to_drive import get_image_url

sheet_name = "Заявки на гибку"
gc = gspread.service_account(filename='cinkoff-store-397509-6699dd9ae142.json')
sh = gc.open(sheet_name)
worksheet = sh.worksheet('test_list')


# Находим пустую строку для записи
def find_empty_row() -> int|None:
    ls = worksheet.get("B1:G100", maintain_size=True)
    for number, row in enumerate(ls,1):
        if not any(row):
            return number
    return None

    #for i in ls:
    #    print(*i)
    # print(empty_row)
    worksheet.update([["It works!!!"]], f'B{empty_row}')

# Не очень удачная реализация, переделать в дальнейшем!
# Мы работаем со списком, в который в процессе работы могут быть добавлены новые заказы
# Что приведет к их потере

def add_orders_to_sheet(orders: list[dict]) -> bool:
    print(orders, type(orders), sep='-----\n')
    try:
        data_to_sheet = []
        for order in orders:
            print('\n\n', order, '\n---\n')
            temp_ls = ["01.01.05",
                        order['nomer_1C'],
                        '--',
                        order['desired_date_complete'],
                        order['draw_link'],
                        order['description']
                    ]
            data_to_sheet.append(temp_ls)
            print(data_to_sheet)
        empty_row = find_empty_row()
        print(empty_row)
        worksheet.update(data_to_sheet, f'B{empty_row}:G{len(data_to_sheet) + empty_row}')
        print("-------------- Данные записаны в таблицу ------------")
        return True

    except Exception as e:
        print(e)
        print('Ошибка при загрузки данных в таблицу')
        raise e
