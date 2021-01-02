from http.server import BaseHTTPRequestHandler, HTTPServer
from http import HTTPStatus

import cec
import subprocess
import os
import time
import json
import cgi

# Test with:
# curl -X POST -H "Content-Type: application/json"  -d '{"command": "on"}' http://localhost:8484
class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_OPTIONS(self):
        # Send allow-origin header for preflight POST XHRs.
        self.send_response(HTTPStatus.NO_CONTENT.value)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'content-type')
        self.end_headers()

        
    def do_POST(self):
        print("received request.")
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        
        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
        
        # read the message and convert it into a python dictionary
        length = int(self.headers.get('content-length'))
        message = json.loads(self.rfile.read(length))

        if message.get("command") == "on":
          try:
            tv = cec.Device(cec.CECDEVICE_TV)
            tv.power_on()
            cec.set_active_source()
          except e:
            print(e)
        
        self._set_headers()
        self.wfile.write(json.dumps({"statusMsg": "Success"}).encode("utf8"))
        

def get_keymap():
    keymap = {
            0: "KP_Enter",
            1: "KP_Up",
            2: "KP_Down",
            3: "KP_Left",
            4: "KP_Right",
            13: "Alt_L+KP_F4",
            68: "Super_L",
            72: "Shift_L+KP_Tab",
            73: "KP_Tab",
            145: "BackSpace",
    }
    for i in range(32, 42):
        keymap[i] = f"KP_{i-32}"
    return keymap

KEYMAP = get_keymap()
# Sometimes only a keydown event is detected
# (with duration 0)
# Sometimes only a keyup (with duration > 0)
# sometimes both. This logic attempts
# to deduplicate these events and only pick one
# (the keydown event).
# (last_code, last_time, last_duration)
last_event = (None, None, None)

def handler(foo, code, duration):
    global last_event
    try:
        print(f"code: {code}, duration: {duration}, foo: {foo}")
        last_code, last_time, last_duration = last_event
        ts = time.time()
        if (code == last_code):
            if (ts - last_time < 1 and 
                last_duration == 0 and 
                duration > 0):
                print("Ignoring key up event")
                return
        last_event = (code, ts, duration)
        
        keysym = KEYMAP.get(code)
        if keysym is None:
            print(f"Unrecognized code: {code}")
            return
        print("executing keysym " + keysym)
        subprocess.check_output(["xdotool", "key", keysym])
    except Exception as e:
        print("Error executing command: " + str(e))


if __name__ == "__main__":
    cec.init()
    cec.add_callback(handler, cec.EVENT_KEYPRESS)
    os.environ["DISPLAY"] = ":0"
    os.environ["XAUTHORITY"] = "/home/pi/.Xauthority"
    print("Remote control python script running")
    httpd = HTTPServer(('', 8484), Server)
    httpd.serve_forever()
    


