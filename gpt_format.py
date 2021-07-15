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
#print(cmd_fdisk_l_stdout)

#'''
# Имитация команда fdisk -l
with open("road_fdisk_l", "r") as road_fdisk_l:
    cmd_fdisk_l_stdout = road_fdisk_l.readlines()
    road_fdisk_l.close()

#print(cmd_fdisk_l_stdout)
#'''

# Ищем последний подключенный диск. a и b диски не трогать - это raid1.
activ_disk = [el[:-1] for el in str(cmd_fdisk_l_stdout).split() if "/dev/sd" in el and
              not "/dev/sda" in el and not "/dev/sdb" in el]


# Логирование
for el_disk in activ_disk:
    print("*******************************************************")
    print("Disk found")
    print("    |     ")
    print("    V     ")
    print(el_disk, "it info:")

    for i_search_info_disk in range(len(cmd_fdisk_l_stdout)):
        if el_disk in cmd_fdisk_l_stdout[i_search_info_disk]:
            for i_info_disk in range(6):  # Выводим инфу о найденном диске
                print(cmd_fdisk_l_stdout[i_search_info_disk + i_info_disk].strip())
    print()