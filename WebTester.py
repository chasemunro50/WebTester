import sys
from socket import *

"""
Program Structure
1. Accept URI from STDIN, parse it
2. Connect to the server of the URI
3. Send an HTTP Request
4. Receive an HTTP Request
5. Routine to print response from server
6. Analyze the HTTP response 
7. Add functionality for multiple request
"""
#TODO: Build a Status Code Processor function
#TODO: Confirm Cookies output is Correct
#TODO: Build a HTTP2 Detector Function, See Tutorial 1 page 29-30
#TODO: Build proper structuring for host / requests

PORT = 80
supports_http2 = "no"
cookies = []
Password_protected = "no"
parsed_data = None
HTTP_version = None
HTTP_status = None


def web_parser(data):
    data_parsed = str(data).replace('\\n', '').split('\\r')
    
    version = data_parsed[0][2:] #Removing b"
    for item in data_parsed:
        if "Set-Cookie" in item:
            print("Found a cookie")
            cookies.append(item.replace(';', ','))
      

def web_requester(uri):
    HOST = (uri, PORT)
    s = socket(AF_INET,SOCK_STREAM) 

    #2. Connect to the server of the URI
    s.connect(HOST) 

    #3. Sending HTTP Request
    s.send(b"GET /index.html HTTP/1.0\n\n")

    #4. Receive an HTTP Request
    data = s.recv(10000)

    #5. Routine to #print response from server
    server_response()

    #6. Analyze HTTP response
    web_parser(data)
    
    s.close() #Closing connection

def server_response():
    print("Output:")
    print("website: " + uri) 
    print("1. Supports http2: " + supports_http2) 
    print("2. List of Cookies:")
    for cookie in cookies:
        print(cookie) # Will be key/value pairs
    print("3. Password-protected: " + Password_protected)

#1. Accept URI from STDIN
valid_input = False
while not valid_input:
    try:   
        uri = sys.argv[1]
    except IndexError:
        uri = input("Input URI: ")
    if uri is not None:
        valid_input = True


web_requester(uri)
server_response()


