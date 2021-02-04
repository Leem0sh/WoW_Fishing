from numpy import where, array
import cv2
import pyautogui
import pyaudio
import audioop
import os
import time
import psutil
import click
import random
import configparser
import win32gui
import win32process
import sys
from tkinter import *
import datetime
from PIL import ImageGrab
import json


##########################################
#                                        #
#          PRESS KEY FUNCTION            #
#                                        #
##########################################
# TODO:            None                  #
##########################################


def press_key(key):
    pyautogui.keyDown(key)
    time.sleep(0.1)
    pyautogui.keyUp(key)


##########################################
#                                        #
#               SNAPSHOT                 #
#                                        #
##########################################
# TODO:            None                  #
##########################################


class Snapper:
    def __init__(self, master):
        self.master = master
        self.rect = None
        self.x = self.y = 0
        self.start_x = None
        self.start_y = None
        self.curX = None
        self.curY = None

        self.master.attributes("-transparent", "blue")
        self.master.geometry("200x50+200+200")
        self.master.title("ScreenSnapper")
        self.master.attributes("-topmost", True)
        self.menu_frame = Frame(master, bg="blue")
        self.menu_frame.pack(fill=BOTH, expand=YES)

        self.buttonBar = Frame(self.menu_frame, bg="")
        self.buttonBar.pack(fill=BOTH, expand=YES)

        self.snipButton = Button(
            self.buttonBar, width=3, command=self.createScreenCanvas, background="green"
        )
        self.snipButton.pack(expand=YES)

        self.master_screen = Toplevel(self.master)
        self.master_screen.withdraw()
        self.master_screen.attributes("-transparent", "blue")
        self.picture_frame = Frame(self.master_screen, background="blue")
        self.picture_frame.pack(fill=BOTH, expand=YES)

    def takeBoundedScreenShot(self, x1, y1, x2, y2):

        im = ImageGrab.grab(bbox=(x1 + 3, y1 + 3, x1 + x2 - 3, y1 + y2 - 3))
        im.save(os.path.join(__file__, "..\..\capture.png"))

    def createScreenCanvas(self):
        self.master_screen.deiconify()
        self.master.withdraw()

        self.screenCanvas = Canvas(self.picture_frame, cursor="cross", bg="grey11")
        self.screenCanvas.pack(fill=BOTH, expand=YES)

        self.screenCanvas.bind("<ButtonPress-1>", self.on_button_press)
        self.screenCanvas.bind("<B1-Motion>", self.on_move_press)
        self.screenCanvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.master_screen.attributes("-fullscreen", True)
        self.master_screen.attributes("-alpha", 0.3)
        self.master_screen.lift()
        self.master_screen.attributes("-topmost", True)

    def on_button_release(self, event):
        self.recPosition()

        if self.start_x <= self.curX and self.start_y <= self.curY:
            self.takeBoundedScreenShot(
                self.start_x,
                self.start_y,
                self.curX - self.start_x,
                self.curY - self.start_y,
            )

        elif self.start_x >= self.curX and self.start_y <= self.curY:
            self.takeBoundedScreenShot(
                self.curX,
                self.start_y,
                self.start_x - self.curX,
                self.curY - self.start_y,
            )

        elif self.start_x <= self.curX and self.start_y >= self.curY:
            self.takeBoundedScreenShot(
                self.start_x,
                self.curY,
                self.curX - self.start_x,
                self.start_y - self.curY,
            )

        elif self.start_x >= self.curX and self.start_y >= self.curY:
            self.takeBoundedScreenShot(
                self.curX, self.curY, self.start_x - self.curX, self.start_y - self.curY
            )

        self.exitScreenshotMode()
        return event

    def exitScreenshotMode(self):
        self.screenCanvas.destroy()
        self.master_screen.withdraw()
        self.master.deiconify()

    def exit_application(self):
        self.master.quit()

    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = self.screenCanvas.canvasx(event.x)
        self.start_y = self.screenCanvas.canvasy(event.y)

        self.rect = self.screenCanvas.create_rectangle(
            self.x, self.y, 1, 1, outline="red", width=3, fill="blue"
        )

    def on_move_press(self, event):
        self.curX, self.curY = (event.x, event.y)
        # expand rectangle as you drag the mouse
        self.screenCanvas.coords(
            self.rect, self.start_x, self.start_y, self.curX, self.curY
        )

    def recPosition(self):
        print(self.start_x)
        print(self.start_y)
        print(self.curX)
        print(self.curY)


##########################################
#                                        #
#              FISHING                   #
#                                        #
##########################################
# TODO:            None                  #
##########################################


class Fishing:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(
            os.path.join(__file__, "..\..\conf\conf.ini"), encoding="utf-8"
        )
        self.screen_size = None
        self.bbox = None
        self.window_start_point_x = None
        self.window_start_point_y = None
        self.window_size_w = None
        self.window_size_h = None
        self.p = pyaudio.PyAudio()
        self.audio_index = 0
        if self.config.get("Settings", "screens") == "off":
            self.screens = False
        else:
            self.screens = True
        self.catched = 0
        self.start_time = time.time()

    ##########################################
    #                                        #
    #             DEVICE CHECK               #
    #                                        #
    ##########################################
    # TODO:            None                  #
    ##########################################

    def device_check(self):
        for i in range(self.p.get_device_count()):
            if (
                self.p.get_device_info_by_index(i)["name"]
                == "CABLE Output (VB-Audio Virtual "
            ):
                self.audio_index = self.p.get_device_info_by_index(i)["index"]

    def get_proc_id(self):

        for proc in psutil.process_iter():
            if proc.name() == self.config.get("Settings", "ProcessName"):
                return proc.pid

    def _get_hwnd_by_pid(self, pid):
        """
        Args:
        pid: process id
        Returns:
        window handle
        """

        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    hwnds.append(hwnd)
                    return True

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return hwnds[0] if hwnds else None

    ##########################################
    #                                        #
    #              SCREEN SIZE               #
    #                                        #
    ##########################################
    # TODO:            None                  #
    ##########################################

    def check_screen_size(self, hwnd):
        try:
            win32gui.SetForegroundWindow(hwnd)
            self.bbox = win32gui.GetWindowRect(hwnd)
            self.window_start_point_x = self.bbox[0]
            self.window_start_point_y = self.bbox[1]
            self.window_size_w = self.bbox[2] - self.window_start_point_x
            self.window_size_h = self.bbox[3] - self.window_start_point_y
            print("Window %s:" % win32gui.GetWindowText(hwnd))
            print(
                "\tLocation: (%d, %d)"
                % (self.window_start_point_x, self.window_start_point_y)
            )
            print("\t    Size: (%d, %d)" % (self.window_size_w, self.window_size_h))
            print("BBOX: ", self.bbox)
        except:
            print(
                f"{self.config.get('Settings', 'ProcessName')}\
                process NOT found. Exiting in 1..."
            )
            time.sleep(1)
            exit(0)

    def send_float(self):
        pyautogui.press(self.config.get("Settings", "Button"))
        print("Button hit, waiting for animation")
        time.sleep(2.5)

    ##########################################
    #                                        #
    #             BAIT DEPLOY                #
    #                                        #
    ##########################################
    # TODO: region size according to         #
    #       size of the window               #
    #       - Done with bbox tuple           #
    ##########################################

    def bait_deploy(self, fish):
        pyautogui.moveTo(1, 1, 0)
        press_key("b")
        loc = pyautogui.locateOnScreen(
            os.path.join(__file__, f"..\..\icons\\{fish.lower()}.png"),
            confidence=0.7,
            region=(
                self.bbox[0] + 100,
                self.bbox[1] + 100,
                self.bbox[2] - 100,
                self.bbox[3] - 100,
            ),  # 1920x1080
        )
        if loc != None:
            center_of_icon = (loc[0] + (loc[2] / 2), loc[1] + (loc[3] / 2))
            self.move_mouse(center_of_icon)
            pyautogui.click(button="right")
            time.sleep(0.1)
            press_key("b")

            global bait_timer
            bait_timer = time.time()
            global bait_in_inventory
            bait_in_inventory = True
        else:
            # No bait in inventory
            bait_in_inventory = False

    ##########################################
    #                                        #
    #             FLOAT FINDER               #
    #                                        #
    ##########################################
    # TODO:    region of locateOnScreen      #
    #          based on window size          #
    ##########################################

    def find_float(self):

        count = 0
        while True:
            loc = pyautogui.locateOnScreen(
                os.path.join(__file__, "..\..\capture.png"),
                confidence=0.6,
                region=(
                    #### CATCHING WINDOW ####
                    int(self.window_size_w * 0.25),
                    int(self.window_size_h * 0.14),
                    int(self.window_size_w * 0.65),
                    int(self.window_size_h * 0.55),
                ),
            )
            if loc != None:
                print(loc[0] + (loc[2] / 2), loc[1] + (loc[3] / 2))
                return (loc[0] + (loc[2] / 2), loc[1] + (loc[3] / 2))
            else:
                count += 1
                if count == 10:
                    break
        # return (loc[0] + (loc[2] / 2), loc[1] + (loc[3] / 2))

    ##########################################
    #                                        #
    #            MOUSE MOVEMENT              #
    #                                        #
    ##########################################
    # TODO:            None                  #
    ##########################################

    def move_mouse(self, place):
        x = round(self.window_start_point_x + place[0])
        y = round(self.window_start_point_y + place[1])
        print(f"Moving cursor to {x} - {y}")
        pyautogui.moveTo(x, y, random.uniform(0.2, 1))

    ##########################################
    #                                        #
    #       LISTENING SPLASH SOUND           #
    #                                        #
    ##########################################
    # TODO:            None                  #
    ##########################################

    def listen(self):
        print("Listening..")
        CHUNK = 512  # CHUNKS of bytes to read each time from mic
        FORMAT = pyaudio.paInt16
        CHANNELS = 8
        RATE = 18000
        if self.config.get("Settings", "Device_check") == "on":
            INDEX = self.audio_index
        else:
            INDEX = int(self.config.get("Settings", "Index"))

        stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            input_device_index=INDEX,
        )
        current_data = ""

        success = False
        listening_start_time = time.time()
        count = 0
        while True:
            try:
                count += 1
                current_data = stream.read(CHUNK)
                rms = audioop.rms(current_data, 2)

                ##########################################
                #                                        #
                #                 RMS                    #
                #                                        #
                ##########################################

                print(rms)
                if rms > int(self.config.get("Settings", "RMS")):
                    if count > 10:
                        print("I heard something!")
                        success = True
                        break
                    else:
                        pass
                if time.time() - listening_start_time > 19:
                    print("No sounds caught, trying again")
                    break
            except IOError:
                break

        stream.close()
        # p.terminate()
        return success

    ##########################################
    #                                        #
    #                 UPTIME                 #
    #                                        #
    ##########################################
    # TODO:            None                  #
    ##########################################

    def timing(self):
        print(
            f"Script running for: {round((time.time() - self.start_time) /60, 2)} minutes"
        )

    ##########################################
    #                                        #
    #             CLICK FUNCTION             #
    #                                        #
    ##########################################
    # TODO:            None                  #
    ##########################################

    def snatch(self):
        time.sleep(random.uniform(0.1, 0.3))
        pyautogui.click()


##########################################
#                                        #
#              LOG WRITER                #
#                                        #
##########################################
# TODO:            None                  #
##########################################


def logWriter(start_time, catched, tries, wantcatch):
    data = {
        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)): {
            "EndTime": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Catched": catched,
            "Tries": tries,
            "SuccessRate": round((catched / tries) * 100, 2),
            "Took": round((time.time() - start_time) / 60, 2),
            "WantedToCatch": wantcatch,
        }
    }
    with open(
        os.path.join(__file__, "..\..\catchlog.log"), "a+", encoding="utf-8"
    ) as f:

        json.dump(data, f, indent=6)


##########################################
#                                        #
#             MAIN FUNCTION              #
#            WITH DECORATORS             #
#                                        #
##########################################
# TODO:            None                  #
##########################################


@click.command()
@click.option(
    "--wantcatch",
    "-c",
    prompt="How many fish do you want to catch?",
    help="While number of catched fish is lower than the number you want to catch, it's gonna be fishing",
    type=click.INT,
)
@click.option(
    "--printscreen", "-p", is_flag=True, help="Allowing recreating printscreen"
)
@click.option(
    "--bait",
    "-b",
    help="Uses bait before starting the session and inside session Usage: -b amberjack = Iridescent Amberjack / piranha = Spinefin Piranha / pike = Silvergrill Pike / bonefish = Pocked Bonefish ",
    type=click.Choice(["amberjack", "piranha", "pike", "bonefish"]),
)
def main(wantcatch, printscreen, bait):
    try:
        print(bait)
        s = Fishing()
        if s.config.get("Settings", "Device_check") == "on":
            s.device_check()
        else:
            pass
        ###### CAPTURE SCREEN #######
        if printscreen:
            root = Tk()
            app = Snapper(root)
            root.mainloop()
        ###### CAPTURE SCREEN #######

        proc_id = s.get_proc_id()
        hwnd = s._get_hwnd_by_pid(proc_id)
        s.check_screen_size(hwnd)

        tries = 0
        ### FIRST BAIT SECTION ###
        if bait:
            # FIRST BAIT FUNCTION
            s.bait_deploy(bait)

        #########################

        while s.catched < wantcatch:
            now = time.time()
            if bait and bait_in_inventory:
                if now - bait_timer > 1800:
                    s.bait_deploy(bait)

            tries += 1
            s.send_float()
            # image = s.make_screenshot()
            place = s.find_float()
            if not place:
                print("Bobber not found")
                continue
            print("Bobber found at " + str(place))
            s.move_mouse(place)
            if not s.listen():
                continue
            s.snatch()
            s.timing()
            time.sleep(random.uniform(0.8, 1.1))
            s.catched += 1
            print(
                f"Succesful {s.catched} / {tries} | {round((s.catched / tries)*100, 2)}%"
            )
            # time.sleep(1)
        s.p.terminate()
        logWriter(s.start_time, s.catched, tries, wantcatch)

        print("We done!")
    except KeyboardInterrupt:
        logWriter(s.start_time, s.catched, tries, wantcatch)