import sys
from socket import *
import ssl

cookies = []

#Input: User-inputted URI
#Output: Parsed URI, split into port, host, and path
def uriparser(user_input):
    # Default
    port = 80
    protocol = "http"
    path = "/"
    
    # Check protocol
    if user_input.startswith("https://"):
        protocol = "https"
        port = 443
        site = user_input[len("https://"):]
    elif user_input.startswith("http://"):
        site = user_input[len("http://"):]
        protocol = "http"
        port = 80
    else:
        site = user_input
    
    # parsing host and path
    if "/" in site:
        host, path = site.split("/", 1)
        path = "/" + path
    else:
        host = site
        path = "/"
    if ":" in host:
        components= host.split(":")
        host = components[0]
        port = int(components[1])

    #DEBUGGING
    # print("Parser Output:")
    # print(f"Host: {host}")
    # print(f"Port: {port}")
    # print(f"Path: {path}")


    return protocol, host, port, path

def web_requests(protocol, host, port, path):
    supports_http2 = "no"   #Default  

    s = socket(AF_INET,SOCK_STREAM) 
    HOST = (host, port)
    
    #3. Setup connection
    try:
        s.connect(HOST) 
    except Exception as e:
        print(f"Error: exception{e}")
        exit(1)

    #4. 
    try:
        if protocol == "https":
            context = ssl.create_default_context()
            context.set_alpn_protocols(['http/1.1', 'h2'])
            s = context.wrap_socket(s, server_hostname=host)
            protocol_used = s.selected_alpn_protocol()
            if protocol_used == 'h2':
                supports_http2 = "yes"
        
        if not path:
            path = "/"

        #4. Send initial HTTP request
        request = f"GET {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += f"Connection: close\r\n"
        request += "\r\n"
        
        s.send(request.encode())

        data = s.recv(10000).decode("utf8")
        s.close()

    except Exception as e:
        print(f"error, exception: {e}")
        exit(1)

    return data, supports_http2

def data_parser(data):
    header = data.split("\r\n\r\n")[0]
    header_lines = header.split("\r\n")
    status_line = header_lines[0]
    password_protected = "no"
    location = None
    
    try:
        response_protocol = status_line.split()[0]
        status_code = int(status_line.split()[1])
    except Exception as e:
        print(f"sorry, there was a problem: {e}")
        exit(1)    
    
    #Get location if redirect code
    if 300 <= status_code <= 399:
        for line in header_lines[1:]:
            if line.lower().startswith("location:"):
                location = line.split(":", 1)[1].strip()
   
    elif status_code >= 400:
        if status_code == 401:
            password_protected = "yes"
        else:
            print('Sorry, something went wrong')
            exit(1)

    #Checking for cookies
    for line in header_lines[1:]:
        if line.lower().startswith("set-cookie:"):
            cookies.append(line)

    return response_protocol, status_code, location, password_protected

def cookie_parser(cookies): #TODO: Fix formatting issue
    pretty_cookies = []
    for cookie in cookies:
        # print(f"Heres the cookie: {cookie}")
        if "expires" in cookie: expires = True
        else: expires = False
        if "domain" in cookie: domain = True
        else: domain = False

        domain = ""
        expires = ""
        components = cookie.split(";")
        cookie_name =(components[0].split("=")[0].split()[1])
        
        for component in components:
            if "domain" in component:
                domain = component.split("=")[1]
            elif "expires" in component:
                expires = component.split("=")[1]
        
        pretty_cookie = f"cookie name: {cookie_name}"
        if domain != "":
            pretty_cookie += f", domain name: {domain}"
        if expires != "":
            pretty_cookie += f", expires time: {expires}"

        pretty_cookies.append(pretty_cookie)
    return pretty_cookies
        


def main():
    #1. Read URI from STDIN
    try:
        uri= sys.argv[1]
    except error:
        uri = input("Input URI: ")

    #2. Parse URI 
    protocol, host, port, path = uriparser(uri)

    #3. Establish Connection
    data, supportshttp2 = web_requests(protocol, host,port,path)
    

    #data_parser
    protocol, status_code, location, password_protected = data_parser(data)

    
    
    while 300 <= status_code <= 399 and location:
        max_redirects = 10
        redirects = 0
        while redirects < max_redirects and location:
            print(f"redirecting to {location}")
            protocol, host, port, path = uriparser(location)
            data, supportshttp2 = web_requests(protocol, host, port, path)
            protocol, status_code, location, password_protected = data_parser(data)
            redirects += 1

    pretty_cookies = cookie_parser(cookies)
    print(f"1. Supports http2: {supportshttp2}")
    print("2. List of Cookies:")
    [print(pretty_cookie) for pretty_cookie in pretty_cookies]
    print(f"3. Password-protected: {password_protected}")

main()