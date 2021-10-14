#!/usr/bin/python3
"""
Скрипт для автоматизации форматирования дисков в GPT
1) Сделать автоматизация форматирования
2) Добавить звуковое сопровождение с помощью speaker, для слепого форматирования.
    ИСТОЧНИК Для работы со speaker server: http://www.it-simple.ru/?p=13866
    sudo apt-get install beep # Устанавливаем пакет beep для работы со speaker.
    sudo modprobe pcspkr # Загружаем модуль ядра pcspkr - Это драйвер speaker.
    beep # Проверка звука - должен быть короткий писк.
    beep -f 196 -l 400 -n -f 262 -l 800 -n -f 196 -l 600 -n -f 220 -l 200 # Ещё раз проверяем уже слышим музычку.
    beep -f 500 -l 100 -r 2 -d 100 # Ещё разик - два писка.
        -f — частота, от 0 до 20 000 герц
        -l — длительность, в миллисекундах
        -r — по умолчанию 1
        -d — пауза/тишина в миллисекундах
        -n — новый писк
    sudo rmmod pcspkr # Выгружаем модуль(драйвер), чтобы не занимать 8 КБ оперативы.
    sudo apt-get remove beep # Команда для удаления пакета beep
3) Контроль форматирования:
    sys.args[1] = "0" ПО УМОЛЧАНИЮ. Неуправляемое форматирование.
    sys.args[1] = "1" Неуправляемое форматирование без звука.
    sys.args[1] = "2" Управляемое форматирование.
    sys.args[1] = "3" Управляемое форматирование без звука.

3) Контроль постоянного мониторинга дисков:
    Указывается только вместе с контролем форматирования!
    sys.args[2] = "0" ПО УМОЛЧАНИЮ. Вечный цикл.
    sys.args[2] = "1" Один проход.
"""

import os
import sys
import time
import pexpect  # pexpect Модуль для работы с дочерними процессами. Аналог expect в Unix.

VARIABLE = "GPT FORMATTER v1.2"


def fun_beep(freq_hz=0, len_ms=0, end_beep=False):
    if sys.argv[1] not in ["1", "3"]:  # Условие для отключения звука
        if end_beep:
            os.system("beep -f 2000 -l 100 -r 3 -d 100") # КОНЕЦ ФОРМАТИРОВАНИЯ ЗВУКОВОЙ СИГНАЛ
        else:
            os.system("beep -f {} -l {}".format(freq_hz, len_ms))  # ЗВУКОВОЙ СИГНАЛ
        time.sleep(1)


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
                      "/dev/sda" not in el and "/dev/sdb" not in el]

    # Логирование
    print(VARIABLE)
    if len(find_disk_list) == 0:
        print("\n***************\nDisk not found\n***************\n")
        return find_disk_list

    for i_disk in range(len(find_disk_list)):
        print("\n*******************************************************")
        if result == 0:
            fun_beep(500, 100)  # ЗВУКОВОЙ СИГНАЛ
            print("Disk found {} INDEX-{}\n".format(find_disk_list[i_disk], i_disk))
        else:
            fun_beep(1111, 1111)  # ЗВУКОВОЙ СИГНАЛ
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


def fun_formatting():
    # Вызов функции команды fdisk -l
    disk_list = fun_fdisk_l()

    # Условие для прекращения функции
    if len(disk_list) == 0:
        return

    if sys.argv[1] not in ["0", "1"]:  # Условие для контроля
        # Выбираем диск из найденного для дальнейшего форматирования
        i_gpt_disk = input("\nHow index disk format in GPT? (0): ")
        if i_gpt_disk == "":
            gpt_disk = disk_list[0]
        else:
            gpt_disk = disk_list[int(i_gpt_disk.strip())]
    else:
        gpt_disk = disk_list[0]

    print("*******************************************************")
    print("Disk {} will be format in GTP".format(gpt_disk))

    # Подтверждение
    if sys.argv[1] not in ["0", "1"]:  # Условие для контроля
        go_format_gpt = input("\nGo format in GPT? (Yes/no): ")
        if go_format_gpt == "no":
            exit()

    # Создаём объект с командой gdisk /dev/sd*
    fun_beep(600, 100)  # ЗВУКОВОЙ СИГНАЛ
    cmd_gdisk = pexpect.spawn("gdisk {}".format(gpt_disk))
    print("\nGo command - gdisk {}\n".format(gpt_disk))

    # Удаляем все разделы на диске
    fun_beep(700, 100)  # ЗВУКОВОЙ СИГНАЛ
    cmd_gdisk.sendline("d")
    cmd_gdisk_partition = 1  # Маркер разделов диска
    # Переменной part_marker присваивается индекс совпадающего слова
    part_marker = cmd_gdisk.expect(["Command", "Partition"], timeout=2)
    # Цикл для удаления n-ого количества разделов на диске
    while True:
        if part_marker == 1:
            fun_beep(700, 50)  # ЗВУКОВОЙ СИГНАЛ
            cmd_gdisk.sendline(str(cmd_gdisk_partition))
            print("Delete {} partition".format(cmd_gdisk_partition))
            cmd_gdisk_partition += 1
            # Обновляем параметр part_marker
            # Переменной part_marker присваивается индекс совпадающего слова
            part_marker = cmd_gdisk.expect(["Command", "Partition"], timeout=2)
        else:
            # Здесь выполнилась команда из условия if, т.е. её код = 1.

            fun_beep(700, 100)  # ЗВУКОВОЙ СИГНАЛ
            print("All partitions deleted!\n")
            break
            # Следующая команда должна быть cmd_gdisk.sendline, так как
            # предыдущая было cmd_gdisk.expect("Command").

    # Форматируем диск в GPT
    fun_beep(800, 100)  # ЗВУКОВОЙ СИГНАЛ
    cmd_gdisk.sendline("o")
    print("Format to GPT")
    cmd_gdisk.expect("Proceed?")
    cmd_gdisk.sendline("Y")
    print("DONE Format to GPT\n")

    # Записываем результат
    fun_beep(900, 100)  # ЗВУКОВОЙ СИГНАЛ
    cmd_gdisk.expect("Command")
    cmd_gdisk.sendline("w")
    print("Write format")
    cmd_gdisk.expect("Do")
    cmd_gdisk.sendline("Y")
    print("DONE write format\n")

    # Завершение действий
    fun_beep(1000, 100)  # ЗВУКОВОЙ СИГНАЛ
    print("Disk {} formatted in GTP".format(gpt_disk))
    print("*******************************************************")

    # Проверяем результат
    fun_fdisk_l(1)

    fun_beep(end_beep=True)
    time.sleep(10)


# Условие для установки без контрольного звукового режима
if len(sys.argv) == 1:
    sys.argv.append("0")  # Установка режима контроля
    sys.argv.append("0")  # Установка режима цикла
elif len(sys.argv) == 2:
    sys.argv.append("0")  # Установка режима цикла

if sys.argv[2] == "0":
    while True:
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print("NON STOP " * 5)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        fun_formatting()
        fun_beep(end_beep=True)
        time.sleep(1)
else:
    fun_formatting()
