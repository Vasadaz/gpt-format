#!/usr/bin/python3
"""
Скрипт для автоматизации форматирования дисков в GPT
1) Сделать автоматизация форматирования
2) Добавить звуковое соправождение с помощью speaker, для слепого форматирования.
    ИСТОЧНИК Для работы со speeker server: http://www.it-simple.ru/?p=13866
    sudo apt-get install beep # Устанавливаем пакет beep для работы со speeker.
    sudo modprobe pcspkr # Загружаем модуль ядра pcspkr - Это драйвер speeker.
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
    sys.args[1] = "0" ПО УМОЛЧАНИЮ.Безконтрольное форматирование
    sys.args[1] = "1" контрольное форматирование
    sys.args[1] = "2" контрольное форматирование без звука.

3) Контроль постояного мониторинга дисков:
    Указывается только вместее с контролем форматирования!
    sys.args[2] = "0" ПО УМОЛЧАНИЮ.Безконтрольное форматирование
    sys.args[2] = "1" вечный цикл
"""

import os
import sys
import time
import pexpect  # pexpect Модуль для работы с дочерними процесами. Аналог expect в Unix.


def fun_beep(freq_hz: int, len_ms: int):
    if sys.argv[1] != "2":  # Условие для отключения звука
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

    if sys.argv[1] != "0":  # Условие для контроля
        # Выбираем диск из найденого для дальнейшего форматирования
        i_gpt_disk = input("\nHow index disk format in GPT? (0): ")
        if i_gpt_disk == "":
            gpt_disk = disk_list[0]
        else:
            gpt_disk = disk_list[int(i_gpt_disk.strip())]
    else:
        gpt_disk = disk_list[0]

    print("*************************************")
    print("Disk {} will be format in GTP".format(gpt_disk))

    # Подтверждение
    if sys.argv[1] != "0":  # Условие для контроля
        go_format_gpt = input("\nGo format in GPT? (Yes/no): ")
        if go_format_gpt == "no":
            exit()

    # Создаём объект с командой gdisk /dev/sd*
    fun_beep(600, 100)  # ЗВУКОВОЙ СИГНАЛ
    cmd_gdisk = pexpect.spawn("gdisk {}".format(gpt_disk))
    print("\nGo command - gdisk {}\n".format(gpt_disk))

    # Удаляем все разделы на диске
    fun_beep(700, 100)  # ЗВУКОВОЙ СИГНАЛ
    cmd_gdisk.expect("Command")
    cmd_gdisk.sendline("d")
    cmd_gdisk_partition = 1  # Маркер разделов диска
    # Цикл для удаления n-ого количесивка разделов на диске
    while True:
        if cmd_gdisk.expect("Command") != 0:
            fun_beep(700, 50)  # ЗВУКОВОЙ СИГНАЛ
            cmd_gdisk.sendline(str(cmd_gdisk_partition))
            print("Delete {} partition".format(cmd_gdisk_partition))
            cmd_gdisk_partition += 1
        else:
            # Здесь выполнилась команда из условия if, т.е. её код = 1.
            # Следующая команда должна быть expect.sendline
            fun_beep(700, 100)  # ЗВУКОВОЙ СИГНАЛ
            print("All partitions deleted!\n")
            break

    # Форматируем диск в GPT
    fun_beep(800, 100)  # ЗВУКОВОЙ СИГНАЛ
    # cmd_gdisk.expect("Command")
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
    print("Disk {} formated in GTP".format(gpt_disk))
    print("*************************************")

    # Проверяем результат
    fun_fdisk_l(1)


# Условие для установки безконтрольного звукового режима
if len(sys.argv) == 1:
    sys.argv.append("0")  # Установка режима контроля
    sys.argv.append("0")  # Установка режима цикла
elif len(sys.argv) == 2:
    sys.argv.append("0")  # Установка режима цикла

if sys.argv[2] != "0":
    while True:
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print("NON STOP " * 5)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        fun_formatting()
        os.system("beep -f 5000 -l 100 -r 3 -d 100")
        time.sleep(5)

else:
    fun_formatting()
