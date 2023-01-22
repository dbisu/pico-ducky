# License : GPLv2.0
# copyright (c) 2021  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
# FeatherS2 board support

import socketpool
import time
import os
import storage

import wsgiserver as server
from adafruit_wsgi.wsgi_app import WSGIApp
import wifi

from duckyinpython import *

payload_html = """<!DOCTYPE html>
<html>
    <head> <title>Pico W Ducky</title> </head>
    <body> <h1>Pico W Ducky</h1>
        <table border="1"> <tr><th>Payload</th><th>Actions</th></tr> {} </table>
        <br>
        <a href="/new">New Script</a>
    </body>
</html>
"""

edit_html = """<!DOCTYPE html>
<html>
  <head>
    <title>Script Editor</title>
  </head>
  <body>
    <form action="/write/{}" method="POST">
      <textarea rows="5" cols="60" name="scriptData">{}</textarea>
      <br/>
      <input type="submit" value="submit"/>
    </form>
    <br>
    <a href="/ducky">Home</a>
  </body>
</html>
"""

new_html = """<!DOCTYPE html>
<html>
  <head>
    <title>New Script</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>@import url(https://fonts.googleapis.com/css2?family=Open+Sans&display=swap);button{margin-top:1em}.main{font-family:'Open Sans',sans-serif;margin:2%}textarea{width:100%;max-width:80vh}#ducky-input{height:50vh}</style>
  </head>
  <body>
    <div class="main">
        <form action="/new" method="POST">
            <p>New Script:</p>
            <textarea rows="1" name="scriptName" placeholder="script name"></textarea><br>
            <textarea id="ducky-input" rows="5" name="scriptData" placeholder="script"></textarea>
            <br><input type="submit" value="submit"/>
          </form>
          <a href="/ducky"><button>go back</button></a>
    </div>
  </body>
</html>
"""

response_html = """<!DOCTYPE html>
<html>
    <head> <title>Pico W Ducky</title> </head>
    <body> <h1>Pico W Ducky</h1>
        {}
        <br>
        <a href="/ducky">Home</a>
    </body>
</html>
"""

newrow_html = "<tr><td>{}</td><td><a href='/edit/{}'>Edit</a> / <a href='/run/{}'>Run</a></tr>"

def selectPayload(payload_number):
    if(payload_number == 1):
        payload = "payload.dd"

    elif(payload_number == 2):
        payload = "payload2.dd"

    elif(payload_number == 3):
        payload = "payload3.dd"

    elif(payload_number == 4):
        payload = "payload4.dd"

    else:
        # if all pins are high, then no switch is present
        # default to payload1
        payload = "payload.dd"

    return(payload)


def ducky_main(request):
    print("Ducky main")
    payloads = []
    rows = ""
    files = os.listdir()
    #print(files)
    for f in files:
        if ('.dd' in f) == True:
            payloads.append(f)
            newrow = newrow_html.format(f,f,f)
            #print(newrow)
            rows = rows + newrow

    response = payload_html.format(rows)

    return(response)

def cleanup_text(buffer):
    return_buffer = buffer.replace('+', ' ').replace('%0D%0A', '\n') + '\n'
    #print(return_buffer)
    return(return_buffer)

web_app = WSGIApp()

@web_app.route("/ducky")
def duck_main(request):
    response = ducky_main(request)
    return("200 OK", [('Content-Type', 'text/html')], response)

@web_app.route("/edit/<filename>")
def edit(request, filename):
    print("Editing ", filename)
    f = open(filename,"r",encoding='utf-8')
    textbuffer = ''
    for line in f:
        textbuffer = textbuffer + line
    f.close()
    response = edit_html.format(filename,textbuffer)
    #print(response)

    return("200 OK",[('Content-Type', 'text/html')], response)

@web_app.route("/write/<filename>",methods=["POST"])
def write_script(request, filename):

    data = request.body.getvalue()
    fields = data.split("&")
    form_data = {}
    for field in fields:
        key,value = field.split('=')
        form_data[key] = value

    #print(form_data)
    storage.remount("/",readonly=False)
    f = open(filename,"w",encoding='utf-8')
    textbuffer = form_data['scriptData']
    textbuffer = cleanup_text(textbuffer)
    #print(textbuffer)
    for line in textbuffer:
        f.write(line)
    f.close()
    storage.remount("/",readonly=True)
    response = response_html.format("Wrote script " + filename)
    return("200 OK",[('Content-Type', 'text/html')], response)

@web_app.route("/new",methods=['GET','POST'])
def write_new_script(request):
    response = ''
    if(request.method == 'GET'):
        response = new_html
    else:
        data = request.body.getvalue()
        fields = data.split("&")
        form_data = {}
        for field in fields:
            key,value = field.split('=')
            form_data[key] = value
        #print(form_data)
        filename = form_data['scriptName']
        textbuffer = form_data['scriptData']
        textbuffer = cleanup_text(textbuffer)
        storage.remount("/",readonly=False)
        f = open(filename,"w",encoding='utf-8')
        for line in textbuffer:
            f.write(line)
        f.close()
        storage.remount("/",readonly=True)
        response = response_html.format("Wrote script " + filename)
    return("200 OK",[('Content-Type', 'text/html')], response)

@web_app.route("/run/<filename>")
def run_script(request, filename):
    print("run_script ", filename)
    response = response_html.format("Running script " + filename)
    #print(response)
    runScript(filename)
    return("200 OK",[('Content-Type', 'text/html')], response)

@web_app.route("/")
def index(request):
    response = ducky_main(request)
    return("200 OK", [('Content-Type', 'text/html')], response)

@web_app.route("/api/run/<filenumber>")
def run_script(request, filenumber):
    filename = selectPayload(int(filenumber))
    print("run_script ", filenumber)
    response = response_html.format("Running script " + filename)
    #print(response)
    runScript(filename)
    return("200 OK",[('Content-Type', 'text/html')], response)

async def startWebService():

    HOST = repr(wifi.radio.ipv4_address_ap)
    PORT = 80        # Port to listen on
    print(HOST,PORT)

    wsgiServer = server.WSGIServer(80, application=web_app)

    print(f"open this IP in your browser: http://{HOST}:{PORT}/")

    # Start the server
    wsgiServer.start()
    while True:
        wsgiServer.update_poll()
        await asyncio.sleep(0)
