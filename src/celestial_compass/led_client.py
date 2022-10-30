"""
 Copyright (C) 2021 Federico Rossi (347N)
 
 This file is part of Trovastelle.
 
 Trovastelle is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 
 Trovastelle is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 
 You should have received a copy of the GNU General Public License
 along with Trovastelle.  If not, see <http://www.gnu.org/licenses/>.
"""
import logging
import json
from threading import TIMEOUT_MAX
import zmq

REQUEST_TIMEOUT = 2500
REQUEST_RETRIES = 3
SERVER_ENDPOINT = "tcp://localhost:5555"

class led_client(object):
    def __init__(self, endpoint, timeout, retries):
        self.endpoint = endpoint
        self.timeout = timeout
        self.retries = retries
        self.context = zmq.Context()
        self.client = self.context.socket(zmq.REQ)
        self.client.connect(self.endpoint)

    def breathe_color_async(self, RGB_color: list=[1.,1.,1.], frequency_hz: float=.25, duration_s: float=10):
        command = json.dumps(RGB_color)
        request = str(command).encode()
        logging.info("Sending (%s)", request)
        self.client.send(request)
        retries_left = self.retries
        while True:
            if (self.client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
                reply = self.client.recv().decode()
                if reply == str("OK") + command:
                    logging.info("Server replied OK (%s)", reply)
                    retries_left = REQUEST_RETRIES
                    break
                    
                else:
                    logging.error("Malformed reply from server: %s", reply)
                    continue

            retries_left -= 1
            logging.warning("No response from server")
            # Socket is confused. Close and remove it.
            self.client.setsockopt(zmq.LINGER, 0)
            self.client.close()
            if retries_left == 0:
                logging.error("Server seems to be offline, abandoning")
                break
            #     sys.exit()

            logging.info("Reconnecting to server…")
            # Create new connection
            self.client = self.context.socket(zmq.REQ)
            self.client.connect(SERVER_ENDPOINT)
            logging.info("Resending (%s)", request)
            self.client.send(request)

if __name__ == "__main__":
    import random, time

    # logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    client = led_client(
        endpoint=SERVER_ENDPOINT,
        timeout=REQUEST_TIMEOUT,
        retries=REQUEST_RETRIES,
    )
    while True:
        client.breathe_color_async(
            RGB_color =[
                random.random(),
                random.random(),
                random.random(),
                ]
            )
        time.sleep(1)