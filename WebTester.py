import sys
from socket import *
import ssl

cookies = []

#Input: User-inputted URI
#Output: Parsed URI, split into port, host, and path
def uriparser(user_input):
    #2.1 Set defaults 
    port = 80
    protocol = "http"
    path = "/"
    
    #2.2 Check protocol
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
    
    #2.3 Parse host and path
    if "/" in site:
        host, path = site.split("/", 1)
        path = "/" + path
    else:
        host = site
        path = "/"

    #2.4 Handle custom ports
    if ":" in host:
        components= host.split(":")
        host = components[0]
        port = int(components[1])
        
    return protocol, host, port, path

#Input: protocol, host, port
#Output: yes/no for HTTP/2 support
def check_http2_support(protocol, host, port):
    """Check if the server supports HTTP/2"""
    supports_http2 = "no"
    
    #3.1 Check HTTP/2 support
    try:
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((host, port))
        
        #3.1.1 if HTTPS use alpn protocols
        if protocol == "https":
            context = ssl.create_default_context()
            context.set_alpn_protocols(['http/1.1', 'h2'])
            ssl_socket = context.wrap_socket(s, server_hostname=host)
            
            if ssl_socket.selected_alpn_protocol() == 'h2':
                supports_http2 = "yes"
            
            ssl_socket.close()
        
        #3.1.2 if HTTP use options, upgrade request
        else:
            request = f"OPTIONS * HTTP/1.1\r\n"
            request += f"Host: {host}\r\n"
            request += f"Connection: Upgrade, HTTP2-Settings\r\n"
            request += f"Upgrade: h2c\r\n"
            request += f"HTTP2-Settings: \r\n"
            request += f"\r\n"
            
            s.send(request.encode())
            upgrade_response = s.recv(10000).decode()
            
            if "200" in upgrade_response and "h2c" in upgrade_response.lower():
                supports_http2 = "yes"  
            
            s.close()
    
    # If HTTP/2 check fails, just continue with HTTP/1.1
    except Exception as e:
        pass
        
    return supports_http2

#Input: protocol, host, port
#Output: socket connection
def create_connection(protocol, host, port):
    """Create and return a socket connection"""
    try:
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((host, port))
        
        if protocol == "https":
            context = ssl.create_default_context()
            context.set_alpn_protocols(['http/1.1'])  # Force HTTP/1.1 for compatibility
            s = context.wrap_socket(s, server_hostname=host)
            
        return s
        
    except Exception as e:
        print(f"Error: exception{e}")
        exit(1)

#Input: protocol, host, port, path
#Output: server response data, yes/no for HTTP/2 support
def web_requests(protocol, host, port, path):
    # 3.1 Check HTTP/2 support
    supports_http2 = check_http2_support(protocol, host, port)
    # 3.2 Create connection for actual request
    s = create_connection(protocol, host, port)
    
    try:
        # Setup path
        if not path:
            path = "/"

        #3.3 Construct HTTP request
        request = f"GET {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += f"Connection: close\r\n"
        request += "\r\n"
        
        #3.4 Send request through socket
        s.send(request.encode())

        # 3.5 Receive response from server
        response_data = b""
        while b"\r\n\r\n" not in response_data:
            chunk = s.recv(4096)
            if not chunk:
                break
            response_data += chunk
        
        # 3.6 Decode response and close connection
        data = response_data.decode()
        s.close()

    except Exception as e:
        print(f"error, exception: {e}")
        exit(1)

    return data, supports_http2

#Input: raw HTTP response data
#Output: protocol, status code, location (if redirect), password protected (yes/no)
def data_parser(data):

    #4.1 Split header and body
    try:
        header = data.split("\r\n\r\n")[0]  #Splitting header from body
        header_lines = header.split("\r\n") #Splitting on carariage return and line-feed
    except error as e:
        print(f"Sorry, an error occured{e}")
        exit(1)
    
    if not header_lines:
        print("Error: No header lines found in response")
        exit(1)
    
    #4.2 Parse status line
    status_line = header_lines[0]
    password_protected = "no"
    location = None
    
    #4.3 Extract protocol and status code
    try:
        parts = status_line.split()
        response_protocol = parts[0]
        status_code = int(parts[1])

    except Exception as e:
        print(f"sorry, there was a problem parsing status line '{status_line}': {e}")
        exit(1)    
    
    #4.4 handle status codes
    #4.4.1 Get location for redirect
    if 300 <= status_code <= 399:
        for line in header_lines[1:]:
            if line.lower().startswith("location:"):
                location = line.split(":", 1)[1].strip()
    
    #4.4.2 if 40X code, handle error
    elif status_code >= 400:
        if status_code == 401:
            password_protected = "yes"
        else:
            print('Sorry, something went wrong')
            exit(1)

    #4.5 extract cookies
    for line in header_lines[1:]:
        if line.lower().startswith("set-cookie:"):
            cookies.append(line)

    return response_protocol, status_code, location, password_protected


#Input: list of raw cookie strings
#Output: list of formatted cookie strings
def cookie_parser(cookies):
    pretty_cookies = []
    for cookie in cookies:
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

    #3. HTTP/HTTPS requests
    data, supportshttp2 = web_requests(protocol, host,port,path)
    
    #4. Parse HTTP server response
    protocol, status_code, location, password_protected = data_parser(data)
    
    #5. Redirect handling
    max_redirects = 10
    redirects = 0
    while 300 <= status_code <= 399 and location and redirects < max_redirects and location:
        protocol, host, port, path = uriparser(location)
        data, supportshttp2 = web_requests(protocol, host, port, path)
        protocol, status_code, location, password_protected = data_parser(data)
        redirects += 1

    #6. Parse Cookies
    pretty_cookies = cookie_parser(cookies)

    #7. Output results
    print(f"1. Supports http2: {supportshttp2}")
    print("2. List of Cookies:")
    [print(pretty_cookie) for pretty_cookie in pretty_cookies]
    print(f"3. Password-protected: {password_protected}")

main()