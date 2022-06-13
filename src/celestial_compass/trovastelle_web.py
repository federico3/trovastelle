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
import os, json
import asyncio
import zmq
import zmq.asyncio
from flask import Flask, request


REQUEST_TIMEOUT = 10000
REQUEST_RETRIES = 3
SERVER_ENDPOINT = "tcp://localhost:5556"
DATA_PATH = os.environ.get("CELESTIAL_COMPASS_DATA")

class trovastelle_web_stateless(object):
    def __init__(self, endpoint, timeout, retries):
        self.endpoint = endpoint
        self.timeout = timeout

    def get_configuration(self):
        command = 'GC'
        request = str(command).encode()
        logging.info("Sending (%s)", request)
        context = zmq.Context()
        client = context.socket(zmq.REQ)
        client.connect(self.endpoint)

        client.send(request)
        while True:
            if (client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
                reply = client.recv().decode()
                try:
                    config = json.loads(reply)
                    retries_left = REQUEST_RETRIES
                    logging.info("Server replied OK (%s)", reply)
                    return config
                except ValueError:                    
                    logging.error("Malformed reply from server: %s", reply)
                    return None

    def get_list(self):
        command = 'GL'
        request = str(command).encode()
        logging.info("Sending (%s)", request)
        context = zmq.Context()
        client = context.socket(zmq.REQ)
        client.connect(self.endpoint)

        client.send(request)
        while True:
            if (client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
                reply = client.recv().decode()
                try:
                    config = json.loads(reply)
                    retries_left = REQUEST_RETRIES
                    logging.info("Server replied OK (%s)", reply)
                    return config
                except ValueError:                    
                    logging.error("Malformed reply from server: %s", reply)
                    return None

    def set_configuration(self, config):
        command = "SL"+json.dumps(config)
        request = str(command).encode()
        logging.debug("Sending (%s)", request)
        context = zmq.Context()
        client = context.socket(zmq.REQ)
        client.connect(self.endpoint)

        client.send(request)
        while True:
            if (client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
                reply = client.recv().decode()
                if reply[:2] != "OK":
                    logging.warn("Warning: non-OK reply from Trovastelle")
                try:
                    logging.warn(reply[2:])
                    config = json.loads(reply[2:])
                    retries_left = REQUEST_RETRIES
                    logging.warn("Server replied (%s)", reply)
                    return config
                    
                except ValueError:                    
                    logging.error("Malformed reply from server: %s", reply)
                    continue

class trovastelle_web_stateful(object):
    def __init__(self, endpoint, timeout, retries):
        self.endpoint = endpoint
        self.timeout = timeout
        self.retries = retries
        self.context = zmq.Context()
        self.client = self.context.socket(zmq.REQ)
        self.client.connect(self.endpoint)

    def get_configuration(self):
        command = 'GC'
        request = str(command).encode()
        logging.info("Sending (%s)", request)
        self.client.send(request)
        retries_left = self.retries
        while True:
            if (self.client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
                reply = self.client.recv().decode()
                try:
                    config = json.loads(reply)
                    retries_left = REQUEST_RETRIES
                    logging.info("Server replied OK (%s)", reply)
                    return config
                except ValueError:                    
                    logging.error("Malformed reply from server: %s", reply)
                    continue

            retries_left -= 1
            logging.warning("No response from server")
            # Socket is confused. Close and remove it.
            self.client.setsockopt(zmq.LINGER, 0)
            self.client.close()
            if retries_left == 0:
                logging.error("Server seems to be offline, abandoning")
                return None
            #     sys.exit()

            logging.info("Reconnecting to server…")
            # Create new connection
            self.client = self.context.socket(zmq.REQ)
            self.client.connect(SERVER_ENDPOINT)
            logging.info("Resending (%s)", request)
            self.client.send(request)

    def get_list(self):
        command = 'GL'
        request = str(command).encode()
        logging.info("Sending (%s)", request)
        self.client.send(request)
        retries_left = self.retries
        while True:
            if (self.client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
                reply = self.client.recv().decode()
                try:
                    config = json.loads(reply)
                    retries_left = REQUEST_RETRIES
                    logging.info("Server replied OK (%s)", reply)
                    return config
                except ValueError:                    
                    logging.error("Malformed reply from server: %s", reply)
                    continue

            retries_left -= 1
            logging.warning("No response from server")
            # Socket is confused. Close and remove it.
            self.client.setsockopt(zmq.LINGER, 0)
            self.client.close()
            if retries_left == 0:
                logging.error("Server seems to be offline, abandoning")
                return None
            #     sys.exit()

            logging.info("Reconnecting to server…")
            # Create new connection
            self.client = self.context.socket(zmq.REQ)
            self.client.connect(SERVER_ENDPOINT)
            logging.info("Resending (%s)", request)
            self.client.send(request)

    def set_configuration(self, config):
        command = "SL"+json.dumps(config)
        request = str(command).encode()
        logging.debug("Sending (%s)", request)
        self.client.send(request)
        retries_left = self.retries
        while True:
            if (self.client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
                reply = self.client.recv().decode()
                if reply[:2] != "OK":
                    logging.warn("Warning: non-OK reply from Trovastelle")
                try:
                    logging.warn(reply[2:])
                    config = json.loads(reply[2:])
                    retries_left = REQUEST_RETRIES
                    logging.warn("Server replied (%s)", reply)
                    return config
                    
                except ValueError:                    
                    logging.error("Malformed reply from server: %s", reply)
                    continue

            retries_left -= 1
            logging.warning("No response from server")
            # Socket is confused. Close and remove it.
            self.client.setsockopt(zmq.LINGER, 0)
            self.client.close()
            if retries_left == 0:
                logging.error("Server seems to be offline, abandoning")
                return None
            #     sys.exit()

            logging.info("Reconnecting to server…")
            # Create new connection
            self.client = self.context.socket(zmq.REQ)
            self.client.connect(SERVER_ENDPOINT)
            logging.info("Resending (%s)", request)
            self.client.send(request)


if __name__ == "__main__":

    tw = trovastelle_web_stateless(
        endpoint=SERVER_ENDPOINT,
        timeout=REQUEST_TIMEOUT,
        retries=REQUEST_RETRIES,
    )

    app = Flask(__name__)

    @app.route("/config/", methods=['GET', 'POST'])
    def process_config_request():
        if request.method == 'GET':
            _config = tw.get_configuration()
            return app.response_class(
                response=json.dumps(_config),
                status=200,
                mimetype='application/json'
            )
        elif request.method == 'POST':
            new_config = request.get_json()
            _config = tw.set_configuration(new_config)
            if _config is None:
                return app.response_class(
                    response="",
                    status=503,
                    mimetype='application/json'
                )
            else:
                return app.response_class(
                    response=json.dumps(_config),
                    status=201,
                    mimetype='application/json'
                )

    @app.route("/list/", methods=['GET'])
    def process_list_request():
        _list = tw.get_list()
        return app.response_class(
            response=json.dumps(_list),
            status=200,
            mimetype='application/json'
        )

    app.run()
    # with open(os.path.join(DATA_PATH, 'config.json'), 'r') as config_file:
    #     config = json.load(config_file)
    # while True:
    #     configr = tw.set_configuration(config)
    #     print(configr)
    #     time.sleep(1)
