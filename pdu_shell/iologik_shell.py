import os
import sys
import json
from http import HTTPStatus
from time import sleep
import threading
import logging
from logging.handlers import RotatingFileHandler


import requests


root_path = os.path.dirname(os.path.dirname(__file__))
if root_path not in sys.path:
    sys.path.append(root_path)


#  Logging settings
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('iologik.log', maxBytes=50000000, backupCount=5)
formatter = logging.Formatter(
    '%(asctime)s: [%(levelname)s] [%(lineno)d]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


event = threading.Event()
locker = threading.RLock()


class PDU:
    """Describes the PDU devise"""
    def __init__(self, adress):
        self.adress = adress
        self.__connection_status = False
        self.event: threading.Event = event
        self.headers = {
                        "Content-Type": "application/json",
                        "Accept": "vdn.dac.v1"
                        }
        self.port_count = 0
        logger.info('Create PDU object')

    def get_connection_status(self):
        with locker:
            return self.__connection_status

    def set_connection_status(self):
        with locker:
            if self.__connection_status is False:
                self.__connection_status = True
            else:
                self.__connection_status = False

    def pdu_connection_status(self):
        try:
            logger.debug('check connection status')
            response = requests.get(
                f'{self.adress}/api/slot/0/io/do', headers=self.headers,
                timeout=0.5
            )
            logger.debug('connection status OK')
            return response.status_code
        except Exception:
            logger.exception('error from connect status')
            return None

    def pdu_info(self):
        try:
            logger.info('request pdu info')
            info = requests.get(
                f'{self.adress}/api/slot/0/sysInfo/device',
                headers=self.headers, timeout=0.5
            )
            if info.status_code == HTTPStatus.OK:
                info = info.json()
                info['sysInfo']['device'][0].setdefault('ip', self.adress.split('//')[1])
                info['sysInfo']['device'][0].setdefault('port count', self.port_count)
                info['sysInfo']['device'][0].setdefault('connection', self.get_connection_status())
                logger.info('pdu info send')
                return info
        except Exception:
            logger.exception('error from pdu_info')
            return None

    def pdu_status(self) -> dict:
        try:
            logger.info('requset pdu status')
            response = requests.get(
                f'{self.adress}/api/slot/0/io/do', headers=self.headers,
                timeout=0.5
            )
            if response.status_code == HTTPStatus.OK:
                logger.info('pdu status send')
                return response.json()
        except Exception:
            logger.exception('error from pdu status')
            return None

    def pdu_port_status(self, slot_id):
        logger.info('request pdu port status')
        response = self.pdu_status()
        if response:
            logger.info('pdu port status send')
            return response['io']['do'][slot_id]
        else:
            logger.error('pdu port status NOT send')
            return None

    def pdu_port_up(self, slot_id):
        logger.info('request port UP')
        data = self.pdu_status()
        if data:
            data['io']['do'][slot_id].update({'doStatus': 1})
            response = requests.put(
                f'{self.adress}/api/slot/0/io/do', data=json.dumps(data),
                headers=self.headers, timeout=0.5,
            )
        if response.status_code == HTTPStatus.OK:
            logger.info('port UP')
            return response
        logger.error('port on failed')
        return None

    def pdu_port_down(self, slot_id):
        logger.info('request port DOWN')
        data = self.pdu_status()
        if data:
            data['io']['do'][slot_id].update({'doStatus': 0})
            response = requests.put(
                f'{self.adress}/api/slot/0/io/do', data=json.dumps(data),
                headers=self.headers, timeout=0.5
            )
        if response.status_code == HTTPStatus.OK:
            logger.info('port DOWN')
            return response
        logger.error('port down failed')
        return None

    def pdu_port_reset(self, slot_id):
        logger.info('request port RESET')
        curr_stat = self.pdu_port_status(slot_id)
        if curr_stat and curr_stat['doStatus'] == 1:
            if self.pdu_port_down(slot_id) == HTTPStatus.OK:
                sleep(0.1)
                logger.info('port RESET')
                return self.pdu_port_up(slot_id)
        else:
            if curr_stat:
                logger.info('port has been disabled, is now enabled')
                return self.pdu_port_up(slot_id)
            logger.error('port reset failed')
            return None

    def pdu_port_toggle(self, slot_id):
        logger.info('request port TOGGLE')
        curr_stat = self.pdu_port_status(slot_id)
        if curr_stat and curr_stat['doStatus'] == 0:
            logger.info('port TOGGLE')
            return self.pdu_port_up(slot_id)
        else:
            if curr_stat:
                logger.info('port TOGGLE')
                return self.pdu_port_down(slot_id)
            logger.error('port toggle failed')
            return None
