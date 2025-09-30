WebTester.py
CHASE MUNRO

modules used: sys, socket, ssl
Python version used: Developed using 3.9.0


HOW TO COMPILE AND RUN CODE:
MUST BE RUNNING at least python 3.6, implemented fstrings that won't work on older version


Input: call as specified in the assignment description
Format: python3 WebTester.py domain_name

EXAMPLES
python3 WebTester.py www.uvic.ca
python3 WebTester.py uvic.ca
python3 WebTester.py https://www.google.com
python3 WebTester.py http://www.google.com


OUTPUT:
    1. Returns whether or not the website supports http2 based on
        - the alpn protocol if https
        - options request if http
    2. Returns a list cookies that was sent in the response(s)
        - Splits into cookie name, domain name(if given) and expire time (if given)
    3. Returns whether or not the website is password protected
        - This is based on receiving a 401 status code in response to outgoing request   



OVERALL PROGRAM STRUCTURE:
main():
    1. Read URI from stdin
    2. parse URI (protocol, host, port, path)
        2.1 Set defaults for port protocol and path
        2.2 Check if protocol provided in URI
        2.3 Parse the host and path in URI
        2.4 Handle port if included
    3. HTTP/HTTPS Requests
        3.1. Check HTTP2 Support
            3.1.1 if HTTPS use alpn protocols
            3.1.2 if HTTP use options, upgrade request
            3.1.3 close HTTP2 check sockets
        3.2 Open new connection over HTTP 1.1
            3.1.1 if HTTPS context wrap socket
        3.3 Construct HTTP request
        3.4 Send Request through socket
        3.5 Receive HTTP response from server
        3.6 Decode response and close Connection
    4. Parse HTTP server response
        4.1 Split header and body
        4.2 Parse status line
        4.3 Extract protocol and status code
        4.4 Handle status codes
            4.4.1 If 30X code, extract location for redirect
            4.4.2 If 40X code, handle error 
        4.5 Extract cookies
    5. Redirect handling
        5.1 While status code 30X, and location included in response send web requests
    6. Parse cookies
    7. Output results






