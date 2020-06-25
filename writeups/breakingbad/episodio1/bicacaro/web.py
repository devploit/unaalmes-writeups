#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import struct
from operator import *
from http.server import HTTPServer, BaseHTTPRequestHandler


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		print (self.headers)
		self.protocol_version='HTTP/1.1'
		self.send_response(200, 'OK')
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		self.wfile.write(bytes("<html> <head><title> OK</title> </head> <body>"))

httpd = HTTPServer(('', 64010), SimpleHTTPRequestHandler)
httpd.serve_forever()
