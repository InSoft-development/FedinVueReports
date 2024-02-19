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
    df_report.to_csv(constants.CSV_ANALOG_SLICES, index=False)
    logger.info("data frame has been formed")

    # get_report_slice(df_report, 'аналоговых')
    #
    # with export_pdf_col:
    #     with open(REPORT_FILE, "rb") as pdf_file:
    #         PDFbyte = pdf_file.read()
    #     export_pdf_button = st.download_button("Загрузить отчет", data=PDFbyte,
    #                                            file_name=PDF_FILE_NAME,
    #                                            key="download_report_button_",
    #                                            mime="application/octet-stream")
    #
    # with csv_result_col:
    #     result_csv = convert_df(df_report)
    #     csv_result_button = st.download_button("Загрузить CSV", data=result_csv, file_name=CSV_NAME_RESULT_FILE,
    #                                            mime='text/csv')
    df_report['Дата и время измерения'] = df_report['Дата и время измерения'].dt.strftime('%Y-%m-%d %H:%M:%S')
    return json.loads(df_report.to_json(orient='records'))


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
