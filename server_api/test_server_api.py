import os
import sys

import unittest
from unittest.mock import Mock, patch
from http import HTTPStatus


root_path = os.path.dirname(__file__)
if root_path not in sys.path:
    sys.path.append(root_path)


import server
import run_server
import data_for_test_server
from pdu_shell.iologik_shell import PDU


class TestPDU(unittest.TestCase):
    def setUp(self) -> None:
        '''create a pdu test object'''
        server.pdu = PDU(adress='http://0.0.0.0')
        server.pdu.port_count = 16

    @patch('run_server.set_true')
    def test_check_and_set_call_set_true(self, mock_set):
        server.pdu.__connection_status = False
        server.check_and_set()
        assert mock_set.called

    @patch('run_server.set_true')
    def test_check_and_set_not_call_set_true(self, mock_set):
        server.pdu.__connection_status = True
        server.check_and_set()
        assert mock_set.not_called

    @patch('server.check_and_set')
    @patch('server.pdu.pdu_connection_status')
    def test_get_pdu_device_info_call_check_set(self, mock_pdu, mock_check):
        mock_pdu.return_value = HTTPStatus.OK
        server.get_pdu_device_info()
        assert mock_check.called

    @patch('server.check_and_set')  # Just mock for continue
    @patch('server.pdu.pdu_status')
    @patch('server.pdu.pdu_connection_status')
    def test_get_pdu_device_info_port_count(self, mock_pdu, mock_port_count, mock):
        mock_pdu.return_value = HTTPStatus.OK
        server.pdu.port_count = 0
        server.get_pdu_device_info()
        assert mock_port_count.called

    @patch('server.check_and_set')  # Just mock for continue
    @patch('server.pdu.pdu_info')
    @patch('server.pdu.pdu_connection_status')
    def test_get_pdu_device_info_ret_val(self, mock_pdu, mock_ret_val, mock):
        mock_pdu.return_value = HTTPStatus.OK
        server.pdu.port_count = 16
        mock_ret_val.return_value = data_for_test_server.pdu_info_ret_val
        value = server.get_pdu_device_info()
        self.assertIsInstance(value, dict)

    @patch('server.check_and_set')  # Just mock for continue
    @patch('server.pdu.pdu_connection_status')
    def test_get_pdu_device_info_ret_val_not_connect(
        self, mock_pdu, mock
    ):
        mock_pdu.return_value = None
        server.pdu.port_count = 0
        value = server.get_pdu_device_info()
        self.assertIsInstance(value, dict)

    @patch('server.pdu.pdu_status')
    def test_get_pdu_curr_stat(self, mock_stat):
        server.get_pdu_curr_stat()
        assert mock_stat.called

    @patch('server.pdu.pdu_status')
    @patch('server.check_and_set')
    def test_get_pdu_curr_stat_call_check(self, mock_stat, mock_check):
        mock_stat.return_value = True
        server.get_pdu_curr_stat()
        assert mock_check.called

    @patch('server.check_and_set')  # Just mock for continue
    @patch('server.pdu.pdu_status')
    def test_get_pdu_curr_stat_correct_resp(self, mock_stat, mock):
        mock_stat.return_value = data_for_test_server.pdu_status_response
        res = server.get_pdu_curr_stat()
        self.assertIsInstance(res, dict)

    @patch('server.pdu.pdu_port_status')
    def test_get_port_curr_stat(self, mock_prot_stat):
        slot_id = 11
        server.get_port_curr_stat(slot_id)
        assert mock_prot_stat.called

    @patch('server.pdu.pdu_port_status')
    @patch('server.check_and_set')
    def test_get_port_curr_stat_call_check(self, mock_check, mock_stat):
        slot_id = 13
        mock_stat.return_value = True
        server.get_port_curr_stat(slot_id)
        assert mock_check.called

    @patch('server.pdu.pdu_port_status')
    @patch('server.check_and_set')
    def test_get_port_curr_stat_check_resp(self, mock_check, mock_stat):
        slot_id = 13
        mock_stat.return_value = data_for_test_server.pdu_port_status
        res = server.get_port_curr_stat(slot_id)
        self.assertIsInstance(res, dict)

    @patch('server.pdu.pdu_port_up')
    def test_pdu_port_on(self, mock_port_up):
        slot_id = 12
        server.pdu_port_on(slot_id)
        assert mock_port_up.called_with(slot_id)

    @patch('server.pdu.pdu_port_up')
    @patch('server.check_and_set')
    def test_pdu_port_on_call_check(self, mock_check, mock_up):
        mock_up.return_value = True
        slot_id = 12
        server.pdu_port_on(slot_id)
        assert mock_check.called

    # @patch('server.pdu.pdu_port_up')
    # @patch('server.check_and_set')  # Just mock for continue
    # def test_pdu_port_on_return_value(self, mock, mock_up):
    #     slot_id = 11
    #     mock_obj = Mock()
    #     mock_obj.status_code = HTTPStatus.OK
    #     mock_up.return_value = mock_obj
    #     res = server.pdu_port_on(slot_id)
    #     self.assertEqual(res.status_code, HTTPStatus.OK)



    @patch('server.pdu.pdu_port_down')
    def test_pdu_port_down(self, mock_port_down):
        slot_id = 12
        server.pdu_port_on(slot_id)
        assert mock_port_down.called_with(slot_id)

    @patch('server.pdu.pdu_port_down')
    @patch('server.check_and_set')
    def test_pdu_port_down_call_check(self, mock_check, mock_down):
        mock_down.return_value = True
        slot_id = 12
        server.pdu_port_off(slot_id)
        assert mock_check.called


if __name__ == '__main__':
    unittest.main()
