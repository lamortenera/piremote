import cec
import subprocess
import os
import time


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
            73: "KP_Tab"
    }
    for i in range(32, 42):
        keymap[i] = f"KP_{i-32}"
    return keymap

KEYMAP = get_keymap()

def handler(_, code, duration):
    print(f"code: {code}, duration: {duration}")
    if duration > 0:
        print("ignoring key")
        return
    keysym = KEYMAP.get(code)
    if keysym is None:
        print(f"Unrecognized code: {code}")
        return
    out = subprocess.check_output(["xdotool", "key", keysym], stderr=subprocess.STDOUT)
    if out:
        print(out)


if __name__ == "__main__":
    cec.init()
    cec.add_callback(handler, cec.EVENT_KEYPRESS)
    os.environ["DISPLAY"] = ":0"
    os.environ["XAUTHORITY"] = "/home/pi/.Xauthority"
    print("Remote control python script running")
    while True:
        time.sleep(1)

