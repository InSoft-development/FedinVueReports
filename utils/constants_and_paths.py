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

WEB_DIR = f'web{os.sep}'

CLIENT_DIR = f'client{os.sep}'
CLIENT_BINARY = f'{CLIENT_DIR}client_lesson02.so'
CLIENT_COMMON_DATA = f'{CLIENT_DIR}common_data.sqlite'
CLIENT_DATA = f'{CLIENT_DIR}data.sqlite'
CLIENT_KKS = f'{CLIENT_DIR}kks.csv'
CLIENT_SLICES = f'{CLIENT_DIR}slices.csv'
CLIENT_SLICES_STATUS = f'{CLIENT_DIR}slices_status.csv'
CLIENT_SLICER_SCRIPT = f'{CLIENT_DIR}slicer_for_streamlit.py'


JINJA = f'jinja{os.sep}'
JINJA_TEMPLATE = f'{JINJA}template{os.sep}'
JINJA_PYLIB = f'{JINJA}pylib{os.sep}'

FEATURES_PALETTE = ['#ff7f0e', '#d62728', '#9467bd', '#52a852', '#10E8E7']
MAIN_SIGNAL_COLOR = px.colors.qualitative.Plotly[0]
