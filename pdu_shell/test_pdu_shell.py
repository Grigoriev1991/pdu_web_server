# Command for run Coverage and generate html report:
# $ coverage run pdu_shell/test_pdu_shell.py
# $ coverage html --omit="*test*" -d coverage

import os
import sys
import copy
from http import HTTPStatus

import unittest
from unittest.mock import Mock, patch


root_path = os.path.dirname(__file__)
if root_path not in sys.path:
    sys.path.append(root_path)


from iologik_shell import PDU
import data_for_test


class TestPDU(unittest.TestCase):
    def setUp(self) -> None:
        '''create a pdu test object'''
        self.test_PDU = PDU(adress='http://0.0.0.0')
        self.test_PDU.port_count = 16

    @patch('iologik_shell.requests')
    def test_pdu_connection_status(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_request.get.return_value = mock_response
        response = self.test_PDU.pdu_connection_status()
        self.assertEqual(response, HTTPStatus.OK)

    @patch('iologik_shell.requests')
    def test_get_pdu_info(self, mock_requests):
        '''Have the correct response in the form of a dict and correct IP'''
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = data_for_test.pdu_base_info
        mock_requests.get.return_value = mock_response
        response = self.test_PDU.pdu_info()
        self.assertIsInstance(response, dict)
        self.assertEqual(
                         response['sysInfo']['device'][0]['ip'],
                         self.test_PDU.adress.split('//')[1]
                        )

    @patch('iologik_shell.requests')
    def test_get_pdu_info_without_HTTPStatus_OK(self, mock_requests):
        '''Have the correct response from pdu_info if HTTPStatus not OK'''
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.NO_CONTENT
        mock_response.json.return_value = data_for_test.pdu_base_info
        mock_requests.get.return_value = mock_response
        response = self.test_PDU.pdu_info()
        self.assertEqual(response, None)

    @patch('iologik_shell.requests')
    def test_get_pdu_status(self, mock_requests):
        '''Have the correct response in the form of a dict'''
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = data_for_test.pdu_all_port_off
        mock_requests.get.return_value = mock_response
        response = self.test_PDU.pdu_status()
        self.assertIsInstance(response, dict)

    @patch('iologik_shell.requests')
    def test_get_pdu_status_without_HTTPstatus_OK(self, mock_requests):
        '''Have the correct response from pdu_status if HTTPStatus not OK'''
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.NOT_FOUND
        mock_requests.get.return_value = mock_response
        response = self.test_PDU.pdu_status()
        self.assertEqual(response, None)

    @patch('iologik_shell.PDU.pdu_status')
    def test_get_pdu_port_status(self, mock_pdu_status):
        '''Have the correct response in the form of a dict'''
        slot_id = 3
        mock_pdu_status.return_value = data_for_test.pdu_all_port_off
        response = self.test_PDU.pdu_port_status(slot_id=slot_id)
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIn(slot_id, range(0, self.test_PDU.port_count))

    @patch('iologik_shell.PDU.pdu_status')
    @patch('iologik_shell.requests')
    def test_pdu_port_up(self, mock_requests, mock_pdu_status):
        '''Have the correct response from pdu_port_up'''
        slot_id = 4
        mock_pdu_status.return_value = copy.deepcopy(
            data_for_test.pdu_all_port_off
        )
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = data_for_test.pdu_port_4_on
        mock_requests.put.return_value = mock_response
        response = self.test_PDU.pdu_port_up(slot_id=slot_id)
        self.assertNotEqual(response.json(), data_for_test.pdu_all_port_off)
        self.assertEqual(response.json(), data_for_test.pdu_port_4_on)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(slot_id, range(0, self.test_PDU.port_count))

    @patch('iologik_shell.PDU.pdu_status')
    @patch('iologik_shell.requests')
    def test_pdu_port_up_without_HTTPstatus_OK(
                                                self,
                                                mock_requests,
                                                mock_pdu_status
                                                ):
        '''Have the correct response from pdu_port_up if HTTPStatus not OK'''
        mock_pdu_status.return_value = copy.deepcopy(
            data_for_test.pdu_all_port_off
        )
        slot_id = 3
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.NOT_FOUND
        mock_requests.put.return_value = mock_response
        response = self.test_PDU.pdu_port_up(slot_id=slot_id)
        self.assertEqual(response, None)

    @patch('iologik_shell.PDU.pdu_status')
    @patch('iologik_shell.requests')
    def test_pdu_port_down(self, mock_requests, mock_pdu_status):
        '''Have the correct response from pdu_port_down'''
        slot_id = 4
        mock_pdu_status.return_value = data_for_test.pdu_all_port_on
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = data_for_test.pdu_port_4_off
        mock_requests.put.return_value = mock_response
        response = self.test_PDU.pdu_port_down(slot_id=slot_id)
        self.assertNotEqual(response.json(), data_for_test.pdu_all_port_off)
        self.assertEqual(response.json(), data_for_test.pdu_port_4_off)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(slot_id, range(0, self.test_PDU.port_count))

    @patch('iologik_shell.PDU.pdu_status')
    @patch('iologik_shell.requests')
    def test_pdu_port_down_without_HTTPstatus_OK(
                                                 self,
                                                 mock_requests,
                                                 mock_pdu_status
                                                 ):
        '''Have the correct response from pdu_port_down if HTTPStatus not OK'''
        slot_id = 4
        mock_pdu_status.return_value = data_for_test.pdu_all_port_on
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.NOT_FOUND
        mock_requests.put.return_value = mock_response
        response = self.test_PDU.pdu_port_down(slot_id=slot_id)
        self.assertEqual(response, None)

    @patch('iologik_shell.PDU.pdu_port_status')
    @patch('iologik_shell.PDU.pdu_port_up')
    @patch('iologik_shell.PDU.pdu_port_down')
    def test_pdu_port_reset_when_port_OFF(
                                     self, mock_pdu_port_down,
                                     mock_pdu_port_up,
                                     mock_pdu_port_status
                                    ):
        '''check that the correct functions
        are called when port OFF and requesting to RESET the port

        '''
        slot_id = 2
        mock_pdu_port_status.return_value = data_for_test.pdu_port_status_2_off
        mock_pdu_port_up.return_value = data_for_test.pdu_port_2_on
        mock_pdu_port_down.return_value = None
        self.test_PDU.pdu_port_reset(slot_id=slot_id)
        assert mock_pdu_port_status.called_with(slot_id)
        assert mock_pdu_port_up.called_with(slot_id)
        assert not mock_pdu_port_down.called

    @patch('iologik_shell.PDU.pdu_port_status')
    @patch('iologik_shell.PDU.pdu_port_up')
    @patch('iologik_shell.PDU.pdu_port_down')
    def test_pdu_port_reset_when_port_ON(
                                     self, mock_pdu_port_down,
                                     mock_pdu_port_up,
                                     mock_pdu_port_status
                                    ):
        '''check that the correct functions
        are called when port ON and requesting to RESET the port

        '''
        slot_id = 2
        mock_pdu_port_status.return_value = data_for_test.pdu_port_status_2_on
        mock_pdu_port_down.return_value = HTTPStatus.OK
        mock_pdu_port_up.return_value = HTTPStatus.OK
        self.test_PDU.pdu_port_reset(slot_id=slot_id)
        assert mock_pdu_port_status.called_with(slot_id)
        assert mock_pdu_port_down.called_with(slot_id)
        assert mock_pdu_port_up.called_with(slot_id)

    @patch('iologik_shell.PDU.pdu_port_status')
    @patch('iologik_shell.PDU.pdu_port_up')
    def test_pdu_port_toggle_when_port_OFF(
                                            self, mock_pdu_port_up,
                                            mock_pdu_port_status
                                        ):
        '''check that the correct functions
        are called when port OFF requesting to TOGGLE the port

        '''
        slot_id = 2
        mock_pdu_port_status.return_value = data_for_test.pdu_port_status_2_off
        self.test_PDU.pdu_port_toggle(slot_id=slot_id)
        mock_pdu_port_up.return_value = HTTPStatus.OK
        assert mock_pdu_port_status.called_with(slot_id)
        assert mock_pdu_port_up.called_with(slot_id)

    @patch('iologik_shell.PDU.pdu_port_status')
    @patch('iologik_shell.PDU.pdu_port_down')
    def test_pdu_port_toggle_when_port_ON(
                                            self, mock_pdu_port_down,
                                            mock_pdu_port_status
                                        ):
        '''check that the correct functions
        are called when port ON requesting to TOGGLE the port

        '''
        slot_id = 2
        mock_pdu_port_status.return_value = data_for_test.pdu_port_status_2_on
        self.test_PDU.pdu_port_toggle(slot_id=slot_id)
        mock_pdu_port_down.return_value = HTTPStatus.OK
        assert mock_pdu_port_status.called_with(slot_id)
        assert mock_pdu_port_down.called_with(slot_id)

    # @patch('iologik_shell.requests')
    # @patch('iologik_shell.PDU.pdu_status')
    # def test_pdu_all_port_OFF(self, mock_pdu_status, mock_request):
    #     mock_pdu_status.return_value = copy.deepcopy(
    #         data_for_test.pdu_all_port_on
    #     )
    #     mock_responce = Mock()
    #     mock_responce.status_code = HTTPStatus.OK
    #     mock_responce.json.return_value = data_for_test.pdu_all_port_off
    #     mock_request.put.return_value = mock_responce
    #     response = self.test_PDU._pdu_all_port_OFF()
    #     self.assertEqual(response.status_code, HTTPStatus.OK)
    #     self.assertEqual(
    #         mock_pdu_status.return_value, data_for_test.pdu_all_port_off
    #     )


if __name__ == '__main__':
    unittest.main()
