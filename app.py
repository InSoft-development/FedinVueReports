import gevent.monkey
gevent.monkey.patch_all()

# Патч обезьяны для функционирования импортируемых модулей python асинхронно

import os
import signal
import platform
import argparse

import sys
import time

import shutil

import sqlite3
from gevent import subprocess
import shlex
import itertools

import pandas as pd

import json
from loguru import logger
import datetime
from dateutil.parser import parse

from utils.correct_start import check_correct_application_structure
import utils.constants_and_paths as constants

from jinja.pylib.get_template import render_slice, render_grid

import eel

from io import StringIO

VERSION = '1.0.0'

# Use latest version of Eel from parent directory
sys.path.insert(1, '../../')


@eel.expose
def get_analog_kks():
    """
    Функция возвращает kks аналоговых датчиков из файла data_AM.txt
    :return: массив строк kks аналоговых датчиков
    """
    logger.info(f"get_analog_kks()")

    with open(f'{constants.DATA_ANALOG}', 'r', encoding='utf8') as f:
        analog_kks = f.readlines()

    # Приведение в верному формату датчиков с KKS
    analog_kks = [i[:-1] for i in analog_kks]
    return analog_kks


@eel.expose
def get_discrete_kks_by_mask(mask):
    """
    Функция возвращает kks дискретных датчиков из файла democub_all.csv по маске шаблона
    :param mask: маска шаблона regex для поиска тегов kks
    :return: массив строк kks дискретных датчиков
    """
    logger.info(f"get_discrete_kks_by_mask({mask})")

    # Если маска пустая, то вовзвращаем пустой массив
    if not mask:
        return []
    discrete_kks = pd.read_csv(constants.DATA_DISCRETE, header=None)
    discrete_kks = discrete_kks[discrete_kks[0].str.contains(mask, regex=True)][0].tolist()
    return discrete_kks


@eel.expose
def get_kks_by_masks(types_list, mask_list):
    """
    Функция возвращает массив kks датчиков из файла тегов kks_all.csv по маске шаблона при поиске kks
    :param types_list: массив выбранных пользователем типов данных
    :param mask_list: массив маск шаблонов поиска regex
    :return: массив строк kks датчиков (чтобы не перегружать форму 10000)
    """
    logger.info(f"get_kks_by_masks({types_list}, {mask_list})")
    kks = KKS_ALL.copy(deep=True)

    kks = kks[kks[1].isin(types_list)]
    logger.info(kks)

    # Если маска пустая, то вовзвращаем пустой массив
    if not mask_list:
        return []

    # Если ведем в веб-приложении поиск тегов и очищаем всю строку поиска, то вовзвращаем пустой массив
    if mask_list[0] == '':
        return []

    for mask in mask_list:
        kks = kks[kks[0].str.contains(mask, regex=True)]

    logger.info(kks[0])
    return kks[0].tolist()[:constants.COUNT_OF_RETURNED_KKS]


@eel.expose
def get_kks(types_list, mask_list, kks_list):
    """
    Функция возвращает массив kks датчиков из файла тегов kks_all.csv по маске шаблона.
    Используется при выполнеии запросов на бэкенде
    :param types_list: массив выбранных пользователем типов данных
    :param mask_list: массив маск шаблонов поиска regex
    :param kks_list: массив kks напрямую, указанные пользователем
    :return: массив строк kks датчиков для выполнения запроса
    """
    logger.info(f"get_kks({types_list} ,{mask_list}, {kks_list})")
    kks_requested_list = []
    kks_mask_list = []

    # Отбор тегов kks по типу данных и маске
    kks = KKS_ALL.copy(deep=True)
    kks = kks[kks[1].isin(types_list)]

    list_kks = kks[0].tolist()
    set_list_kks = list(set(kks[0].tolist()))

    # Проверка на дубликаты kks, образовывающиеся при поиске по маске и вручную указанным пользователем

    try:
        assert len(list_kks) == len(set_list_kks)
    except AssertionError:
        logger.warning("В найденных тегах есть дубликаты")

    # Отбор тегов по указанным маскам
    if mask_list:
        for mask in mask_list:
            kks = kks[kks[0].str.contains(mask, regex=True)]
        kks_mask_list = kks[0].tolist()

    # Отбор тегов, указанных вручную
    if kks_list:
        kks_requested_list = [kks for kks in kks_list if kks not in kks_mask_list]

    kks_requested_list += kks_mask_list
    logger.info(kks_requested_list)
    return kks_requested_list


@eel.expose
def get_kks_tag_exist(kks_tag):
    """
    Функция возвращает результат проверки наличия тега в файле тегов kks_all.csv
    :param kks_tag: проверяемый тег kks
    :return: True - тег в файле тегов kks_all.csv; False - тега не найден в файле тегов kks_all.csv или это шаблон маски
    """
    logger.info(f"get_kks_exist({kks_tag})")
    return kks_tag in KKS_ALL[0].values


@eel.expose
def get_server_config():
    """
    Функция возвращает конфигурацию клиента OPC UA
    :return: строка конфигурации клиента OPC UA, True/False результат проверки существования файла тегов kks_all.csv
    """
    logger.info(f"get_server_config()")
    with open(constants.CLIENT_SERVER_CONF, "r") as readfile:
        server_config = readfile.readline()
        logger.info(server_config)

    return server_config, os.path.isfile(constants.DATA_KKS_ALL)


@eel.expose
def get_ip_port_config():
    """
    Функция возвращает ip-адрес и порт клиента OPC UA
    :return: строка ip-адресс, строка порта
    """
    logger.info(f"get_ip_port_config()")
    with open(constants.CLIENT_SERVER_CONF, "r") as readfile:
        server_config = readfile.readline().replace("opc.tcp://", '')
        logger.info(server_config)

    ip, port = server_config.split(':')
    return ip, port


@eel.expose
def change_opc_server_config(ip, port):
    """
    Процедура заменяет строку конфигурации клиента OPC UA
    :param ip: ip-адресс
    :param port: порта
    """
    logger.info(f"change_opc_server_config({ip}, {port})")

    with open(constants.CLIENT_SERVER_CONF, "w") as writefile:
        writefile.write(f"opc.tcp://{ip}:{port}")


@eel.expose
def get_last_update_file_kks():
    """
    Функция возвращает дату последнего обновления файла тегов kks_all.csv
    :return: строка даты последнего обновления файла тегов kks_all.csv
    """
    logger.info(f"get_last_update_file_kks()")
    if not os.path.isfile(constants.DATA_KKS_ALL):
        return f"Файл {constants.DATA_KKS_ALL} не найден"
    logger.info(str(datetime.datetime.fromtimestamp(os.path.getmtime(constants.DATA_KKS_ALL))))
    return str(datetime.datetime.fromtimestamp(os.path.getmtime(constants.DATA_KKS_ALL)))


@eel.expose
def get_types_of_sensors():
    """
    Функция возвращает все типы данных тегов kks, найденных в файле тегов kks_all.csv
    :return: массив строк типовы данных
    """
    logger.info(f"get_types_of_sensors()")
    logger.info(KKS_ALL[1].dropna().unique().tolist())
    return KKS_ALL[1].dropna().unique().tolist()


# Переменная под объект гринлета обновления тегов
update_greenlet = None
# Переменная под объект модуля subprocess процесса обновления тегов
p_kks_all = None


@eel.expose
def update_kks_all():
    """
    Процедура запуска гринлета обновления файла тегов kks_all.csv
    """
    logger.info(f"update_kks_all()")

    def update_kks_all_spawn():
        """
        Процедура запуска обновления файла тегов kks_all.csv
        """
        logger.info(f"update_kks_all_spawn()")
        eel.sleep(5)
        command_kks_all_string = f"cd client && ./client -k all -c"
        command_tail_kks_all_string = f"wc -l {constants.CLIENT_KKS} && tail -1 {constants.CLIENT_KKS}"
        logger.info(f'get from OPC_UA all kks and types')
        logger.info(command_kks_all_string)

        args = command_kks_all_string  # команда запуска процесса обновления
        args_tail = command_tail_kks_all_string  # команда получения последнего тега в файле kks_all.csv

        try:
            global p_kks_all
            # with open('test', "w+") as outfile:
            out = open('out.log', 'w+')
            err = open('err.log', 'w+')
            # p_kks_all = subprocess.Popen(args, stdout=out, shell=True, stderr=err)

            p_kks_all = subprocess.Popen(args, stdout=out, shell=True, preexec_fn=os.setsid, stderr=err)
            # p_kks_all = subprocess.Popen(args, close_fds=True, stdout=outfile, shell=True,
            #                              preexec_fn=os.setsid, stderr=subprocess.PIPE, bufsize=1, text=True)
            eel.sleep(1)  # даем небольшое время на наполнение временного файла тегов kks.csv

            # line = p_kks_all.stdout.read(1)
            # logger.info(line)
            # if line == '':
            #     logger.info(line)
            #     return
            # sys.stdout.write(line)
            # sys.stdout.flush()

            # Если процесс завершается сразу, то скорее всего произошла ошибка
            if p_kks_all.poll() == 0:
                try:
                    lines = p_kks_all.stdout.read()
                    # lines = outfile.read()
                    logger.info(lines)
                    lines_decode = str(lines)
                    # Выводим в веб-приложении ошибку
                    eel.setUpdateStatus(f"Ошибка: {lines_decode}\n", True)
                    return

                    # if "Connect failed with status BadTimeout" in lines_decode:
                    #     eel.setUpdateStatus(f"Ошибка: {lines_decode}\n", True)
                    #     return
                    #
                    # if "Connect failed with status Bad" in lines_decode:
                    #     eel.setUpdateStatus(f"Ошибка: {lines_decode}\n", True)
                    #     return
                    #
                    # if "Connect failed with status BadCommunicationError" in lines_decode:
                    #     eel.setUpdateStatus(f"Ошибка: {lines_decode}\n", True)
                    #     return
                    #
                    # if "Connect failed with status BadDisconnect" in lines_decode:
                    #     eel.setUpdateStatus(f"Ошибка: {lines_decode}\n", True)
                    #     return

                except Exception as exception:
                    # Если произошла неизвестная ошибка, то ловим и выводим исключение
                    logger.error(exception)
                    eel.setUpdateStatus(f"Ошибка: {exception}\n", True)
                    return

            # Ждем окончание процесса обновления тегов клиентом
            while p_kks_all.poll() != 0:
                logger.info(p_kks_all)
                logger.info(p_kks_all.stdout)




                # logger.info(outfile.read())



                # line = p_kks_all.stdout.read(1)
                # logger.info(line)
                # if line == '':
                #     break
                # sys.stdout.write(line)
                # sys.stdout.flush()


                # try:
                #     with open(f"/proc/{p_kks_all.pid}/fd/1", 'r') as readfile:
                #         lines = readfile.read()
                #
                #     logger.info(lines)

                    # if "Connect failed with status BadTimeout" in lines:
                    #     eel.setUpdateStatus(f"Ошибка: {lines}\n", True)
                    #     return
                    #
                    # if "Connect failed with status Bad" in lines:
                    #     eel.setUpdateStatus(f"Ошибка: {lines}\n", True)
                    #     return
                    #
                    # if "Connect failed with status BadCommunicationError" in lines:
                    #     eel.setUpdateStatus(f"Ошибка: {lines}\n", True)
                    #     return
                    #
                    # if "Connect failed with status BadDisconnect" in lines:
                    #     eel.setUpdateStatus(f"Ошибка: {lines}\n", True)
                    #     return

                # except Exception as exception:
                #     logger.error(exception)
                #     lines = p_kks_all.stdout.read()
                #     lines_decode = str(lines.decode('utf-8'))
                    # if "Connect failed with status BadTimeout" in lines_decode:
                    #     eel.setUpdateStatus(f"Ошибка: {lines_decode}\n", True)
                    #     return
                    #
                    # if "Connect failed with status Bad" in lines_decode:
                    #     eel.setUpdateStatus(f"Ошибка: {lines_decode}\n", True)
                    #     return
                    #
                    # if "Connect failed with status BadCommunicationError" in lines_decode:
                    #     eel.setUpdateStatus(f"Ошибка: {lines_decode}\n", True)
                    #     return
                    #
                    # if "Connect failed with status BadDisconnect" in lines_decode:
                    #     eel.setUpdateStatus(f"Ошибка: {lines_decode}\n", True)
                    #     return
                    # eel.setUpdateStatus(f"Ошибка: {exception}\n", True)
                    # return

                # logger.info(p_kks_all.stdout.read())
                # logger.info(p_kks_all.stdout.read())

                # try:
                #     lines = p_kks_all.stdout.read()
                #     lines_decode = str(lines.decode('utf-8'))
                #     if "Connect failed with status BadTimeout" in lines_decode:
                #         eel.setUpdateStatus(f"Ошибка: {lines_decode}\n", True)
                #         return
                #
                #     if "Connect failed with status Bad" in lines_decode:
                #         eel.setUpdateStatus(f"Ошибка: {lines_decode}\n", True)
                #         return
                #
                #     if "Connect failed with status BadCommunicationError" in lines_decode:
                #         eel.setUpdateStatus(f"Ошибка: {lines_decode}\n", True)
                #         return
                #
                # if "Connect failed with status BadDisconnect" in lines_decode:
                #     eel.setUpdateStatus(f"Ошибка: {lines_decode}\n", True)
                #     return
                #
                # except Exception as exception:
                #     logger.error(exception)
                #     return

                # try:
                # logger.info(p_kks_all.stdout)
                # out_kks_all, err_kks_all = p_kks_all.communicate(timeout=10)
                # if "Connect failed with status BadTimeout" in out_kks_all.decode('utf-8'):
                #     logger.info(out_kks_all.decode('utf-8'))
                #     eel.setUpdateStatus(f"Ошибка: {out_kks_all.decode('utf-8')}\n")
                #     return
                # except TimeoutExpired:

                # Последний выкаченный тег

                p_tail = subprocess.Popen(args_tail, stdout=subprocess.PIPE, shell=True)
                out, err = p_tail.communicate()
                records = out.decode('utf-8').split('\n')
                count = records[0].split()[0]
                record = records[1].split(';')[0]
                eel.setUpdateStatus(f"{count}. {record} Успех\n", False)
                logger.info(f"{count}. {record} Успех\n")
                eel.sleep(5)

            eel.setUpdateStatus(f"Последняя запись\n", True)
            p_tail = subprocess.Popen(args_tail, stdout=subprocess.PIPE, shell=True)
            out, err = p_tail.communicate()
            records = out.decode('utf-8').split('\n')
            count = records[0].split()[0]
            record = records[1].split(';')[0]
            eel.setUpdateStatus(f"{count}. {record} Успех\n", True)
        except subprocess.CalledProcessError as subprocess_exception:
            # Если произошла ошибка во время вызова клиента, то ловим и выводим исключение
            logger.error(subprocess_exception)
            eel.setUpdateStatus(f"Ошибка: {subprocess_exception}\n", True)
        except RuntimeError as run_time_exception:
            # Если произошла ошибка во время выполнении процесса, то ловим и выводим исключение
            logger.error(run_time_exception)
            eel.setUpdateStatus(f"Ошибка: {run_time_exception}\n", True)
            return

        shutil.copy(constants.CLIENT_KKS, constants.DATA_KKS_ALL)  # копируем kks.csv в data/kks_all.csv
        # Пытаемся загрузить kks_all.csv, если он существует в переменную
        try:
            global KKS_ALL
            KKS_ALL = pd.read_csv(constants.DATA_KKS_ALL, header=None, sep=';')
        except FileNotFoundError as csv_exception:
            logger.info(csv_exception)

        eel.setUpdateStatus(f"Обновление тегов закончено\n", True)

    # Запуск гринлета обновления тегов
    global update_greenlet
    # Если обновление уже идет, выводим в веб-приложении
    if update_greenlet:
        logger.warning(f"update_greenlet is running")
        eel.setUpdateStatus(f"Обновление тегов уже было начато на сервере\n", True)
        return

    # Запуск процесса обновления тегов через gevent
    update_greenlet = eel.spawn(update_kks_all_spawn)
    eel.gvt.joinall([update_greenlet])


@eel.expose
def update_cancel():
    """
    Процедура отмены процесса обновления и уничтожения гринлета gevent
    """
    logger.info(f"update_cancel()")
    global update_greenlet
    global p_kks_all
    if update_greenlet:
        if p_kks_all:
            # Убиваем по групповому id, чтобы завершить все дочерние процессы
            os.killpg(os.getpgid(p_kks_all.pid), signal.SIGINT)
            # os.kill(p_kks_all.pid, signal.SIGINT)
            p_kks_all = None
        eel.gvt.killall([update_greenlet])
        logger.info(f"update_greenlet убит")
        eel.setUpdateStatus(f"Обновление тегов прервано пользователем\n", True)
        update_greenlet = None


# Переменная под объект гринлета выполнения запроса по срезам тегов
signals_greenlet = None


@eel.expose
def get_signals_data(types_list, mask_list, kks_list, quality, date, date_deep_search):
    """
    Функция запуска гринлета выполнения запроса по срезам тегов
    :param types_list: массив выбранных пользователем типов данных
    :param mask_list: массив маск шаблонов поиска regex
    :param kks_list: массив kks напрямую, указанные пользователем
    :param quality: массив кодов качества, указанные пользователем
    :param date: дата, указанная пользователем в запросе
    :param date_deep_search: дата глубины поиска данных в архивах
    :return: json объект для заполнения таблицы срезов тегов
    """
    logger.info(f"get_signals_data({types_list} ,{mask_list}, {kks_list}, {quality}, {date}, {date_deep_search})")

    def get_signals_data_spawn(types_list, mask_list, kks_list, quality, date, date_deep_search):
        """
        Функция запуска выполнения запроса по срезам тегов
        :param types_list: массив выбранных пользователем типов данных
        :param mask_list: массив маск шаблонов поиска regex
        :param kks_list: массив kks напрямую, указанные пользователем
        :param quality: массив кодов качества, указанные пользователем
        :param date: дата, указанная пользователем в запросе
        :param date_deep_search: дата глубины поиска данных в архивах
        :return: json объект для заполнения таблицы срезов тегов
        """
        logger.info(f"get_signals_data_spawn({types_list} ,{mask_list}, {kks_list}, {quality}, {date}, {date_deep_search})")
        error_flag = False  # флаг ошибки поиска в архивах

        eel.setUpdateSignalsRequestStatus(f"Формирование списка kks сигналов\n")
        kks_requested_list = get_kks(types_list, mask_list, kks_list)
        logger.info(kks_requested_list)
        eel.setUpdateSignalsRequestStatus(f"Список kks сигналов успешно сформирован\n")

        # Подготовка к выполнению запроса
        # Формирование списка выбранных кодов качества
        correct_quality_list = list(map(lambda x: constants.QUALITY_CODE_DICT[x], quality))

        # Формирование декартового произведения
        decart_list = [kks_requested_list, correct_quality_list]
        decart_product = []

        for element in itertools.product(*decart_list):
            decart_product.append(element)

        # Сбрасываем обобщенную таблицу
        con_common_data = sqlite3.connect(constants.CLIENT_COMMON_DATA)
        cursor = con_common_data.cursor()
        cursor.execute(f'DROP TABLE IF EXISTS {constants.CLIENT_COMMON_DATA_TABLE}')
        con_common_data.commit()
        con_common_data.close()

        for i, element in enumerate(decart_product):
            # Сохранение датчика с KKS
            csv_tag_KKS = pd.DataFrame(data=[element[0]])
            csv_tag_KKS.to_csv(constants.CLIENT_KKS, index=False, header=None)

            # Формирование команды для запуска бинарника historian
            command_datetime_begin_time = (parse(date) - datetime.timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            command_datetime_end_time = parse(date).strftime("%Y-%m-%dT%H:%M:%SZ")
            command_string = f"cd client && ./client -b {command_datetime_begin_time} -e " \
                             f"{command_datetime_end_time} -p 100 -t 10000 -r -xw"

            logger.info(f'Получение по OPC UA: {element[0]}->{element[1]}')
            logger.info(command_string)

            eel.setUpdateSignalsRequestStatus(f"Получение по OPC UA: {element[0]}->{element[1]}\n")

            args = command_string
            try:
                subprocess.run(args, capture_output=True, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                # Если произошла ошибка во время вызова клиента, то ловим и выводим исключение
                logger.error(e)
                return f"Произошла ошибка {str(e)}"
            except RuntimeError as run_time_exception:
                # Если произошла ошибка во время выполнении процесса, то ловим и выводим исключение
                logger.error(run_time_exception)
                eel.setUpdateSignalsRequestStatus(f"Ошибка: {run_time_exception}\n")
                return

            # Достаем фрейм из sqlite
            con_current_data = sqlite3.connect(constants.CLIENT_DATA)

            query_string = f"SELECT * from {constants.CLIENT_DYNAMIC_TABLE} WHERE id='{element[0]}' " \
                           f"AND status='{element[-1]}' AND t <= '{parse(date).strftime('%Y-%m-%d %H:%M:%S')}' " \
                           f"ORDER BY t DESC LIMIT 1"
            logger.info(query_string)

            df_sqlite = pd.read_sql_query(
                query_string,
                con_current_data, parse_dates=['t'])
            con_current_data.close()
            logger.info(df_sqlite)
            # Если не нашли, то расширяем поиск:
            if df_sqlite.empty:
                logger.info(f"{constants.CLIENT_DATA} пуст")
                eel.setUpdateSignalsRequestStatus(f"Расширение поиска в архивах...\n")

                # Получаем предельное время в часах для поиска в глубину в архивах
                deep_search_in_hour = (parse(date) - parse(date_deep_search)).total_seconds() / 3600

                delta = 2  # Строим запрос на 2 секунды раньше
                delta_prev = 0  # Формирование окна просмотра архива посредстовом сохранения предыдущего datetime
                while df_sqlite.empty:
                    logger.info(df_sqlite)
                    try:
                        # Формирование повторной команды с расширенной выборкой
                        command_datetime_begin_time = (parse(date) - datetime.timedelta(hours=delta)).strftime(
                            "%Y-%m-%dT%H:%M:%SZ")
                        command_datetime_end_time = (parse(date) - datetime.timedelta(hours=delta_prev)).strftime(
                            "%Y-%m-%dT%H:%M:%SZ")

                        command_string = f"cd client && ./client -b {command_datetime_begin_time} -e " \
                                         f"{command_datetime_end_time} -p 100 -t 10000 -xw"
                        logger.info(f'Получение по OPC UA: {element[0]}->{element[1]}')
                        logger.info(command_string)

                        eel.setUpdateSignalsRequestStatus(f"Получение по OPC UA: {element[0]}->{element[1]}\n"
                                                          f"за период с {command_datetime_begin_time} по "
                                                          f"{command_datetime_end_time}\n")

                        args = command_string
                        try:
                            subprocess.run(args, capture_output=True, shell=True, check=True)
                        except subprocess.CalledProcessError as e:
                            # Если произошла ошибка во время вызова клиента, то ловим и выводим исключение
                            logger.error(e)
                            return f"Произошла ошибка {str(e)}"
                        except RuntimeError as run_time_exception:
                            # Если произошла ошибка во время выполнении процесса, то ловим и выводим исключение
                            logger.error(run_time_exception)
                            eel.setUpdateSignalsRequestStatus(f"Ошибка: {run_time_exception}\n")
                            return

                        con_current_data = sqlite3.connect(constants.CLIENT_DATA)
                        df_sqlite = pd.read_sql_query(
                            query_string,
                            con_current_data, parse_dates=['t'])
                        con_current_data.close()
                        delta_prev = delta
                        delta += constants.STEP_OF_BACK_SEARCH
                        # Если больше 1 года
                        # if delta > constants.BACK_SEARCH_TIME_IN_HOUR:
                        if delta > deep_search_in_hour:
                            logger.info(f"За заданный период поиска в часах ({deep_search_in_hour}) в архиве ничего не нашлось: {element[0]}->{element[1]}")
                            eel.setUpdateSignalsRequestStatus(f"За заданный период поиска в часах ({deep_search_in_hour}) в архиве ничего не нашлось: {element[0]}->{element[1]}\n")
                            error_flag = True
                            break
                    except OverflowError:
                        error_flag = True
                        logger.info(f'OverflowError: {element[0]}->{element[1]}')
                        logger.info(f'begin_time = {command_datetime_begin_time}; end_time = {command_datetime_end_time}')
                        eel.setUpdateSignalsRequestStatus(f"OverflowError: {element[0]}->{element[1]}\n"
                                                          f"begin_time = {command_datetime_begin_time}; "
                                                          f"end_time = {command_datetime_end_time}\n")
                        break

            if not error_flag:
                con_common_data = sqlite3.connect(constants.CLIENT_COMMON_DATA)
                logger.info(con_common_data)
                df_sqlite.to_sql(f'{constants.CLIENT_COMMON_DATA_TABLE}', con_common_data, if_exists='append', index=False)
                con_common_data.close()
                logger.info(f'Успешно завершено: {element[0]}->{element[1]}')
                eel.setUpdateSignalsRequestStatus(f"Успешно завершено: {element[0]}->{element[1]}\n")
            error_flag = False
            eel.setProgressBarSignals(int((i+1)/len(decart_product) * 100 * 0.9))  # 0.9 для масштабирования max в 90%

        try:
            con_common_data = sqlite3.connect(constants.CLIENT_COMMON_DATA)

            df_sqlite = pd.read_sql_query(
                f"SELECT * from {constants.CLIENT_COMMON_DATA_TABLE}",
                con_common_data, parse_dates=['t'])
        except Exception as e:
            # Если произошла ошибка с sqlite, то ловим и выводим исключение
            logger.error(f"{constants.CLIENT_COMMON_DATA_TABLE} is empty: {e}")
            eel.setUpdateSignalsRequestStatus(f"Никаких данных за год не нашлось\n")
            return f"Никаких данных за год не нашлось"
        finally:
            con_common_data.close()

        df_report = pd.DataFrame(
            columns=['Код сигнала (KKS)', 'Дата и время измерения', 'Значение', 'Качество',
                     'Код качества'],
            data={'Код сигнала (KKS)': df_sqlite['id'],
                  'Дата и время измерения': df_sqlite['t'],
                  'Значение': df_sqlite['val'],
                  'Качество': df_sqlite['status'],
                  'Код качества': list(map(lambda x: constants.QUALITY_DICT[x], df_sqlite['status'].to_list()))})
        df_report.to_csv(constants.CSV_SIGNALS, index=False, encoding='utf-8')
        logger.info("Датафрейм сформирован")
        shutil.copy(constants.CSV_SIGNALS, f'{constants.WEB_DIR}signals_slice.csv')
        logger.info("Датафрейм доступен для выкачки")
        df_report['Дата и время измерения'] = df_report['Дата и время измерения'].dt.strftime('%Y-%m-%d %H:%M:%S')
        eel.setUpdateSignalsRequestStatus(f"Запрос успешно завершен\n")

        eel.setProgressBarSignals(90)
        eel.setUpdateSignalsRequestStatus(f"Формирование отчета\n")
        slice = json.loads(df_report.to_json(orient='records'))
        render_slice(slice)
        eel.setUpdateSignalsRequestStatus(f"Отчет сформирован\n")

        return slice

    global signals_greenlet
    global analog_signals_greenlet
    global discrete_signals_greenlet
    global grid_greenlet
    global analog_grid_greenlet
    global discrete_grid_greenlet
    global bounce_greenlet
    started_greenlet = [signals_greenlet, analog_signals_greenlet, discrete_signals_greenlet,
                        grid_greenlet, analog_grid_greenlet, discrete_grid_greenlet, bounce_greenlet]
    if any(started_greenlet):
        logger.warning(f"signals_greenlet is running")
        return f"Запрос уже выполняется для другого клиента. Попробуйте выполнить запрос позже"
    signals_greenlet = eel.spawn(get_signals_data_spawn, types_list, mask_list, kks_list, quality, date, date_deep_search)
    eel.gvt.joinall([signals_greenlet])

    logger.info("Формирование отчета")
    return signals_greenlet.value


@eel.expose
def signals_data_cancel():
    """
    Процедура отмены процесса выполнения запросов срезов и уничтожения гринлета gevent
    """
    logger.info(f"signals_data_cancel()")
    global signals_greenlet
    if signals_greenlet:
        eel.gvt.killall([signals_greenlet])
        signals_greenlet = None


# Переменная под объект гринлета выполнения запроса сетки
grid_greenlet = None


@eel.expose
def get_grid_data(kks, date_begin, date_end, interval, dimension):
    """
    Функция запуска гринлета выполнения запроса сетки
    :param kks: массив kks
    :param date_begin: начальная дата сетки
    :param date_end: конечная дата сетки
    :param interval: интервал
    :param dimension: размерность интервала [день, час, минута, секунда]
    :return: json объект для заполнения таблицы сеток
    """
    logger.info(f"get_grid_data({kks}, {date_begin}, {date_end}, {interval}, {dimension})")

    def get_grid_data_spawn(kks, date_begin, date_end, interval, dimension):
        """
        Функция запуска выполнения запроса сетки
        :param kks: массив kks
        :param date_begin: начальная дата сетки
        :param date_end: конечная дата сетки
        :param interval: интервал
        :param dimension: размерность интервала [день, час, минута, секунда]
        :return: json объект для заполнения таблицы сеток
        """
        logger.info(f"get_grid_data_spawn({kks}, {date_begin}, {date_end}, {interval}, {dimension})")
        # Сохранение датчика с KKS
        eel.setUpdateGridRequestStatus(f"Сохранение датчиков KKS\n")
        csv_tag_KKS = pd.DataFrame(data=kks)
        csv_tag_KKS.to_csv(constants.CLIENT_KKS, index=False, header=None)

        # Формирование команд для запуска бинарника historian и скрипта slices.py
        command_datetime_begin_time = parse(date_begin).strftime("%Y-%m-%d %H:%M:%S")
        command_datetime_end_time = parse(date_end).strftime("%Y-%m-%d %H:%M:%S")

        command_datetime_begin_time_binary = parse(date_begin).strftime("%Y-%m-%dT%H:%M:%SZ")
        command_datetime_end_time_binary = parse(date_end).strftime("%Y-%m-%dT%H:%M:%SZ")

        command_string_binary = f"cd client && ./client -b {command_datetime_begin_time_binary} -e " \
                                f"{command_datetime_end_time_binary} -p 100 -t 10000 -rxw"

        delta_interval = interval * constants.DELTA_INTERVAL_IN_SECONDS[dimension]
        command_string = f'cd client && python ./slicer_for_streamlit.py -d {delta_interval} ' \
                         f'-t \"{command_datetime_begin_time}\" \"{command_datetime_end_time}\"'

        logger.info("Получение по OPC UA")
        logger.info(command_string_binary)

        eel.setUpdateGridRequestStatus(f"Получение по OPC UA валидных тегов\n")

        eel.setProgressBarGrid(5)

        args = command_string_binary
        try:
            subprocess.run(args, capture_output=True, shell=True, check=True)
            eel.setProgressBarGrid(10)
        except subprocess.CalledProcessError as subprocess_exception:
            # Если произошла ошибка во время вызова клиента, то ловим и выводим исключение
            logger.error(subprocess_exception)
            return f"Произошла ошибка {str(subprocess_exception)}"
        except RuntimeError as run_time_exception:
            # Если произошла ошибка во время выполнении процесса, то ловим и выводим исключение
            logger.error(run_time_exception)
            eel.setUpdateGridRequestStatus(f"Ошибка: {run_time_exception}\n")
            return

        logger.info("Получение срезов")
        logger.info(command_string)

        eel.setUpdateGridRequestStatus(f"Получение срезов\n")

        args = command_string
        try:
            eel.setProgressBarGrid(40)
            subprocess.run(args, capture_output=True, shell=True, check=True)
            eel.setProgressBarGrid(50)
        except subprocess.CalledProcessError as subprocess_exception:
            # Если произошла ошибка во время вызова клиента, то ловим и выводим исключение
            logger.error(subprocess_exception)
            if "ValueError: sampling_period is greater than the duration between start and end" in str(subprocess_exception):
                logger.error("интервал больше, чем дата начала и конца")
                return f"интервал больше, чем дата начала и конца"
        except RuntimeError as run_time_exception:
            # Если произошла ошибка во время выполнении процесса, то ловим и выводим исключение
            logger.error(run_time_exception)
            eel.setUpdateGridRequestStatus(f"Ошибка: {run_time_exception}\n")
            return

        eel.setUpdateGridRequestStatus(f"Формирование таблиц отчета\n")

        df_slice_csv = pd.read_csv(constants.CLIENT_SLICES)
        df_slice_status_csv = pd.read_csv(constants.CLIENT_SLICES_STATUS)

        df_report = pd.DataFrame(df_slice_csv['timestamp'])
        df_report.rename(columns={'timestamp': 'Метка времени'}, inplace=True)

        df_report_slice = pd.DataFrame(df_slice_status_csv['timestamp'])
        df_report_slice.rename(columns={'timestamp': 'Метка времени'}, inplace=True)

        for index, kks in enumerate(df_slice_csv.columns.tolist()[1:]):
            df_report[index] = df_slice_csv[kks]
            df_report_slice[index] = df_slice_status_csv[kks]

        eel.setProgressBarGrid(70)

        logger.info(df_report)
        logger.info(df_report_slice)

        eel.setUpdateGridRequestStatus(f"Сохранение таблиц отчета\n")

        df_report.to_csv(constants.CSV_GRID, index=False, encoding='utf-8')
        logger.info("Датафрейм сформирован")

        shutil.copy(constants.CSV_GRID, f'{constants.WEB_DIR}grid.csv')
        logger.info("Датафрейм доступен для выкачки")

        # get_report_grid(code_kks, colored_df_list, colored_dict_list, 'аналоговых')
        eel.setUpdateGridRequestStatus(f"Передача данных в веб-приложение...\n")

        eel.setProgressBarGrid(90)
        eel.setUpdateGridRequestStatus(f"Формирование отчета\n")
        code = json.loads(pd.DataFrame(data={
            '№': [i for i in range(len(df_slice_csv.columns.tolist()[1:]))],
            'Обозначение сигнала': [kks for kks in df_slice_csv.columns.tolist()[1:]]})
                          .to_json(orient='records'))

        # Разделение таблиц по группам по 5 датчикам
        separate_count = 1
        grid_separated_json_list = []
        status_separated_json_list = []

        grid_separated_json_list_single = []
        status_separated_json_list_single = []

        temp_df_slice = df_report[['Метка времени']].copy()
        temp_df_status = df_report_slice[['Метка времени']].copy()

        for kks in df_report.columns.tolist()[1:]:
            temp_df_slice[kks] = df_report[kks]
            temp_df_status[kks] = df_report_slice[kks]

            if (separate_count % constants.SEPARATED_COUNT == 0) \
                    or (separate_count == len(df_report.columns.tolist()[1:])):
                temp_json_grid = json.loads(temp_df_slice.to_json(orient='records'))
                temp_json_status = json.loads(temp_df_status.to_json(orient='records'))

                grid_separated_json_list.append(temp_json_grid)
                status_separated_json_list.append(temp_json_status)

                for index in temp_df_slice.columns.tolist()[1:]:
                    temp_json_grid_single = json.loads(temp_df_slice[['Метка времени', index]].copy()
                                                       .to_json(orient='records'))
                    temp_json_status_single = json.loads(temp_df_status[['Метка времени', index]].copy()
                                                         .to_json(orient='records'))

                    grid_separated_json_list_single.append(temp_json_grid_single)
                    status_separated_json_list_single.append(temp_json_status_single)

                temp_df_slice = df_report[['Метка времени']].copy()
                temp_df_status = df_report_slice[['Метка времени']].copy()
            separate_count += 1
        # grid, status = json.loads(df_report.to_json(orient='records')), json.loads(df_report_slice.
        #                                                                            to_json(orient='records'))

        parameters_of_request = {
            "date_begin": date_begin,
            "date_end": date_end,
            "interval": interval,
            "dimension": constants.INTERVAL_TO_LOCALE[dimension]
        }

        render_grid(code, grid_separated_json_list, status_separated_json_list,
                    grid_separated_json_list_single, status_separated_json_list_single, parameters_of_request)
        eel.setUpdateGridRequestStatus(f"Отчет сформирован\n")

        return json.loads(df_report.to_json(orient='records')), json.loads(df_report_slice.to_json(orient='records'))

    global signals_greenlet
    global analog_signals_greenlet
    global discrete_signals_greenlet
    global grid_greenlet
    global analog_grid_greenlet
    global discrete_grid_greenlet
    global bounce_greenlet
    started_greenlet = [signals_greenlet, analog_signals_greenlet, discrete_signals_greenlet,
                        grid_greenlet, analog_grid_greenlet, discrete_grid_greenlet, bounce_greenlet]
    if any(started_greenlet):
        logger.warning(f"grid_greenlet is running")
        return f"Запрос уже выполняется для другого клиента. Попробуйте выполнить запрос позже"
    grid_greenlet = eel.spawn(get_grid_data_spawn, kks, date_begin, date_end, interval, dimension)
    eel.gvt.joinall([grid_greenlet])
    # if grid_greenlet:
    return grid_greenlet.value


@eel.expose
def grid_data_cancel():
    """
    Процедура отмены процесса выполнения запросов сетки и уничтожения гринлета gevent
    :return:
    """
    logger.info(f"grid_data_cancel()")
    global grid_greenlet
    if grid_greenlet:
        eel.gvt.killall([grid_greenlet])
        grid_greenlet = None


analog_signals_greenlet = None


@eel.expose
def get_analog_signals_data(kks, quality, date):
    logger.info(f"get_analog_signals_data({kks}, {quality}, {date})")

    def get_analog_signals_data_spawn(kks, quality, date):
        logger.info(f"get_analog_signals_data_spawn({kks}, {quality}, {date})")
        error_flag = False

        # Подготовка к выполнению запроса
        # Формирование списка выбранных кодов качества
        correct_quality_list = list(map(lambda x: constants.QUALITY_CODE_DICT[x], quality))

        # Формирование декартового произведения
        decart_list = [kks, correct_quality_list]
        decart_product = []

        for element in itertools.product(*decart_list):
            decart_product.append(element)

        # Сбрасываем обобщенную таблицу
        con_common_data = sqlite3.connect(constants.CLIENT_COMMON_DATA)
        cursor = con_common_data.cursor()
        cursor.execute(f'DROP TABLE IF EXISTS {constants.CLIENT_COMMON_DATA_TABLE}')
        con_common_data.commit()
        con_common_data.close()

        for i, element in enumerate(decart_product):
            # Сохранение датчика с KKS
            csv_tag_KKS = pd.DataFrame(data=[element[0]])
            csv_tag_KKS.to_csv(constants.CLIENT_KKS, index=False, header=None)

            # Формирование команды для запуска бинарника historian
            command_datetime_begin_time = (parse(date) - datetime.timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            command_datetime_end_time = parse(date).strftime("%Y-%m-%dT%H:%M:%SZ")
            command_string = f"cd client && ./client -b {command_datetime_begin_time} -e " \
                             f"{command_datetime_end_time} -p 100 -t 10000 -r -xw"

            logger.info(f'get OPC_UA: {element[0]}->{element[1]}')
            logger.info(command_string)

            args = command_string
            try:
                subprocess.run(args, capture_output=True, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                logger.error(e)
                return f"Произошла ошибка {str(e)}"

            # Достаем фрейм из sqlite
            con_current_data = sqlite3.connect(constants.CLIENT_DATA)

            query_string = f"SELECT * from {constants.CLIENT_DYNAMIC_TABLE} WHERE id='{element[0]}' " \
                           f"AND status='{element[-1]}' AND t <= '{parse(date).strftime('%Y-%m-%d %H:%M:%S')}' " \
                           f"ORDER BY t DESC LIMIT 1"
            logger.info(query_string)

            df_sqlite = pd.read_sql_query(
                query_string,
                con_current_data, parse_dates=['t'])
            con_current_data.close()
            logger.info(df_sqlite)
            # Если не нашли, то расширяем поиск:
            if df_sqlite.empty:
                logger.info(f"{constants.CLIENT_DATA} is empty")
                delta = 2  # Строим запрос на 2 секунды раньше
                delta_prev = 0  # Формирование окна просмотра архива посредстовом сохранения предыдущего datetime
                while df_sqlite.empty:
                    logger.info(df_sqlite)
                    try:
                        # Формирование повторной команды с расширенной выборкой
                        command_datetime_begin_time = (parse(date) - datetime.timedelta(hours=delta)).strftime(
                            "%Y-%m-%dT%H:%M:%SZ")
                        command_datetime_end_time = (parse(date) - datetime.timedelta(hours=delta_prev)).strftime(
                            "%Y-%m-%dT%H:%M:%SZ")

                        command_string = f"cd client && ./client -b {command_datetime_begin_time} -e " \
                                         f"{command_datetime_end_time} -p 100 -t 10000 -xw"
                        logger.info(f'get OPC_UA: {element[0]}->{element[1]}')
                        logger.info(command_string)

                        args = command_string
                        try:
                            subprocess.run(args, capture_output=True, shell=True, check=True)
                        except subprocess.CalledProcessError as e:
                            logger.error(e)
                            return f"Произошла ошибка {str(e)}"

                        con_current_data = sqlite3.connect(constants.CLIENT_DATA)
                        df_sqlite = pd.read_sql_query(
                            query_string,
                            con_current_data, parse_dates=['t'])
                        con_current_data.close()
                        delta_prev = delta
                        delta += constants.STEP_OF_BACK_SEARCH
                        # Если больше 1 года
                        if delta > constants.BACK_SEARCH_TIME_IN_HOUR:
                            logger.info(f'За год не нашлось: {element[0]}->{element[1]}')
                            error_flag = True
                            break
                    except OverflowError:
                        error_flag = True
                        logger.info(f'OverflowError: {element[0]}->{element[1]}')
                        logger.info(
                            f'begin_time = {command_datetime_begin_time}; end_time = {command_datetime_end_time}')
                        break

            if not error_flag:
                con_common_data = sqlite3.connect(constants.CLIENT_COMMON_DATA)
                logger.info(con_common_data)
                df_sqlite.to_sql(f'{constants.CLIENT_COMMON_DATA_TABLE}', con_common_data, if_exists='append',
                                 index=False)
                con_common_data.close()
                logger.info(f'successfully completed: {element[0]}->{element[1]}')
            error_flag = False
            eel.setProgressBarAnalogSignals(int((i + 1) / len(decart_product) * 100))

        try:
            con_common_data = sqlite3.connect(constants.CLIENT_COMMON_DATA)

            df_sqlite = pd.read_sql_query(
                f"SELECT * from {constants.CLIENT_COMMON_DATA_TABLE}",
                con_common_data, parse_dates=['t'])
        except Exception as e:
            logger.error(f"{constants.CLIENT_COMMON_DATA_TABLE} is empty: {e}")
            return f"Никаких данных за год не нашлось"
        finally:
            con_common_data.close()

        df_report = pd.DataFrame(
            columns=['Код сигнала (KKS)', 'Дата и время измерения', 'Значение', 'Качество',
                     'Код качества'],
            data={'Код сигнала (KKS)': df_sqlite['id'],
                  'Дата и время измерения': df_sqlite['t'],
                  'Значение': df_sqlite['val'],
                  'Качество': df_sqlite['status'],
                  'Код качества': list(map(lambda x: constants.QUALITY_DICT[x], df_sqlite['status'].to_list()))})
        # df_report['Дата и время измерения'] = pd.to_datetime(df_report['Дата и время измерения'], unit='ms')
        # output = st.dataframe(data=df_report.style.applymap(color_cell), use_container_width=False)
        df_report.to_csv(constants.CSV_ANALOG_SLICES, index=False, encoding='utf-8')
        logger.info("data frame has been formed")

        # get_report_slice(df_report, 'аналоговых')

        shutil.copy(constants.CSV_ANALOG_SLICES, f'{constants.WEB_DIR}analog_slice.csv')
        logger.info("data frame is accessed for download")
        df_report['Дата и время измерения'] = df_report['Дата и время измерения'].dt.strftime('%Y-%m-%d %H:%M:%S')

        slice = json.loads(df_report.to_json(orient='records'))
        render_slice(slice)

        return slice

    global signals_greenlet
    global analog_signals_greenlet
    global discrete_signals_greenlet
    global grid_greenlet
    global analog_grid_greenlet
    global discrete_grid_greenlet
    global bounce_greenlet
    started_greenlet = [signals_greenlet, analog_signals_greenlet, discrete_signals_greenlet,
                        grid_greenlet, analog_grid_greenlet, discrete_grid_greenlet, bounce_greenlet]
    if any(started_greenlet):
        logger.warning(f"analog_signals_greenlet is running")
        return f"Запрос уже выполняется для другого клиента. Попробуйте выполнить запрос позже"

    analog_signals_greenlet = eel.spawn(get_analog_signals_data_spawn, kks, quality, date)
    eel.gvt.joinall([analog_signals_greenlet])
    # if analog_signals_greenlet:
    return analog_signals_greenlet.value


discrete_signals_greenlet = None


@eel.expose
def get_discrete_signals_data(kks, values, quality, date):
    logger.info(f"get_discrete_signals_data({kks}, {values}, {quality}, {date})")

    def get_discrete_signals_data_spawn(kks, values, quality, date):
        logger.info(f"get_discrete_signals_data({kks}, {values}, {quality}, {date})")
        error_flag = False

        # Подготовка к выполнению запроса
        # Формирование списка выбранных кодов качества
        correct_quality_list = list(map(lambda x: constants.QUALITY_CODE_DICT[x], quality))

        # Формирование декартового произведения
        decart_list = [kks, correct_quality_list, values]
        decart_product = []

        for element in itertools.product(*decart_list):
            decart_product.append(element)

        # Сбрасываем обобщенную таблицу
        con_common_data = sqlite3.connect(constants.CLIENT_COMMON_DATA)
        cursor = con_common_data.cursor()
        cursor.execute(f'DROP TABLE IF EXISTS {constants.CLIENT_COMMON_DATA_TABLE}')
        con_common_data.commit()
        con_common_data.close()

        for i, element in enumerate(decart_product):
            # Сохранение датчика с KKS
            csv_tag_KKS = pd.DataFrame(data=[element[0]])
            csv_tag_KKS.to_csv(constants.CLIENT_KKS, index=False, header=None)

            # Формирование команды для запуска бинарника historian
            command_datetime_begin_time = (parse(date) - datetime.timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            command_datetime_end_time = parse(date).strftime("%Y-%m-%dT%H:%M:%SZ")
            command_string = f"cd client && ./client -b {command_datetime_begin_time} -e " \
                             f"{command_datetime_end_time} -p 100 -t 10000 -r -xw"

            logger.info(f'get OPC_UA: {element[0]}->{element[1]}->{element[2]}')
            logger.info(command_string)

            args = command_string
            try:
                subprocess.run(args, capture_output=True, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                logger.error(e)
                return f"Произошла ошибка {str(e)}"

            # Достаем фрейм из sqlite
            con_current_data = sqlite3.connect(constants.CLIENT_DATA)

            query_string = f"SELECT * from {constants.CLIENT_DYNAMIC_TABLE} WHERE id='{element[0]}' " \
                           f"AND status='{element[1]}' AND val={element[2]} AND t <= '{parse(date).strftime('%Y-%m-%d %H:%M:%S')}' " \
                           f"ORDER BY t DESC LIMIT 1"
            logger.info(query_string)

            df_sqlite = pd.read_sql_query(
                query_string,
                con_current_data, parse_dates=['t'])
            con_current_data.close()
            logger.info(df_sqlite)
            # Если не нашли, то расширяем поиск:
            if df_sqlite.empty:
                logger.info(f"{constants.CLIENT_DATA} is empty")
                delta = 2  # Строим запрос на 2 секунды раньше
                delta_prev = 0  # Формирование окна просмотра архива посредстовом сохранения предыдущего datetime
                while df_sqlite.empty:
                    logger.info(df_sqlite)
                    try:
                        # Формирование повторной команды с расширенной выборкой
                        command_datetime_begin_time = (parse(date) - datetime.timedelta(hours=delta)).strftime(
                            "%Y-%m-%dT%H:%M:%SZ")
                        command_datetime_end_time = (parse(date) - datetime.timedelta(hours=delta_prev)).strftime(
                            "%Y-%m-%dT%H:%M:%SZ")

                        command_string = f"cd client && ./client -b {command_datetime_begin_time} -e " \
                                         f"{command_datetime_end_time} -p 100 -t 10000 -xw"
                        logger.info(f'get OPC_UA: {element[0]}->{element[1]}->{element[2]}')
                        logger.info(command_string)

                        args = command_string
                        try:
                            subprocess.run(args, capture_output=True, shell=True, check=True)
                        except subprocess.CalledProcessError as e:
                            logger.error(e)
                            return f"Произошла ошибка {str(e)}"

                        con_current_data = sqlite3.connect(constants.CLIENT_DATA)
                        df_sqlite = pd.read_sql_query(
                            query_string,
                            con_current_data, parse_dates=['t'])
                        con_current_data.close()
                        delta_prev = delta
                        delta += constants.STEP_OF_BACK_SEARCH
                        # Если больше 1 года
                        if delta > constants.BACK_SEARCH_TIME_IN_HOUR:
                            logger.info(f'За год не нашлось: {element[0]}->{element[1]}->{element[2]}')
                            error_flag = True
                            break
                    except OverflowError:
                        error_flag = True
                        logger.info(f'OverflowError: {element[0]}->{element[1]}->{element[2]}')
                        logger.info(f'begin_time = {command_datetime_begin_time}; end_time = {command_datetime_end_time}')
                        break

            if not error_flag:
                con_common_data = sqlite3.connect(constants.CLIENT_COMMON_DATA)
                logger.info(con_common_data)
                df_sqlite.to_sql(f'{constants.CLIENT_COMMON_DATA_TABLE}', con_common_data, if_exists='append', index=False)
                con_common_data.close()
                logger.info(f'successfully completed: {element[0]}->{element[1]}->{element[2]}')
            error_flag = False
            eel.setProgressBarDiscreteSignals(int((i + 1) / len(decart_product) * 100))

        try:
            con_common_data = sqlite3.connect(constants.CLIENT_COMMON_DATA)

            df_sqlite = pd.read_sql_query(
                f"SELECT * from {constants.CLIENT_COMMON_DATA_TABLE}",
                con_common_data, parse_dates=['t'])
        except Exception as e:
            logger.error(f"{constants.CLIENT_COMMON_DATA_TABLE} is empty: {e}")
            return f"Никаких данных за год не нашлось"
        finally:
            con_common_data.close()

        df_report = pd.DataFrame(
            columns=['Код сигнала (KKS)', 'Дата и время измерения', 'Значение', 'Качество',
                     'Код качества'],
            data={'Код сигнала (KKS)': df_sqlite['id'],
                  'Дата и время измерения': df_sqlite['t'],
                  'Значение': df_sqlite['val'],
                  'Качество': df_sqlite['status'],
                  'Код качества': list(map(lambda x: constants.QUALITY_DICT[x], df_sqlite['status'].to_list()))})
        df_report.to_csv(constants.CSV_DISCRETE_SLICES, index=False, encoding='utf-8')
        logger.info("data frame has been formed")

        # get_report_slice(df_report, 'аналоговых')

        shutil.copy(constants.CSV_DISCRETE_SLICES, f'{constants.WEB_DIR}discrete_slice.csv')
        logger.info("data frame is accessed for download")

        df_report['Дата и время измерения'] = df_report['Дата и время измерения'].dt.strftime('%Y-%m-%d %H:%M:%S')

        slice = json.loads(df_report.to_json(orient='records'))
        render_slice(slice)

        return slice

    global signals_greenlet
    global analog_signals_greenlet
    global discrete_signals_greenlet
    global grid_greenlet
    global analog_grid_greenlet
    global discrete_grid_greenlet
    global bounce_greenlet
    started_greenlet = [signals_greenlet, analog_signals_greenlet, discrete_signals_greenlet,
                        grid_greenlet, analog_grid_greenlet, discrete_grid_greenlet, bounce_greenlet]
    if any(started_greenlet):
        logger.warning(f"discrete_signals_greenlet is running")
        return f"Запрос уже выполняется для другого клиента. Попробуйте выполнить запрос позже"

    discrete_signals_greenlet = eel.spawn(get_discrete_signals_data_spawn, kks, values, quality, date)
    eel.gvt.joinall([discrete_signals_greenlet])
    # if discrete_signals_greenlet:
    return discrete_signals_greenlet.value


analog_grid_greenlet = None


@eel.expose
def get_analog_grid_data(kks, date_begin, date_end, interval, dimension):
    logger.info(f"get_analog_grid_data({kks}, {date_begin}, {date_end}, {interval}, {dimension})")

    def get_analog_grid_data_spawn(kks, date_begin, date_end, interval, dimension):
        logger.info(f"get_analog_grid_data_spawn({kks}, {date_begin}, {date_end}, {interval}, {dimension})")

        # Сохранение датчика с KKS
        csv_tag_KKS = pd.DataFrame(data=kks)
        csv_tag_KKS.to_csv(constants.CLIENT_KKS, index=False, header=None)

        # Формирование команд для запуска бинарника historian и скрипта slices.py
        command_datetime_begin_time = parse(date_begin).strftime("%Y-%m-%d %H:%M:%S")
        command_datetime_end_time = parse(date_end).strftime("%Y-%m-%d %H:%M:%S")

        command_datetime_begin_time_binary = parse(date_begin).strftime("%Y-%m-%dT%H:%M:%SZ")
        command_datetime_end_time_binary = parse(date_end).strftime("%Y-%m-%dT%H:%M:%SZ")

        command_string_binary = f"cd client && ./client -b {command_datetime_begin_time_binary} -e " \
                                f"{command_datetime_end_time_binary} -p 100 -t 10000 -rxw"

        delta_interval = interval * constants.DELTA_INTERVAL_IN_SECONDS[dimension]
        command_string = f'cd client && python ./slicer_for_streamlit.py -d {delta_interval} ' \
                         f'-t \"{command_datetime_begin_time}\" \"{command_datetime_end_time}\"'

        logger.info("get OPC_UA")
        logger.info(command_string_binary)

        eel.setProgressBarAnalogSignals(5)

        args = command_string_binary
        try:
            subprocess.run(args, capture_output=True, shell=True, check=True)
            eel.setProgressBarAnalogSignals(10)
        except subprocess.CalledProcessError as e:
            logger.error(e)
            return f"Произошла ошибка {str(e)}"

        logger.info("get slices")
        logger.info(command_string)

        args = command_string
        try:
            eel.setProgressBarAnalogSignals(40)
            subprocess.run(args, capture_output=True, shell=True, check=True)
            eel.setProgressBarAnalogSignals(50)
        except subprocess.CalledProcessError as e:
            logger.error(e)
            if "ValueError: sampling_period is greater than the duration between start and end" in str(e):
                logger.error("интервал больше, чем дата начала и конца")
                return f"интервал больше, чем дата начала и конца"

        df_slice_csv = pd.read_csv(constants.CLIENT_SLICES)
        df_slice_status_csv = pd.read_csv(constants.CLIENT_SLICES_STATUS)

        df_report = pd.DataFrame(df_slice_csv['timestamp'])
        df_report.rename(columns={'timestamp': 'Метка времени'}, inplace=True)

        df_report_slice = pd.DataFrame(df_slice_status_csv['timestamp'])
        df_report_slice.rename(columns={'timestamp': 'Метка времени'}, inplace=True)

        for index, kks in enumerate(df_slice_csv.columns.tolist()[1:]):
            df_report[index] = df_slice_csv[kks]
            df_report_slice[index] = df_slice_status_csv[kks]

        eel.setProgressBarAnalogSignals(70)

        logger.info(df_report)
        logger.info(df_report_slice)

        df_report.to_csv(constants.CSV_ANALOG_GRID, index=False, encoding='utf-8')
        logger.info("data frame has been formed")

        shutil.copy(constants.CSV_ANALOG_GRID, f'{constants.WEB_DIR}analog_grid.csv')
        logger.info("data frame is accessed for download")

        eel.setProgressBarAnalogSignals(90)
        code = json.loads(pd.DataFrame(data={
            '№': [i for i in range(len(df_slice_csv.columns.tolist()[1:]))],
            'Обозначение сигнала': [kks for kks in df_slice_csv.columns.tolist()[1:]]})
                          .to_json(orient='records'))

        # Разделение таблиц по группам по 5 датчикам
        separate_count = 1
        grid_separated_json_list = []
        status_separated_json_list = []

        grid_separated_json_list_single = []
        status_separated_json_list_single = []

        temp_df_slice = df_report[['Метка времени']].copy()
        temp_df_status = df_report_slice[['Метка времени']].copy()

        for kks in df_report.columns.tolist()[1:]:
            temp_df_slice[kks] = df_report[kks]
            temp_df_status[kks] = df_report_slice[kks]

            if (separate_count % constants.SEPARATED_COUNT == 0) \
                    or (separate_count == len(df_report.columns.tolist()[1:])):
                temp_json_grid = json.loads(temp_df_slice.to_json(orient='records'))
                temp_json_status = json.loads(temp_df_status.to_json(orient='records'))

                grid_separated_json_list.append(temp_json_grid)
                status_separated_json_list.append(temp_json_status)

                for index in temp_df_slice.columns.tolist()[1:]:
                    temp_json_grid_single = json.loads(temp_df_slice[['Метка времени', index]].copy()
                                                       .to_json(orient='records'))
                    temp_json_status_single = json.loads(temp_df_status[['Метка времени', index]].copy()
                                                         .to_json(orient='records'))

                    grid_separated_json_list_single.append(temp_json_grid_single)
                    status_separated_json_list_single.append(temp_json_status_single)

                temp_df_slice = df_report[['Метка времени']].copy()
                temp_df_status = df_report_slice[['Метка времени']].copy()
            separate_count += 1
        # grid, status = json.loads(df_report.to_json(orient='records')), json.loads(df_report_slice.
        #                                                                            to_json(orient='records'))

        parameters_of_request = {
            "date_begin": date_begin,
            "date_end": date_end,
            "interval": interval,
            "dimension": constants.INTERVAL_TO_LOCALE[dimension]
        }

        render_grid(code, grid_separated_json_list, status_separated_json_list,
                    grid_separated_json_list_single, status_separated_json_list_single, parameters_of_request)

        return json.loads(df_report.to_json(orient='records')), json.loads(df_report_slice.to_json(orient='records'))

    global signals_greenlet
    global analog_signals_greenlet
    global discrete_signals_greenlet
    global grid_greenlet
    global analog_grid_greenlet
    global discrete_grid_greenlet
    global bounce_greenlet
    started_greenlet = [signals_greenlet, analog_signals_greenlet, discrete_signals_greenlet,
                        grid_greenlet, analog_grid_greenlet, discrete_grid_greenlet, bounce_greenlet]
    if any(started_greenlet):
        logger.warning(f"analog_grid_greenlet is running")
        return f"Запрос уже выполняется для другого клиента. Попробуйте выполнить запрос позже"

    analog_grid_greenlet = eel.spawn(get_analog_grid_data_spawn, kks, date_begin, date_end, interval, dimension)
    eel.gvt.joinall([analog_grid_greenlet])
    # if analog_grid_greenlet:
    return analog_grid_greenlet.value


discrete_grid_greenlet = None


@eel.expose
def get_discrete_grid_data(kks, date_begin, date_end, interval, dimension):
    logger.info(f"get_discrete_grid_data({kks}, {date_begin}, {date_end}, {interval}, {dimension})")

    def get_discrete_grid_data_spawn(kks, date_begin, date_end, interval, dimension):
        logger.info(f"get_discrete_grid_data_spawn({kks}, {date_begin}, {date_end}, {interval}, {dimension})")
        # Сохранение датчика с KKS
        csv_tag_KKS = pd.DataFrame(data=kks)
        csv_tag_KKS.to_csv(constants.CLIENT_KKS, index=False, header=None)

        # Формирование команд для запуска бинарника historian и скрипта slices.py
        command_datetime_begin_time = parse(date_begin).strftime("%Y-%m-%d %H:%M:%S")
        command_datetime_end_time = parse(date_end).strftime("%Y-%m-%d %H:%M:%S")

        command_datetime_begin_time_binary = parse(date_begin).strftime("%Y-%m-%dT%H:%M:%SZ")
        command_datetime_end_time_binary = parse(date_end).strftime("%Y-%m-%dT%H:%M:%SZ")

        command_string_binary = f"cd client && ./client -b {command_datetime_begin_time_binary} -e " \
                                f"{command_datetime_end_time_binary} -p 100 -t 10000 -rxw"

        delta_interval = interval * constants.DELTA_INTERVAL_IN_SECONDS[dimension]
        command_string = f'cd client && python ./slicer_for_streamlit.py -d {delta_interval} ' \
                         f'-t \"{command_datetime_begin_time}\" \"{command_datetime_end_time}\"'

        logger.info("get OPC_UA")
        logger.info(command_string_binary)

        eel.setProgressBarDiscreteSignals(5)

        args = command_string_binary
        try:
            subprocess.run(args, capture_output=True, shell=True, check=True)
            eel.setProgressBarDiscreteSignals(10)
        except subprocess.CalledProcessError as e:
            logger.error(e)
            return f"Произошла ошибка {str(e)}"

        logger.info("get slices")
        logger.info(command_string)

        args = command_string
        try:
            eel.setProgressBarDiscreteSignals(40)
            subprocess.run(args, capture_output=True, shell=True, check=True)
            eel.setProgressBarDiscreteSignals(50)
        except subprocess.CalledProcessError as e:
            logger.error(e)
            if "ValueError: sampling_period is greater than the duration between start and end" in str(e):
                logger.error("интервал больше, чем дата начала и конца")
                return f"интервал больше, чем дата начала и конца"

        df_slice_csv = pd.read_csv(constants.CLIENT_SLICES)
        df_slice_status_csv = pd.read_csv(constants.CLIENT_SLICES_STATUS)

        df_report = pd.DataFrame(df_slice_csv['timestamp'])
        df_report.rename(columns={'timestamp': 'Метка времени'}, inplace=True)

        df_report_slice = pd.DataFrame(df_slice_status_csv['timestamp'])
        df_report_slice.rename(columns={'timestamp': 'Метка времени'}, inplace=True)

        for index, kks in enumerate(df_slice_csv.columns.tolist()[1:]):
            df_report[index] = df_slice_csv[kks]
            df_report_slice[index] = df_slice_status_csv[kks]

        eel.setProgressBarDiscreteSignals(70)

        logger.info(df_report)
        logger.info(df_report_slice)

        df_report.to_csv(constants.CSV_DISCRETE_GRID, index=False, encoding='utf-8')
        logger.info("data frame has been formed")

        shutil.copy(constants.CSV_DISCRETE_GRID, f'{constants.WEB_DIR}discrete_grid.csv')
        logger.info("data frame is accessed for download")

        eel.setProgressBarDiscreteSignals(90)
        code = json.loads(pd.DataFrame(data={
            '№': [i for i in range(len(df_slice_csv.columns.tolist()[1:]))],
            'Обозначение сигнала': [kks for kks in df_slice_csv.columns.tolist()[1:]]})
                          .to_json(orient='records'))

        # Разделение таблиц по группам по 5 датчикам
        separate_count = 1
        grid_separated_json_list = []
        status_separated_json_list = []

        grid_separated_json_list_single = []
        status_separated_json_list_single = []

        temp_df_slice = df_report[['Метка времени']].copy()
        temp_df_status = df_report_slice[['Метка времени']].copy()

        for kks in df_report.columns.tolist()[1:]:
            temp_df_slice[kks] = df_report[kks]
            temp_df_status[kks] = df_report_slice[kks]

            if (separate_count % constants.SEPARATED_COUNT == 0) \
                    or (separate_count == len(df_report.columns.tolist()[1:])):
                temp_json_grid = json.loads(temp_df_slice.to_json(orient='records'))
                temp_json_status = json.loads(temp_df_status.to_json(orient='records'))

                grid_separated_json_list.append(temp_json_grid)
                status_separated_json_list.append(temp_json_status)

                for index in temp_df_slice.columns.tolist()[1:]:
                    temp_json_grid_single = json.loads(temp_df_slice[['Метка времени', index]].copy()
                                                       .to_json(orient='records'))
                    temp_json_status_single = json.loads(temp_df_status[['Метка времени', index]].copy()
                                                         .to_json(orient='records'))

                    grid_separated_json_list_single.append(temp_json_grid_single)
                    status_separated_json_list_single.append(temp_json_status_single)

                temp_df_slice = df_report[['Метка времени']].copy()
                temp_df_status = df_report_slice[['Метка времени']].copy()
            separate_count += 1
        # grid, status = json.loads(df_report.to_json(orient='records')), json.loads(df_report_slice.
        #                                                                            to_json(orient='records'))

        parameters_of_request = {
            "date_begin": date_begin,
            "date_end": date_end,
            "interval": interval,
            "dimension": constants.INTERVAL_TO_LOCALE[dimension]
        }

        render_grid(code, grid_separated_json_list, status_separated_json_list,
                    grid_separated_json_list_single, status_separated_json_list_single, parameters_of_request)

        return json.loads(df_report.to_json(orient='records')), json.loads(df_report_slice.to_json(orient='records'))

    global signals_greenlet
    global analog_signals_greenlet
    global discrete_signals_greenlet
    global grid_greenlet
    global analog_grid_greenlet
    global discrete_grid_greenlet
    global bounce_greenlet
    started_greenlet = [signals_greenlet, analog_signals_greenlet, discrete_signals_greenlet,
                        grid_greenlet, analog_grid_greenlet, discrete_grid_greenlet, bounce_greenlet]
    if any(started_greenlet):
        logger.warning(f"discrete_grid_greenlet is running")
        return f"Запрос уже выполняется для другого клиента. Попробуйте выполнить запрос позже"

    discrete_grid_greenlet = eel.spawn(get_discrete_grid_data_spawn, kks, date_begin, date_end, interval, dimension)
    eel.gvt.joinall([discrete_grid_greenlet])
    # if discrete_grid_greenlet:
    return discrete_grid_greenlet.value


bounce_greenlet = None


@eel.expose
def get_bounce_signals_data(template, date, interval, dimension, top):
    logger.info(f"get_bounce_signals_data({template}, {date}, {interval}, {dimension}, {top})")

    def get_bounce_signals_data_spawn(template, date, interval, dimension, top):
        logger.info(f"get_bounce_signals_data_spawn({template}, {date}, {interval}, {dimension}, {top})")

        kks = get_discrete_kks_by_mask(template)
        if not kks:
            return f"По шаблону ничего не найдено"

        # Сохранение датчика с KKS
        csv_tag_KKS = pd.DataFrame(data=kks)
        csv_tag_KKS.to_csv(constants.CLIENT_KKS, index=False, header=None)

        # Формирование команд для запуска бинарника historian
        delta_interval = interval * constants.DELTA_INTERVAL_IN_SECONDS[dimension]
        command_datetime_begin_time = (parse(date) - datetime.timedelta(seconds=delta_interval)).strftime("%Y-%m-%dT%H:%M:%SZ")
        command_datetime_end_time = parse(date).strftime("%Y-%m-%dT%H:%M:%SZ")

        command_string = f"cd client && ./client -b {command_datetime_begin_time} -e " \
                         f"{command_datetime_end_time} -p 100 -t 1 -xw"

        logger.info("get OPC_UA")
        logger.info(command_string)

        eel.setProgressBarBounceSignals(5)

        args = command_string
        try:
            subprocess.run(args, capture_output=True, shell=True, check=True)
            eel.setProgressBarBounceSignals(10)
        except subprocess.CalledProcessError as e:
            logger.error(e)
            return f"Произошла ошибка {str(e)}"

        logger.info(f'client finished')

        # Достаем фрейм из sqlite
        con_current_data = sqlite3.connect(constants.CLIENT_DATA)
        query_string = f"SELECT * from {constants.CLIENT_DYNAMIC_TABLE}"

        df_sqlite = pd.read_sql_query(
            query_string,
            con_current_data, parse_dates=['t'])
        con_current_data.close()

        if df_sqlite.empty:
            msg = "Не нашлось ни одного значения из выбранных датчиков. Возможно интервал слишком мал."
            logger.info(msg)
            return msg

        # df_counts = pd.DataFrame(kks, columns=['Наименование датчика'])
        # df_counts['Частота'] = df_sqlite['id'].value_counts()
        df_counts = pd.DataFrame()
        df_counts['Частота'] = df_sqlite['id'].value_counts()
        df_counts.index.name = 'Наименование датчика'
        df_counts['Наименование датчика'] = df_counts.index.values.tolist()

        logger.info(df_counts[:int(top)])
        return json.loads(df_counts[:int(top)].to_json(orient='records'))

    global signals_greenlet
    global analog_signals_greenlet
    global discrete_signals_greenlet
    global grid_greenlet
    global analog_grid_greenlet
    global discrete_grid_greenlet
    global bounce_greenlet
    started_greenlet = [signals_greenlet, analog_signals_greenlet, discrete_signals_greenlet,
                        grid_greenlet, analog_grid_greenlet, discrete_grid_greenlet, bounce_greenlet]
    if any(started_greenlet):
        logger.warning(f"bounce_greenlet is running")
        return f"Запрос уже выполняется для другого клиента. Попробуйте выполнить запрос позже"

    bounce_greenlet = eel.spawn(get_bounce_signals_data_spawn, template, date, interval, dimension, top)
    eel.gvt.joinall([bounce_greenlet])
    # if bounce_greenlet:
    return bounce_greenlet.value


def server_run_thread():
    while True:
        eel.sleep(1.0)


def on_close(page, sockets):
    """Callback close Eel application."""
    logger.info(page)
    logger.info(sockets)


def start_eel(develop):
    """Start Eel with either production or development configuration."""
    logger.info("before init")

    if develop:
        directory = f'vue{os.sep}src'
        app = None
        page = {'port': 3000}
    else:
        directory = f'web'
        app = 'chrome-app'
        page = ''

    eel.init(directory, ['.js', '.html'])
    logger.info("after init")

    # These will be queued until the first connection is made, but won't be repeated on a page reload
    eel_kwargs = dict(
        host='10.23.23.31',
        port=8005,
        size=(1920, 1080),
    )
    try:
        logger.info("start")
        # eel.spawn(server_run_thread)
        eel.start(page, block=False, mode=app, shutdown_delay=5.0, callback=on_close, **eel_kwargs)

        while True:
            # print("I'm a main loop")
            eel.sleep(1.0)
    except EnvironmentError:
        # If Chrome isn't found, fallback to Microsoft Edge on Win10 or greater
        if sys.platform in ['win32', 'win64'] and int(platform.release()) >= 10:
            eel.start(page, mode='edge', shutdown_delay=5.0, callback=on_close, **eel_kwargs)
        else:
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="start eel + vue 3 web-application")
    parser.add_argument("-v", "--version", action="version", help="print version", version=f'{VERSION}')

    try:
        opt = parser.parse_args()
    except SystemExit:
        logger.info(f'{VERSION} eel + vue 3 web-application version')
        exit(0)

    check_correct_application_structure()

    # Пытаемся загрузить kks_all.csv если он существует
    try:
        KKS_ALL = pd.read_csv(constants.DATA_KKS_ALL, header=None, sep=';')
    except FileNotFoundError as e:
        logger.info(e)
        KKS_ALL = pd.DataFrame()

    # Pass any second argument to enable debugging
    start_eel(develop=len(sys.argv) == 2)
