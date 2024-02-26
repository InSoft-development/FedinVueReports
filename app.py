import os
import platform
import argparse
import sys

import eel
import shutil

import sqlite3
import subprocess
import shlex
import itertools

import pandas as pd

import json
from loguru import logger
import datetime
from dateutil.parser import parse

from utils.correct_start import check_correct_application_structure
import utils.constants_and_paths as constants

VERSION = '1.0.0'

# Use latest version of Eel from parent directory
sys.path.insert(1, '../../')


@eel.expose
def get_analog_kks():
    logger.info(f"get_analog_kks()")

    with open(f'{constants.DATA_ANALOG}', 'r', encoding='utf8') as f:
        analog_kks = f.readlines()

    # Приведение в верному формату датчиков с KKS
    analog_kks = [i[:-1] for i in analog_kks]
    return analog_kks


@eel.expose
def get_discrete_kks_by_mask(mask):
    logger.info(f"get_discrete_kks_by_mask({mask})")
    if mask is None:
        return []
    discrete_kks = pd.read_csv(constants.DATA_DISCRETE, header=None)
    discrete_kks = discrete_kks[discrete_kks[0].str.contains(mask, regex=True)][0].tolist()
    return discrete_kks


@eel.expose
def get_analog_signals_data(kks, quality, date):
    logger.info(f"get_analog_signals_data({kks}, {quality}, {date})")
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
        command_string = f"cd client && ./client_lesson02.so -b {command_datetime_begin_time} -e " \
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

                    command_string = f"cd client && ./client_lesson02.so -b {command_datetime_begin_time} -e " \
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
                    logger.info(f'begin_time = {command_datetime_begin_time}; end_time = {command_datetime_end_time}')
                    break

        if not error_flag:
            con_common_data = sqlite3.connect(constants.CLIENT_COMMON_DATA)
            logger.info(con_common_data)
            df_sqlite.to_sql(f'{constants.CLIENT_COMMON_DATA_TABLE}', con_common_data, if_exists='append', index=False)
            con_common_data.close()
            logger.info(f'successfully completed: {element[0]}->{element[1]}')
        error_flag = False
        eel.setProgressBarAnalogSignals(int((i+1)/len(decart_product) * 100))

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
        columns=['Код сигнала (AKS)', 'Дата и время измерения', 'Значение', 'Качество',
                 'Код качества'],
        data={'Код сигнала (AKS)': df_sqlite['id'],
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
    return json.loads(df_report.to_json(orient='records'))


@eel.expose
def get_discrete_signals_data(kks, values, quality, date):
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
        command_string = f"cd client && ./client_lesson02.so -b {command_datetime_begin_time} -e " \
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

                    command_string = f"cd client && ./client_lesson02.so -b {command_datetime_begin_time} -e " \
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
        columns=['Код сигнала (AKS)', 'Дата и время измерения', 'Значение', 'Качество',
                 'Код качества'],
        data={'Код сигнала (AKS)': df_sqlite['id'],
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
    return json.loads(df_report.to_json(orient='records'))


@eel.expose
def get_analog_grid_data(kks, date_begin, date_end, interval, dimension):
    logger.info(f"get_analog_grid_data({kks}, {date_begin}, {date_end}, {interval}, {dimension})")

    # Сохранение датчика с KKS
    csv_tag_KKS = pd.DataFrame(data=kks)
    csv_tag_KKS.to_csv(constants.CLIENT_KKS, index=False, header=None)

    # Формирование команд для запуска бинарника historian и скрипта slices.py
    command_datetime_begin_time = parse(date_begin).strftime("%Y-%m-%d %H:%M:%S")
    command_datetime_end_time = parse(date_end).strftime("%Y-%m-%d %H:%M:%S")

    command_datetime_begin_time_binary = parse(date_begin).strftime("%Y-%m-%dT%H:%M:%SZ")
    command_datetime_end_time_binary = parse(date_end).strftime("%Y-%m-%dT%H:%M:%SZ")

    command_string_binary = f"cd client && ./client_lesson02.so -b {command_datetime_begin_time_binary} -e " \
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

    # get_report_grid(code_kks, colored_df_list, colored_dict_list, 'аналоговых')

    return json.loads(df_report.to_json(orient='records')), json.loads(df_report_slice.to_json(orient='records'))


@eel.expose
def get_discrete_grid_data(kks, date_begin, date_end, interval, dimension):
    logger.info(f"get_discrete_grid_data({kks}, {date_begin}, {date_end}, {interval}, {dimension})")

    # Сохранение датчика с KKS
    csv_tag_KKS = pd.DataFrame(data=kks)
    csv_tag_KKS.to_csv(constants.CLIENT_KKS, index=False, header=None)

    # Формирование команд для запуска бинарника historian и скрипта slices.py
    command_datetime_begin_time = parse(date_begin).strftime("%Y-%m-%d %H:%M:%S")
    command_datetime_end_time = parse(date_end).strftime("%Y-%m-%d %H:%M:%S")

    command_datetime_begin_time_binary = parse(date_begin).strftime("%Y-%m-%dT%H:%M:%SZ")
    command_datetime_end_time_binary = parse(date_end).strftime("%Y-%m-%dT%H:%M:%SZ")

    command_string_binary = f"cd client && ./client_lesson02.so -b {command_datetime_begin_time_binary} -e " \
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

    # get_report_grid(code_kks, colored_df_list, colored_dict_list, 'дискретных')

    return json.loads(df_report.to_json(orient='records')), json.loads(df_report_slice.to_json(orient='records'))


@eel.expose
def get_bounce_signals_data(template, date, interval, dimension, top):
    logger.info(f"get_bounce_signals_data({template}, {date}, {interval}, {dimension}, {top})")

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

    command_string = f"cd client && ./client_lesson02.so -b {command_datetime_begin_time} -e " \
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
        eel.start(page, mode=app, shutdown_delay=5.0, callback=on_close, **eel_kwargs)
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

    # Pass any second argument to enable debugging
    start_eel(develop=len(sys.argv) == 2)
