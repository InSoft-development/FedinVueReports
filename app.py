import os
import platform
import argparse
import sys

import eel
import shutil

import pandas as pd

import json
from loguru import logger
import datetime
from dateutil import parser as pars

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
        host='localhost',
        port=8000,
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
