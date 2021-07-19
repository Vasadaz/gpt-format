#!/usr/bin/python3
"""
Скрипт для автоматизации форматирования дисков в GPT
1) Сделать автоматизация форматирования
2) Добавить звуковое соправождение с помощью speaker, для слепого форматирования
"""

# pexpect Модуль для работы с дочерними процесами. Аналог expect в Unix.
import pexpect


# Функция для команды fdisk -l
def fun_fdisk_l(result=0):
    # Создаём объект с командой fdisk -l
    cmd_fdisk_l = pexpect.spawn("fdisk -l")
    # Вызов объекта cmd_fdisk_l и ожидание окончания его вывода для появления атрибута .before
    cmd_fdisk_l.expect(pexpect.EOF)

    # Преобразование атрибута .before в кодировку utf-8
    cmd_fdisk_l_stdout = cmd_fdisk_l.before.decode("utf-8")
    # print(cmd_fdisk_l_stdout.split("\n"))

    # Ищем последний подключенный диск. a и b диски не трогать - это raid1.
    find_disk_list = [el[:-1] for el in cmd_fdisk_l_stdout.split() if "/dev/sd" in el and
                      not "/dev/sda" in el and not "/dev/sdb" in el]

    # Логирование
    if len(find_disk_list) == 0:
        print("\n***************\nDisk not found\n***************\n")
        exit()

    for i_disk in range(len(find_disk_list)):
        print("\n*******************************************************")
        if result == 0:
            print("Disk found {} INDEX-{}\n".format(find_disk_list[i_disk], i_disk))
        else:
            print("FORMATTING RESULT\n")

        for i_search_info_disk in range(len(cmd_fdisk_l_stdout.split("\n"))):
            if find_disk_list[i_disk] in cmd_fdisk_l_stdout.split("\n")[i_search_info_disk]:
                for i_info_disk in range(6):  # Выводим инфу о найденном диске
                    try:
                        print(cmd_fdisk_l_stdout.split("\n")[i_search_info_disk + i_info_disk].strip())
                    except IndexError:
                        pass
        print("*******************************************************")
    return find_disk_list  # Возвращаем список найденных дисков


# Вызов функции команды fdisk -l
disk_list = fun_fdisk_l()

# Выбираем диск из найденого для дальнейшего форматирования
i_gpt_disk = input("\nHow index disk format in GPT? (0): ")
if i_gpt_disk == "":
    gpt_disk = disk_list[0]
else:
    gpt_disk = disk_list[int(i_gpt_disk.strip())]

print("*************************************")
print("Disk {} will be format in GTP".format(gpt_disk))

# Подтверждение
go_format_gpt = input("\nGo format in GPT? (Yes/no): ")
if go_format_gpt == "no":
    exit()

# Создаём объект с командой gdisk /dev/sd*
cmd_gdisk = pexpect.spawn("gdisk {}".format(gpt_disk))
print("\nGo command - gdisk {}\n".format(gpt_disk))

# Удаляем все разделы на диске
cmd_gdisk.expect("Command")
cmd_gdisk.sendline("d")
cmd_gdisk_partition = 1  # Маркер разделов диска
# Цикл для удаления n-ого количесивка разделов на диске
while True:
    if cmd_gdisk.expect("Command") != 0:
        cmd_gdisk.sendline(str(cmd_gdisk_partition))
        print("Delete {} partition".format(cmd_gdisk_partition))
        cmd_gdisk_partition += 1
    else:
        # Здесь выполнилась команда из условия if, т.е. её код = 1.
        # Следующая команда должна быть expect.sedline
        print("All partitions deleted!\n")
        break

# Форматируем диск в GPT
# cmd_gdisk.expect("Command")
cmd_gdisk.sendline("o")
print("Format to GPT")
cmd_gdisk.expect("Proceed?")
cmd_gdisk.sendline("Y")
print("DONE Format to GPT\n")

# Записываем результат
cmd_gdisk.expect("Command")
cmd_gdisk.sendline("w")
print("Write format")
cmd_gdisk.expect("Do")
cmd_gdisk.sendline("Y")
print("DONE write format\n")

print("Disk {} formated in GTP".format(gpt_disk))
print("*************************************")

# Проверяем результат
fun_fdisk_l(1)
