#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        return url.hostname, url.port
    
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # Use split by spaces to isolate code
        return data.split()[1]

    def get_headers(self,data):
        # Collect headers using dictionary
        headers = {}
        lines = data.splitlines()
        # Run through each line and check for headers in key/value format seperated by : and save it in dict
        for line in lines:
            if line.contains(":"):
                index = line.indexOf(":")
                headers[line[:index]] = line[index:]
        return headers

    def get_body(self, data):
        # Use split to find body using sequence that leads to body
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # Parse url and get host and port and create connection
        parsed = urllib.parse.urlparse(url)
        host, port = self.get_host_port(parsed)
        print(host,port,parsed.path)
        self.connect(host, port)
        # Send request
        self.sendall(f"GET {parsed.path} HTTP/1.1\nHost: {host}")
        # Get server response and read it
        response = self.recvall(self.socket)
        self.close()
        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # Parse url and get host and port and create connection
        parsed = urllib.parse.urlparse(url)
        host, port = self.get_host_port(parsed)
        self.connect(host, port)
        # Create post request
        post = f"POST {parsed.path} HTTP/1.1\nHost: {host}\nContent-Type: application/x-www-form-urlencoded\n\n"
        if args:
            # Convert dictionary to string to post 
            post += urllib.parse.urlencode(args)
        self.sendall(post)
        response = self.recvall(self.socket)
        self.close()
        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
