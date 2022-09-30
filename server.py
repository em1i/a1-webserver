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
            "statusCode": "test code",
            "contentLength" : 0,
            "contentType": "test message",
            "contentMessage": "test message",
            "location": "test location"
        }

        self.data = self.request.recv(1024).strip()
        print("`````````` START `````````")
        print ("Got a request of: %s\n" % self.data)

        dataList = self.data.decode("utf-8").splitlines()
        print("@@@ dataList: ", dataList)
        rLine = dataList[0].split()
        print("@@@ rLine is: ", rLine)
        rMethod = rLine[0]
        rPath = rLine[1]

        # Only accept GET method in this assignment
        if rMethod == "GET":

            fullPath = self.getFullPath(rPath)
            pathResult = self.pathExist(fullPath)
            mimeType = self.getMimeType(rPath)

            print("******* mime-type: " + mimeType)

            if pathResult == "isDirectory":

                # Does not end with "/", return status code "301 Moved Permanently"
                # Otherwise return status code "200 OK"
                if self.validDirectory(rPath):
                    self.handleHTML(fullPath + "index.html")
                else:
                    self.statusCode301(rPath + "/")

            elif pathResult =="isFile":
                # .css??
                if mimeType == "css":
                    self.handleCSS(fullPath)

                # .html?
                elif mimeType == "html":
                    self.handleHTML(fullPath)
                
                else:
                    print("invalid mime-type")

            # Path not found, return return status code "404 Not Found"
            else:
                self.statusCode404()

        # status code "405 Method not allowed" for all non GET method
        else:
            self.statusCode405()

        # self.request.sendall(bytearray("OK",'utf-8'))

        
        print(self.headerResponse())
        self.request.sendall(bytearray(self.headerResponse(),'utf-8'))
        print("`````````` END `````````")
        

    def statusCode200(self):
        self.headerDetails["statusCode"] = "200 OK"
        self.headerDetails["contentType"] = "text/html"

    # Handle status code 301 #
    # HTTP/1.1 301 Moved Permanently
    # Go to the URI mentioned in the Location header, and don't ask me again!
    # URI in the location bar automatically changes
    def statusCode301(self, location):
        self.headerDetails["statusCode"] = "301 Moved Permanently"
        self.location = location 
        # self.headerDetails["contentLength"] = len(self.headerDetails["contentMessage"])

    # Handle status code 404 #
    # HTTP/1.1 404 Not Found
    # You've got the wrong resource or path. Can't find what you're looking for. Droids? What droids? 
    def statusCode404(self):
        self.headerDetails["statusCode"] = "404 Not Found"
        # self.headerDetails["contentLength"] = len(self.headerDetails["contentMessage"])

    # Handle status code 405 #
    # HTTP/1.1 405 Method not allowed
    # Whatever method you used (GET/HEAD/POST/PUT/DELETE/...) doesn't work on this URI
    def statusCode405(self):
        self.headerDetails["statusCode"] = "405 Method not allowed"
        # self.headerDetails["contentLength"] = len(self.headerDetails["contentMessage"])

    # construct header response

    def headerResponse(self): 
        response = """HTTP/1.1 {0}\n\rContent-Length: {1}\n\rContent-Type: {2}\n\r\n\r{3}""".format(self.headerDetails["statusCode"], self.headerDetails["contentLength"], self.headerDetails["contentType"], self.headerDetails["contentMessage"])
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

    # open css file and read the content
    def handleCSS(self, fullPath):
        print("******* in handleCSS")
        content = self.getFileContent(fullPath)
        self.headerDetails["statusCode"] = "200 OK"
        self.headerDetails["contentType"] = "text/css"
        self.headerDetails["contentLength"] = len(content)
        self.headerDetails["contentMessage"] = content


    # open html file and read the content
    def handleHTML(self, fullPath):
        print("******* in handleHTML")
        content = self.getFileContent(fullPath)
        self.headerDetails["statusCode"] = "200 OK"
        self.headerDetails["contentType"] = "text/html"
        self.headerDetails["contentLength"] = len(content)
        self.headerDetails["contentMessage"] = content
        return

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