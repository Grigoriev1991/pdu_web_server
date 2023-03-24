import os
import sys
import logging
import threading
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI


root_path = os.path.dirname(os.path.dirname(__file__))
if root_path not in sys.path:
    sys.path.append(root_path)


#  Logging settings
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('server.log', maxBytes=50000000, backupCount=5)
formatter = logging.Formatter(
    '%(asctime)s: [%(levelname)s] [%(lineno)d]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


#  Create server
app = FastAPI()
pdu = None
locker = threading.RLock()


def check_and_set():
    import run_server
    if pdu.get_connection_status() is False:
        logger.info('Call set_true func')
        return run_server.set_true()


#  Communication logic
@app.get('/api/pdu/info/')
def get_pdu_device_info():
    with locker:
        logger.info('request PDU info')
        if pdu.pdu_connection_status():
            check_and_set()
            if pdu.port_count == 0:
                pdu.port_count = len(pdu.pdu_status()['io']['do'])
            logger.info('PDU info sent')
            return pdu.pdu_info()
        else:
            return {'pdu': {
                'connection': pdu.get_connection_status(),
                'adress': pdu.adress, 'port count': pdu.port_count}}


@app.get('/')
def get_inf():
    return {'yes': 'work'}


@app.get("/api/pdu/status/")
def get_pdu_curr_stat():
    with locker:
        try:
            logger.info('request PDU status')
            status = pdu.pdu_status()
            if status:
                check_and_set()
            logger.info('PDU status sent')
            return status
        except Exception:
            logger.exception('PDU status error')


@app.get("/api/slot/{id}/status")
def get_port_curr_stat(id: int):
    with locker:
        try:
            logger.info(f'request port DO{id} STATUS')
            status = pdu.pdu_port_status(slot_id=id)
            if status:
                check_and_set()
                logger.info(f'port DO{id} STATUS send')
                return status
            else:
                logger.info(f'NO port DO{id} STATUS')
        except Exception:
            logger.exception(f'port DO{id} get STATUS error')


@app.put("/api/slot/{id}/on/")
def pdu_port_on(id: int):
    with locker:
        try:
            logger.info(f'request to ENABLE port DO{id}')
            status = pdu.pdu_port_up(slot_id=id)
            if status:
                check_and_set()
                logger.info(f'port DO{id} ENABLE')
                return status.status_code
            else:
                logger.exception(f'port DO{id} ENABLE error')
                return status
        except Exception:
            logger.exception(f'port DO{id} ENABLE error')


@app.put("/api/slot/{id}/off/")
def pdu_port_off(id: int):
    with locker:
        try:
            logger.info(f'request to DISABLE port DO{id}')
            status = pdu.pdu_port_down(slot_id=id)
            if status:
                check_and_set()
                logger.info(f'port DO{id} DISABLE')
                return status.status_code
            else:
                logger.info(f'port DO{id} not DISABLE')
            return status
        except Exception:
            logger.exception(f'port DO{id} DISABLE error')


@app.put("/api/slot/{id}/reset/")
def pdu_port_reset(id: int):
    with locker:
        try:
            logger.info(f'request to RESET port DO{id}')
            status = pdu.pdu_port_reset(slot_id=id)
            if status:
                check_and_set()
                logger.info(f'port DO{id} RESET')
                return status.status_code
            else:
                logger.info(f'port DO{id} not RESET')
            return status
        except Exception:
            logger.exception(f'port DO{id} RESET error')


@app.put("/api/slot/{id}/toggle/")
def pdu_port_toggle(id: int):
    with locker:
        try:
            logger.info(f'request to TOGGLE port DO{id}')
            status = pdu.pdu_port_toggle(slot_id=id)
            if status:
                check_and_set()
                logger.info(f'port DO{id} TOGGLE')
                return status.status_code
            else:
                logger.info(f'port DO{id} not TOGGLE')
            return status
        except Exception:
            logger.exception(f'port DO{id} TOGGLE error')
