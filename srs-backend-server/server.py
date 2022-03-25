#!/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging
import os
from netaddr import IPNetwork, IPAddress
from systemd.journal import JournalHandler

log = logging.getLogger('srs-backend-handler')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

class Error:
    success = 0
    failure = 1
    system_parse_json = 100
    system_parse_subnet = 200

try:
    bind_ip = os.environ['SRS_BACKEND_SERVER_BIND_IP']
except KeyError:
    bind_ip = "127.0.0.1"

try:
    bind_port = int(os.environ['SRS_BACKEND_SERVER_BIND_PORT'])
except KeyError:
    bind_port = 59354

try:
    tokens_json = os.environ['SRS_BACKEND_SERVER_ALLOWED_TOKENS']
    tokens = json.loads(tokens_json)
    tokens = [f'?token={token}' for token in tokens]
except KeyError:
    tokens = []
except Exception:
    log.error('Failed to parse JSON')
    os._exit(Error.system_parse_json)

try:
    allowed_subnet = os.environ['SRS_BACKEND_SERVER_ALLOWED_SUBNET_MASK']
    allowed_subnet = IPNetwork(allowed_subnet)
except KeyError:
    allowed_subnet = None
except Exception:
    log.error('Failed to parse subnet mask')
    os._exit(Error.system_parse_subnet)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        code = Error.success

        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        try:
            json_data = json.loads(post_body)
        except Exception:
            code = Error.system_parse_json
            log.error('Failed to parse JSON')
            log.error(post_body)

        """ json_data example:
        {
            'action': 'on_publish',
            'client_id': 798,
            'ip': '10.156.186.3',
            'vhost': '__defaultVhost__',
            'app': 'live',
            'tcUrl': 'rtmp://10.156.186.5/live?token=foo',
            'stream': 'test',
            'param': '?token=foo'
        }
        """

        if json_data['action'] == 'on_publish' and \
            (allowed_subnet != None and IPAddress(json_data['ip']) not in allowed_subnet) and \
            json_data['param'] not in tokens:
                log.info("Denying access")
                log.info(json_data)
                code = Error.failure

        response = bytes(json.dumps({"code": code, "data": None}), "UTF-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(response))
        self.end_headers()
        self.wfile.write(response)

try:
    server = HTTPServer((bind_ip, bind_port), SimpleHTTPRequestHandler)
except PermissionError:
    log.error("Permission denied to bind ip and/or port")
    os._exit(Error.failure)

try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
