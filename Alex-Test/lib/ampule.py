import io
import re

BUFFER_SIZE = 256
TIMEOUT = 30
routes = []
variable_re = re.compile("^<([a-zA-Z]+)>$")

class Request:
    def __init__(self, method, full_path):
        self.method = method
        self.path = full_path.split("?")[0]
        self.params = Request.__parse_params(full_path)
        self.headers = {}
        self.body = None

    @staticmethod
    def __parse_params(path):
        query_string = path.split("?")[1] if "?" in path else ""
        param_list = query_string.split("&")
        params = {}
        for param in param_list:
            key_val = param.split("=")
            if len(key_val) == 2:
                params[key_val[0]] = key_val[1]
        return params


def __parse_headers(reader):
    headers = {}
    for line in reader:
        if line == b'\r\n': break
        title, content = str(line, "utf-8").split(":", 1)
        headers[title.strip().lower()] = content.strip()
    return headers

def __parse_body(reader):
    data = bytearray()
    for line in reader:
        if line == b'\r\n': break
        data.extend(line)
    return str(data, "utf-8")

def __read_request(client):
    message = bytearray()
    client.settimeout(30)
    socket_recv = True

    try:
        while socket_recv:
            buffer = bytearray(BUFFER_SIZE)
            client.recv_into(buffer)
            start_length = len(message)
            for byte in buffer:
                if byte == 0x00:
                    socket_recv = False
                    break
                else:
                    message.append(byte)
    except OSError as error:
        print("Error reading from socket", error)

    reader = io.BytesIO(message)
    line = str(reader.readline(), "utf-8")
    (method, full_path, version) = line.rstrip("\r\n").split(None, 2)

    request = Request(method, full_path)
    request.headers = __parse_headers(reader)
    request.body = __parse_body(reader)

    return request

def __send_response(client, code, headers, data):
    headers["Server"] = "Ampule/0.0.1-alpha (CircuitPython)"
    headers["Connection"] = "close"
    headers["Content-Length"] = len(data)

    response = "HTTP/1.1 %i OK\r\n" % code
    for k, v in headers.items():
        response += "%s: %s\r\n" % (k, v)
    response += "\r\n" + data + "\r\n"

    client.send(response)

def __on_request(method, rule, request_handler):
    regex = "^"
    rule_parts = rule.split("/")
    for part in rule_parts:
        # Is this portion of the path a variable?
        var = variable_re.match(part)
        if var:
            # If so, allow any alphanumeric value
            regex += r"([a-zA-Z0-9_-]+)\/"
        else:
            # Otherwise exact match
            regex += part + r"\/"
    regex += "?$"
    routes.append(
        (re.compile(regex), {"method": method, "func": request_handler})
    )

def __match_route(path, method):
    for matcher, route in routes:
        match = matcher.match(path)
        if match and method == route["method"]:
            return (match.groups(), route)
    return None

def listen(socket):
    try:
        client, remote_address = socket.accept()
        client.settimeout(1)

        request = __read_request(client)
        match = __match_route(request.path, request.method)
        if match:
            args, route = match
            status, headers, body = route["func"](request, *args)
            __send_response(client, status, headers, body)
        else:
            __send_response(client, 404, {}, "Not found")
    except OSError as e:
        print("Timed Out, continuing")
        return
    except BaseException as e:
        print("Error with request:", e)
        __send_response(client, 500, {}, "Error processing request")

    client.close()

def route(rule, method='GET'):
    return lambda func: __on_request(method, rule, func)
