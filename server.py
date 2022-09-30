#  coding: utf-8 
import socketserver

import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):

        # Dictionary to store header response messages
        self.headerDetails = {
            "statusCode": "",
            "contentLength" : 0,
            "contentType": "",
            "contentMessage": "",
            "location": ""
        }

        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        dataList = self.data.decode("utf-8").splitlines()
        rLine = dataList[0].split()
        rMethod = rLine[0]
        rPath = rLine[1]

        if "favicon" not in rPath: 
            # Only accept GET method in this assignment
            if rMethod == "GET":

                fullPath = self.getFullPath(rPath)
                pathResult = self.pathExist(fullPath)
                mimeType = self.getMimeType(rPath)

                if pathResult == "isDirectory":
                    # Does not end with "/", return status code "301 Moved Permanently"
                    # Otherwise return status code "200 OK"
                    if self.validDirectory(rPath):
                        self.handleHTML(fullPath + "index.html")
                        self.request.sendall(bytearray(self.headerResponse(200),'utf-8'))
                    else:
                        self.statusCode301(rPath + "/")
                        self.request.sendall(bytearray(self.headerResponse(301),'utf-8'))

                elif pathResult =="isFile":
                    # .css
                    if mimeType == "css":
                        self.handleCSS(fullPath)

                    # .html
                    elif mimeType == "html":
                        self.handleHTML(fullPath)
                    
                    else:
                        print("invalid mime-type")
                    
                    self.request.sendall(bytearray(self.headerResponse(200),'utf-8'))

                # Path not found, return return status code "404 Not Found"
                else:
                    # End with "/"
                    if self.validDirectory(rPath):
                        self.statusCode404()
                        self.request.sendall(bytearray(self.headerResponse(404),'utf-8'))
                    else:
                        self.statusCode301(rPath + "/")
                        self.request.sendall(bytearray(self.headerResponse(301),'utf-8'))
                    

            # status code "405 Method not allowed" for all non GET method
            else:
                self.statusCode405()
                self.request.sendall(bytearray(self.headerResponse(405),'utf-8'))

        # self.request.sendall(bytearray("OK",'utf-8'))
      

    # Handle status code 301 #
    # HTTP/1.1 301 Moved Permanently
    # Go to the URI mentioned in the Location header
    # URI in the location bar automatically changes
    def statusCode301(self, loc):
        self.headerDetails["statusCode"] = "301 Moved Permanently"
        self.headerDetails["location"]  = loc

    # Handle status code 404 #
    # HTTP/1.1 404 Not Found
    # Path does not exist
    def statusCode404(self):
        self.headerDetails["statusCode"] = "404 Not Found"

    # Handle status code 405 #
    # HTTP/1.1 405 Method not allowed
    # Only accepting GET for this assignment
    def statusCode405(self):
        self.headerDetails["statusCode"] = "405 Method not allowed"


    # status code 200
    def statusCode200(self, fullPath):
        content = self.getFileContent(fullPath)
        self.headerDetails["statusCode"] = "200 OK"
        self.headerDetails["contentLength"] = len(content)
        self.headerDetails["contentMessage"] = content


    # open css file and read the content
    def handleCSS(self, fullPath):
        self.statusCode200(fullPath)
        self.headerDetails["contentType"] = "text/css"


    # open html file and read the content
    def handleHTML(self, fullPath):
        self.statusCode200(fullPath)
        self.headerDetails["contentType"] = "text/html"


    # construct header response
    def headerResponse(self, code): 
        response = ""
        if code == 200:
            response = "HTTP/1.1 {0}\r\nContent-Length: {1}\r\nContent-Type: {2}\r\n\r\n{3}".format(self.headerDetails["statusCode"], self.headerDetails["contentLength"], self.headerDetails["contentType"], self.headerDetails["contentMessage"])
        
        elif code == 301:
            response = "HTTP/1.1 {0}\r\nLocation: {1}\r\n".format(self.headerDetails["statusCode"], self.headerDetails["location"])
        else:
            response = "HTTP/1.1 {0}\r\n\r\n{1}".format(self.headerDetails["statusCode"], self.headerDetails["statusCode"])
        return response


    # Check if path exist, is it directory or file
    def pathExist(self, fullPath):
        # Is it a directory (folder)? 
        if os.path.isdir(fullPath):
            return "isDirectory"
        elif os.path.isfile(fullPath):
            return "isFile"
        else:
            return "pathDoesNotExist"


    # Get the full path wth given path parameter
    def getFullPath(self, rPath):
        return os.getcwd() + "/www" + rPath

    # Check if for valid directory. Must end in "/"
    def validDirectory(self, rPath):
        lastCharIndex = len(rPath)-1
        if rPath[lastCharIndex] == "/":
            return True
        else:
            return False


    # Get mime-types, accepts http and css for this assignment
    def getMimeType(self, rPath):
        if ".css" in rPath:
            return "css"
        elif ".html" in rPath:
            return "html"
        else:
            return "invalid"


    # Read file content
    def getFileContent(self, fullPath):
        try:
            with open(fullPath) as file:
                content = file.read()
                return content
        except IOError:
            return "Can not read file."


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()