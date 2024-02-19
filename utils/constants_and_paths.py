"""
Модуль содержит все использеумые в приложении константы
"""
import os
import plotly.express as px

DATA_DIRECTORY = f'data{os.sep}'
DATA_ANALOG = f'{DATA_DIRECTORY}data_AM.txt'
DATA_DISCRETE = f'{DATA_DIRECTORY}democub_all.csv'

REPORTS_DIRECTORY = f'reports{os.sep}'
REPORTS_CUSTOM = f'{REPORTS_DIRECTORY}custom{os.sep}'

REPORTS_ANALOG_SLICES = f'{REPORTS_DIRECTORY}analog_slice.pdf'
REPORTS_DISCRETE_SLICES = f'{REPORTS_DIRECTORY}discrete_slice.pdf'
REPORTS_ANALOG_GRID = f'{REPORTS_DIRECTORY}analog_grid.pdf'
REPORTS_DISCRETE_GRID = f'{REPORTS_DIRECTORY}discrete_grid.pdf'
REPORTS_BOUNCE = f'{REPORTS_DIRECTORY}bounce.pdf'

CSV_ANALOG_SLICES = f'{REPORTS_DIRECTORY}analog_slice.csv'
CSV_DISCRETE_SLICES = f'{REPORTS_DIRECTORY}discrete_slice.csv'
CSV_ANALOG_GRID = f'{REPORTS_DIRECTORY}analog_grid.csv'
CSV_DISCRETE_GRID = f'{REPORTS_DIRECTORY}discrete_grid.csv'
CSV_BOUNCE = f'{REPORTS_DIRECTORY}bounce.csv'

WEB_DIR = f'web{os.sep}'

CLIENT_DIR = f'client{os.sep}'
CLIENT_BINARY = f'{CLIENT_DIR}client_lesson02.so'
CLIENT_COMMON_DATA = f'{CLIENT_DIR}common_data.sqlite'
CLIENT_COMMON_DATA_TABLE = f'common_data'
CLIENT_DYNAMIC_TABLE = f'dynamic_data'
CLIENT_DATA = f'{CLIENT_DIR}data.sqlite'
CLIENT_KKS = f'{CLIENT_DIR}kks.csv'
CLIENT_SLICES = f'{CLIENT_DIR}slices.csv'
CLIENT_SLICES_STATUS = f'{CLIENT_DIR}slices_status.csv'
CLIENT_SLICER_SCRIPT = f'{CLIENT_DIR}slicer_for_streamlit.py'

JINJA = f'jinja{os.sep}'
JINJA_TEMPLATE = f'{JINJA}template{os.sep}'
JINJA_PYLIB = f'{JINJA}pylib{os.sep}'

QUALITY = ["8 - (BNC) - ОТКАЗ СВЯЗИ (TIMEOUT)",
           "16 - (BSF) - ОТКАЗ ПАРАМ",
           "24 - (BCF) - ОТКАЗ СВЯЗИ",
           "28 - (BOS) - ОТКАЗ ОБСЛУЖ",
           "88 - (BLC) - ОТКАЗ РАСЧЕТ",
           "192 - (GOD) – ХОРОШ",
           "200 - (GLC) - ХОРОШ РАСЧЕТ",
           "216 - (GFO) - ХОРОШ ИМИТИР",
           "224 - (GLT) - ХОРОШ ЛОКАЛ ВРЕМ"]

QUALITY_DICT = {'BadNoCommunication': 8,
                'BadSensorFailure': 16,
                'BadCommunicationFailure': 24,
                'BadDeviceFailure': 28,
                'UncertainLastUsableValue': 88,
                'Good': 192,
                'GoodХОРОШ РАСЧЕТ': 200,
                'GoodХОРОШ ИМИТИР': 216,
                'GoodLocalTime': 224,
                }
QUALITY_CODE_DICT = {'8 - (BNC) - ОТКАЗ СВЯЗИ (TIMEOUT)': 'BadNoCommunication',
                     '16 - (BSF) - ОТКАЗ ПАРАМ': 'BadSensorFailure',
                     '24 - (BCF) - ОТКАЗ СВЯЗИ': 'BadCommunicationFailure',
                     '28 - (BOS) - ОТКАЗ ОБСЛУЖ': 'BadDeviceFailure',
                     '88 - (BLC) - ОТКАЗ РАСЧЕТ': 'UncertainLastUsableValue',
                     '192 - (GOD) – ХОРОШ': 'Good',
                     '200 - (GLC) - ХОРОШ РАСЧЕТ': 'GoodХОРОШ РАСЧЕТ',
                     '216 - (GFO) - ХОРОШ ИМИТИР': 'GoodХОРОШ ИМИТИР',
                     '224 - (GLT) - ХОРОШ ЛОКАЛ ВРЕМ': 'GoodLocalTime'
                     }

BAD_CODE_LIST = ['BadNoCommunication', 'BadSensorFailure', 'BadCommunicationFailure',
                 'BadDeviceFailure', 'UncertainLastUsableValue']
BAD_NUMERIC_CODE_LIST = [8, 16, 24, 28, 88]

BACK_SEARCH_TIME_IN_HOUR = 8760  # Предельное время поиска в глубину в часах
STEP_OF_BACK_SEARCH = 720  # Глубина поиска в архивах

FEATURES_PALETTE = ['#ff7f0e', '#d62728', '#9467bd', '#52a852', '#10E8E7']
MAIN_SIGNAL_COLOR = px.colors.qualitative.Plotly[0]
