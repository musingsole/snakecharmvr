import socket
from network import WLAN


not_configured_response = """HTTP/1.1 404 Not Found
Content-Type: text/html
Connection: close
Server: Jormunitor

Endpoint not found"""


success = """HTTP/1.1 200 OK
Content-Type: text/html
Connection: close
Access-Control-Allow-Origin: *
Server: Jormunitor

Successful Operation
"""


failure = """HTTP/1.1 502 OK
Content-Type: text/html
Connection: close
Access-Control-Allow-Origin: *
Server: Jormunitor

Operation Failed
"""


MAX_HTTP_MESSAGE_LENGTH = 2048


def unquote(s):
    """unquote('abc%20def') -> b'abc def'."""
    # Note: strings are encoded as UTF-8. This is only an issue if it contains
    # unescaped non-ASCII characters, which URIs should not.
    if not s:
        return b''

    if isinstance(s, str):
        s = s.encode('utf-8')

    bits = s.split(b'%')
    if len(bits) == 1:
        return s

    res = [bits[0]]
    append = res.append

    # Build cache for hex to char mapping on-the-fly only for codes
    # that are actually used
    hextobyte_cache = {}
    for item in bits[1:]:
        try:
            code = item[:2]
            char = hextobyte_cache.get(code)
            if char is None:
                char = hextobyte_cache[code] = bytes([int(code, 16)])
            append(char)
            append(item[2:])
        except KeyError:
            append(b'%')
            append(item)

    return b''.join(res)


def parse_querystring(qs):
    parameters = {}
    ampersandSplit = qs.split("&")
    for element in ampersandSplit:
        equalSplit = element.split("=")
        parameters[equalSplit[0]] = unquote(equalSplit[1].replace("+", " ")).decode()

    return parameters


# TODO: Implement as threading system
def http_daemon(ssid="Jormunitor",
                password="Jormunitor",
                host_ip="192.168.4.1",
                path_to_handler={},
                lock=None,
                log=lambda msg: print(msg)):
    log("Creating Access Point {} with password {}".format(ssid, password))
    log("User will need to connect to the webpage at {}".format(host_ip))

    wlan = WLAN()
    wlan.deinit()
    wlan.ifconfig(config=(host_ip, '255.255.255.0', '0.0.0.0', '8.8.8.8'))
    wlan.init(mode=WLAN.AP, ssid=ssid, auth=(WLAN.WPA2, password), channel=5, antenna=WLAN.INT_ANT)

    s = socket.socket()
    address = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s.bind(address)

    s.listen(5)
    log('listening on {}'.format(address))

    while lock is None or not lock.locked():
        connection_socket, address = s.accept()
        connection_socket.setblocking(False)
        log('New connection from {}'.format(address))

        try:
            msg = connection_socket.recv(MAX_HTTP_MESSAGE_LENGTH).decode()
            msg = msg.replace("\r\n", "\n")

            log("Received MSG:\n{}".format(msg))

            blank_line_split = msg.split('\n\n')
            if len(blank_line_split) != 2:
                raise Exception("Malformated HTTP request.")

            preamble = blank_line_split[0].split("\n")
            request = preamble[0]
            request_keys = ["method", "path", "version"]
            request_key_value = zip(request_keys, request.split(" "))
            request = {key: value for key, value in request_key_value}

            headers = preamble[1:]
            headers = {line.split(":")[0].strip(): line.split(":")[1].strip() for line in headers}

            for key, value in headers.items():
                request[key] = value

            log("Received Request:\n{}".format(request))

            request['body'] = blank_line_split[1]
            if 'Content-Length' in request:
                content_length = int(request['Content-Length'])

                if len(request['body']) < content_length:
                    log("Attempting to retrieve {} ({} remaining) bytes of content".format(content_length, content_length - len(request['body'])))
                    while len(request['body']) != content_length:
                        new_segment = connection_socket.recv(MAX_HTTP_MESSAGE_LENGTH).decode()
                        request['body'] += new_segment

            if request['path'] not in path_to_handler:
                log("{} not found in path_to_handler".format(request['path']))
                response = not_configured_response
            else:
                endpoint_handler = path_to_handler[request['path']]
                log("Path found. Passing to {}".format(endpoint_handler))
                response = endpoint_handler(**request)

            log("Sending response")

            connection_socket.send(response)
        except Exception as e:
            log("Request processing failure: {}".format(e))
            connection_socket.send(failure)
            connection_socket.close()

    log("HTTP Daemon dying")


def build_response(status_code=200, body=''):
    base = """Content-Type: text/html
Connection: close
Access-Control-Allow-Origin: *
Server: Jormunitor

"""

    status_line = "HTTP/1.1 {}\n".format(status_code)

    response = status_line + base + body

    return response
