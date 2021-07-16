#!/usr/bin/python3
"""
Скрипт для автоматизации форматирования дисков в GPT
1) Сделать автоматизация форматирования
2) Добавить звуковое соправождение с помощью speaker, для слепого форматирования
"""

# pexpect Модуль для работы с дочерними процесами. Аналог expect в Unix.
import pexpect

# Создаём объект с командой fdisk -l
cmd_fdisk_l = pexpect.spawn("fdisk -l")
# Вызов объекта cmd_fdisk_l и ожидание окончания его вывода для появления атрибута .before
cmd_fdisk_l.expect(pexpect.EOF)

# Преобразование атрибута .before в кодировку utf-8
#cmd_fdisk_l_stdout = cmd_fdisk_l.before.decode("utf-8")
#print(cmd_fdisk_l_stdout.split("\n"))

#'''
# Имитация команда fdisk -l
with open("road_fdisk_l", "r") as road_fdisk_l:
    cmd_fdisk_l_stdout = road_fdisk_l.read()
    road_fdisk_l.close()

#print(cmd_fdisk_l_stdout)
#'''

# Ищем последний подключенный диск. a и b диски не трогать - это raid1.
activ_disk_list = [el[:-1] for el in cmd_fdisk_l_stdout.split() if "/dev/sd" in el and
                   not "/dev/sda" in el and not "/dev/sdb" in el]



# Логирование
if len(activ_disk_list) == 0:
    print("\n***************\nDisk not found\n***************\n")
    exit()

for i_disk in range(len(activ_disk_list)):
    print("\n*******************************************************")
    print("Disk found {} INDEX-{}\n".format(activ_disk_list[i_disk],i_disk))

    for i_search_info_disk in range(len(cmd_fdisk_l_stdout.split("\n"))):
        if activ_disk_list[i_disk] in cmd_fdisk_l_stdout.split("\n")[i_search_info_disk]:
            for i_info_disk in range(6):  # Выводим инфу о найденном диске
                try:
                    print(cmd_fdisk_l_stdout.split("\n")[i_search_info_disk + i_info_disk].strip())
                except IndexError:
                    pass
    print("*******************************************************")

# Выьераем диск из найденого для дальнейшего форматирования
i_gpt_disk = input("\nHow index disk format in GPT? (0): ")
if i_gpt_disk == "":
    gpt_disk = activ_disk_list[0]
else:
    gpt_disk = activ_disk_list[int(i_gpt_disk.strip())]

print("*************************************")
print("Disk {} will be format in GTP".format(gpt_disk))
print("*************************************")

# Подтверждение
go_format_gpt = input("\nGo format in GPT? (Yes/no): ")
if go_format_gpt == "no":
    exit()
print("GPT___" * 8)

