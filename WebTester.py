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
#TODO: fix web_requester (connect, send) to handle redirects
#  URI FORMAT protocol://host[:port]/filepath
#TODO: Build redirect location for status_code_processor
#TODO: Build a HTTP2 Detector Function, See Tutorial 1 page 29-30
        #1. try options request
        #2. Try TLS-ALPN (TSL Handshake)


PORT = 80
supports_http2 = "no"
cookies = []
Password_protected = "no"
parsed_data = None
HTTP_version = None
HTTP_status = None


def web_parser(data):

    parsed_data = str(data).replace('\\n', '').split('\\r') 
    version = parsed_data[0][2:] #Removing b"
    #print(parsed_data) #DEBUGGING
    HTTP_version = version.split()[0]
    status_code = int(version.split()[1])

    return parsed_data, status_code



# Takes the URI input, returns data from the server
def web_requester(uri):

    HOST = (uri, PORT)
    s = socket(AF_INET,SOCK_STREAM) 

    s.connect(HOST) #2. Connect to the server of the URI

    s.send(b"GET /index.html HTTP/1.0\n\n") #3. Sending HTTP Request 
    
    data = s.recv(10000) #4. Receive an HTTP Request

    s.close() 

    return data

# Final output
def final_ouput(uri):

    print("Output:")
    print("website: " + uri) 
    print("1. Supports http2: " + supports_http2) 
    print("2. List of Cookies:")
    for cookie in cookies:
        print(cookie) 
    print("3. Password-protected: " + Password_protected)


def status_code_processor(code_received, parsed_data):

    if code_received == 200:
        print("status code 200, everything went okay with request") 
        successful_request(parsed_data) #6. Analyze http response

    elif code_received == 401:
        Password_protected = "yes"
        print("status code 401, website is password protected")
    elif code_received == 301:
        print("status code 301, moved permanently")

    elif code_received == 302:
        print("status code 302, moved temporarily")
        #Looking for redirection
        for data in parsed_data:
            if "Location" in data:
                redirect_location = data.split()[1] 
                print(redirect_location)
        



    elif code_received == 404:
        print("status code 404, not found")
    elif code_received == 505:
        print("status code 505, HTTP version not supported")


#Function handles data for status code 200, successful request
def successful_request(parsed_data):

    for item in parsed_data:

        #Parsing cookies
        if "Set-Cookie" in item: 
            expire_time = False
            domain = False

            if "expires" in item:
                expire_time = True
            if "domain" in item:
                domain = True
            components = item.split(';')
            #print(components) #DEBUGGING
            cookie_name =(components[0].split("=")[0]) 


            if expire_time and domain:
                for component in components: 
                    if "expires" in component:
                        cookie_expire_time = component
                    elif "domain" in component:
                        cookie_domain = component

                cookies.append(cookie_name + "," + cookie_expire_time + "," + cookie_domain)    
           
            elif expire_time:
                for component in components:
                    if "expires" in component:
                        cookies.append(cookie_name + "," + component)
            elif domain:
                for component in components:
                    if "domain" in component:
                        cookies.append(cookie_name + "," + component)
            else:
                cookies.append(cookie_name)


#Breaks data into header and body for debugging
def deconstructor(data): 
    deconstructed_data = data.split(b"\r\n\r\n")
    print("Header:")
    print(deconstructed_data[0])
    try:
        print("body:")
        print(deconstructed_data[1])
    except error:
        print("error, no packet body")



def main():
    #1. Accept URI from STDIN
    valid_input = False
    while not valid_input:
        try:   
            uri = sys.argv[1]
        except IndexError:
            uri = input("Input URI: ")
        if uri is not None:
            valid_input = True

    data = web_requester(uri) #Returns data from HTTP Request

    parsed_data, status_code = web_parser(data) #Splits data, gets HTTP version, status code

    status_code_processor(status_code,parsed_data) #processes status code

    final_ouput(uri) #Final output


main()