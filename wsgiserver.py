# SPDX-FileCopyrightText: Copyright (c) 2019 Matt Costi for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_esp32spi_wsgiserver`
================================================================================

A simple WSGI (Web Server Gateway Interface) server that interfaces with the ESP32 over SPI.
Opens a specified port on the ESP32 to listen for incoming HTTP Requests and
Accepts an Application object that must be callable, which gets called
whenever a new HTTP Request has been received.

The Application MUST accept 2 ordered parameters:
    1. environ object (incoming request data)
    2. start_response function. Must be called before the Application
        callable returns, in order to set the response status and headers.

The Application MUST return a single string in a list,
which is the response data

Requires update_poll being called in the applications main event loop.

For more details about Python WSGI see:
https://www.python.org/dev/peps/pep-0333/

* Author(s): Matt Costi
"""
# pylint: disable=no-name-in-module

import io
import gc
from micropython import const
import socketpool
import wifi

class BadRequestError(Exception):
    """Raised when the client sends an unexpected empty line"""
    pass

_BUFFER_SIZE = 32
buffer = bytearray(_BUFFER_SIZE)
def readline(socketin):
    """
    Implement readline() for native wifi using recv_into
    """
    data_string = b""
    while True:
        try:
            num = socketin.recv_into(buffer, 1)
            data_string += str(buffer, 'utf8')[:num]
            if num == 0:
                return data_string
            if data_string[-2:] == b"\r\n":
                return data_string[:-2]
        except OSError as ex:
            # if ex.errno == 9: # [Errno 9] EBADF
            #     return None
            if ex.errno == 11:  # [Errno 11] EAGAIN
                continue
            raise


def read(socketin,length = -1):
    total = 0
    data_string = b""
    try:
        if length > 0:
            while total < length:
                reste = length - total
                num = socketin.recv_into(buffer, min(_BUFFER_SIZE, reste))
                #
                if num == 0:
                    # timeout
                    # raise OSError(110)
                    return data_string
                #
                data_string += buffer[:num]
                total = total + num
            return data_string
        else:
            while True:
                num = socketin.recv_into(buffer, 1)
                data_string += str(buffer, 'utf8')[:num]
                if num == 0:
                    return data_string
    except OSError as ex:
        if ex.errno == 11: # [Errno 11] EAGAIN
            return data_string
        raise

def parse_headers(sock):
    """
    Parses the header portion of an HTTP request/response from the socket.
    Expects first line of HTTP request/response to have been read already
    return: header dictionary
    rtype: Dict
    """
    headers = {}
    while True:
        line = readline(sock)
        if not line or line == b"\r\n":
            break

        #print("**line: ", line)
        title, content = line.split(b': ', 1)
        if title and content:
            title = str(title.lower(), 'utf-8')
            content = str(content, 'utf-8')
            headers[title] = content
    return headers


pool = socketpool.SocketPool(wifi.radio)

NO_SOCK_AVAIL = const(255)

# pylint: disable=invalid-name
class WSGIServer:
    """
    A simple server that implements the WSGI interface
    """

    def __init__(self, port=80, debug=False, application=None):
        self.application = application
        self.port = port
        self._server_sock = None
        self._client_sock = None
        self._debug = debug

        self._response_status = None
        self._response_headers = []

    def start(self):
        """
        starts the server and begins listening for incoming connections.
        Call update_poll in the main loop for the application callable to be
        invoked on receiving an incoming request.
        """
        self._server_sock = pool.socket(pool.AF_INET,pool.SOCK_STREAM)
        HOST = repr(wifi.radio.ipv4_address_ap)
        self._server_sock.bind((repr(wifi.radio.ipv4_address_ap), self.port))
        self._server_sock.listen(1)
#         if self._debug:
#             ip = _the_interface.pretty_ip(_the_interface.ip_address)
#             print("Server available at {0}:{1}".format(ip, self.port))
#             print(
#                 "Sever status: ",
#                 _the_interface.get_server_state(self._server_sock.socknum),
#             )

    def pretty_ip(self):
        return f"http://{wifi.radio.ipv4_address_ap}:{self.port}"

    def update_poll(self):
        """
        Call this method inside your main event loop to get the server
        check for new incoming client requests. When a request comes in,
        the application callable will be invoked.
        """
        self.client_available()
        if self._client_sock:
            try:
                environ = self._get_environ(self._client_sock)
                result = self.application(environ, self._start_response)
                self.finish_response(result)
            except BadRequestError:
                self._start_response("400 Bad Request", [])
                self.finish_response([])

    def finish_response(self, result):
        """
        Called after the application callbile returns result data to respond with.
        Creates the HTTP Response payload from the response_headers and results data,
        and sends it back to client.

        :param string result: the data string to send back in the response to the client.
        """
        try:
            response = "HTTP/1.1 {0}\r\n".format(self._response_status)
            for header in self._response_headers:
                response += "{0}: {1}\r\n".format(*header)
            response += "\r\n"
            self._client_sock.send(response.encode("utf-8"))
            for data in result:
                if isinstance(data, str):
                    data = data.encode("utf-8")
                elif not isinstance(data, bytes):
                    data = str(data).encode("utf-8")
                bytes_sent = 0
                while bytes_sent < len(data):
                    try:
                        bytes_sent += self._client_sock.send(data[bytes_sent:])
                    except OSError as ex:
                        if ex.errno != 11:  # [Errno 11] EAGAIN
                            raise
            gc.collect()
        except OSError as ex:
            if ex.errno != 104:  # [Errno 104] ECONNRESET
                raise
        finally:
            #print("closing")
            self._client_sock.close()
            self._client_sock = None

    def client_available(self):
        """
        returns a client socket connection if available.
        Otherwise, returns None
        :return: the client
        :rtype: Socket
        """
        sock = None
        if not self._server_sock:
            print("Server has not been started, cannot check for clients!")
        elif not self._client_sock:
            self._server_sock.setblocking(False)
            try:
                self._client_sock, addr = self._server_sock.accept()
            except OSError as ex:
                if ex.errno != 11:  # [Errno 11] EAGAIN
                    raise

        return None

    def _start_response(self, status, response_headers):
        """
        The application callable will be given this method as the second param
        This is to be called before the application callable returns, to signify
        the response can be started with the given status and headers.

        :param string status: a status string including the code and reason. ex: "200 OK"
        :param list response_headers: a list of tuples to represent the headers.
            ex ("header-name", "header value")
        """
        self._response_status = status
        self._response_headers = [("Server", "esp32WSGIServer")] + response_headers

    def _get_environ(self, client):
        """
        The application callable will be given the resulting environ dictionary.
        It contains metadata about the incoming request and the request body ("wsgi.input")

        :param Socket client: socket to read the request from
        """
        env = {}
        line = readline(client).decode("utf-8")
        try:
            (method, path, ver) = line.rstrip("\r\n").split(None, 2)
        except ValueError:
            raise BadRequestError("Unknown request from client.")

        env["wsgi.version"] = (1, 0)
        env["wsgi.url_scheme"] = "http"
        env["wsgi.multithread"] = False
        env["wsgi.multiprocess"] = False
        env["wsgi.run_once"] = False

        env["REQUEST_METHOD"] = method
        env["SCRIPT_NAME"] = ""
        env["SERVER_NAME"] = str(wifi.radio.ipv4_address_ap)
        env["SERVER_PROTOCOL"] = ver
        env["SERVER_PORT"] = self.port
        if path.find("?") >= 0:
            env["PATH_INFO"] = path.split("?")[0]
            env["QUERY_STRING"] = path.split("?")[1]
        else:
            env["PATH_INFO"] = path

        headers = parse_headers(client)
        if "content-type" in headers:
            env["CONTENT_TYPE"] = headers.get("content-type")
        if "content-length" in headers:
            env["CONTENT_LENGTH"] = headers.get("content-length")
            body = read(client, int(env["CONTENT_LENGTH"]))
            env["wsgi.input"] = io.StringIO(body)
        else:
            body = read(client)
            env["wsgi.input"] = io.StringIO(body)
        for name, value in headers.items():
            key = "HTTP_" + name.replace("-", "_").upper()
            if key in env:
                value = "{0},{1}".format(env[key], value)
            env[key] = value

        return env
