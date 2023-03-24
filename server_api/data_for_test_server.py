pdu_info_ret_val = {
    "slot": 0,
    "sysInfo": {
        "device": [
            {
                "modelName": "E1211",
                "deviceName": "",
                "deviceUpTime": "00:00:18",
                "firmwareVersion": "V3.2 Build20111915",
                "ip": "2.2.8.8",
                "port count": 16,
                "connection": 1
            }
        ]
    }
}

pdu_status_response = {
    "slot": 0,
    "io": {
        "do": [
            {
                "doIndex": 0,
                "doMode": 0,
                "doStatus": 0
            },
            {
                "doIndex": 1,
                "doMode": 0,
                "doStatus": 0
            },
            {
                "doIndex": 2,
                "doMode": 0,
                "doStatus": 0
            },
            {
                "doIndex": 3,
                "doMode": 0,
                "doStatus": 0
            },
            {
                "doIndex": 4,
                "doMode": 0,
                "doStatus": 0
            }
        ]
    }
}

pdu_port_status = {"doIndex": 0, "doMode": 0, "doStatus": 0}

pdu_port_up = {"doIndex": 0, "doMode": 0, "doStatus": 1}

pdu_port_down = {"doIndex": 0, "doMode": 0, "doStatus": 0}
