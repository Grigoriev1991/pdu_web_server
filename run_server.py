import uvicorn
from http import HTTPStatus
from time import sleep
import threading
import logging
from logging.handlers import RotatingFileHandler

import server_api.server
from pdu_shell.iologik_shell import PDU
from server_api.server import app


#  Logging settings
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('run_server.log', maxBytes=50000000, backupCount=5)
formatter = logging.Formatter(
    '%(asctime)s: [%(levelname)s] [%(lineno)d]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


#  Main logic
def create_pdu(ip):
    adress = f'http://{ip}'
    pdu = PDU(adress=adress)
    logger.info('PDU object create')
    try:
        connection = pdu.pdu_connection_status()
        if connection == HTTPStatus.OK:
            pdu.set_connection_status()
            logger.info('connection established at createion PDU')
        else:
            logger.info('PDU connection false')
    except Exception:
        logger.exception('PDU object create ERROR')
    return pdu


def set_true():
    server_api.server.pdu.set_connection_status()
    server_api.server.pdu.event.set()
    logger.info('connection established at set_true()')


def run_api_server(host="0.0.0.0", port=9090):
    logger.info('fastapi server started')
    uvicorn.run(app, host=host, port=port)


def polling_pdu():
    while True:
        if server_api.server.pdu.get_connection_status():
            try:
                connect = server_api.server.pdu.pdu_connection_status()
                if connect == HTTPStatus.OK:
                    sleep(1)
                    print('connect OK')
                else:
                    print(f'connection status: {connect}')
                    server_api.server.pdu.set_connection_status()
                    server_api.server.pdu.event.clear()
                    server_api.server.pdu.event.wait()
            except Exception:
                logger.exception('ERROR polling PDU')


if __name__ == '__main__':
    logger.info('run_server.py start')
    server_api.server.pdu = create_pdu(ip='2.2.8.8')

    server = threading.Thread(
        target=run_api_server, daemon=True, name='server'
    )
    server.start()

    polling = threading.Thread(
        target=polling_pdu, daemon=True, name='polling'
    )
    polling.start()
    while True:
        sleep(1)
