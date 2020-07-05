import cv2
from numpy import where, array
import pyautogui
import pyaudio
import audioop
import os
import time
import psutil
import random
import configparser
import win32gui
import win32process
from PIL import ImageGrab

class Fishing():

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(".\\conf.ini", encoding="utf-8")
        self.screen_size = None
        self.bbox = None
        self.window_start_point_x = None
        self.window_start_point_y = None
        self.window_size_w = None
        self.window_size_h = None
        self.dev = False
        self.p = pyaudio.PyAudio()
        self.audio_index = 0
        if self.config.get("Settings", "screens") == "off":
            self.screens = False
        else:
            self.screens = True
        self.catched = 0
        self.start_time = time.time()

# p = pyaudio.PyAudio()
# for i in range(p.get_device_count()):
#     print (p.get_device_info_by_index(i))

    def device_check(self):
        for i in range(self.p.get_device_count()):
            if self.p.get_device_info_by_index(i)["name"] == "CABLE Output (VB-Audio Virtual ":
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




    def check_screen_size(self, hwnd):
        try:
            win32gui.SetForegroundWindow(hwnd)
            self.bbox = win32gui.GetWindowRect(hwnd)
            self.window_start_point_x = self.bbox[0]
            self.window_start_point_y = self.bbox[1]
            self.window_size_w = self.bbox[2] - self.window_start_point_x
            self.window_size_h = self.bbox[3] - self.window_start_point_y
            print("Window %s:" % win32gui.GetWindowText(hwnd))
            print("\tLocation: (%d, %d)" % (self.window_start_point_x, self.window_start_point_y))
            print("\t    Size: (%d, %d)" % (self.window_size_w, self.window_size_h))
            print("BBOX: ", self.bbox)
        except:
            print(f"{self.config.get('Settings', 'ProcessName')} process NOT found. Exiting in 1...")
            time.sleep(1)
            exit(0)




    def send_float(self):
        print ('Sending float')
        pyautogui.press(self.config.get("Settings", "Button"))
        print ('Float is sent, waiting animation')
        time.sleep(2)




    def make_screenshot(self):
        print ('Capturing screen')
        screenshot = ImageGrab.grab(self.bbox) # (0, 710, 410, 1010)
        screenshot = array(screenshot)
        # if self.dev:
        #     screenshot_name = '.\\var\\fishing_session_' + str(int(time.time())) + '.png'
        # else:
        #     screenshot_name = '.\\var\\fishing_session.png'
        # screenshot.save(screenshot_name)
        return screenshot




    def find_float(self, img_name):
        print ('Looking for float')
        # todo: maybe make some universal float without background? +1
        template = cv2.imread('.\\var\\bobber' + '.png', 0)

        # img_rgb = cv2.imread(img_name)
        img_gray = cv2.cvtColor(img_name, cv2.COLOR_BGR2GRAY)
        # print('got images')
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
        threshold = float(self.config.get("Settings", "Recognition_treshold"))
        loc = where( res >= threshold) # numpy.where
        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_name, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
        if loc[0].any():
            print ('Float found')
            if self.screens:
                cv2.imwrite('.\\var\\fishing_session_' + str(int(time.time())) + '_success.png', img_name)
            else:
                pass
            return (loc[1][0] + w / 2), (loc[0][0] + h / 2)




    def move_mouse(self, place):
        x = round(self.window_start_point_x + place[0])
        y = round(self.window_start_point_y + place[1])
   
        print(f"Moving cursor to {x} - {y}")
        pyautogui.moveTo(x, y, random.uniform(0.2,1))




    def listen(self):
        print ('Listening..')
        CHUNK = 512  # CHUNKS of bytes to read each time from mic
        FORMAT = pyaudio.paInt16
        CHANNELS = 8
        RATE = 18000
        if self.config.get("Settings", "Device_check") == "on":
            INDEX = self.audio_index
        else:
            INDEX = int(self.config.get("Settings", "Index"))


        stream = self.p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=INDEX)
        current_data = ''

        success = False
        listening_start_time = time.time()
        count = 0
        while True:
            try:
                count += 1
                current_data = stream.read(CHUNK)
                rms = audioop.rms(current_data, 2)
                print(rms) # uncomment if noise level check needed
                if rms > int(self.config.get("Settings", "RMS")):
                    if count > 10:
                        print ('I heard something!')
                        success = True
                        break
                    else:
                        pass
                if time.time() - listening_start_time > 19:
                    print ('No sounds caught, trying again')
                    break
            except IOError:
                break

        stream.close()
        # p.terminate()
        return success


    def timing(self):
        print(f"Script running for: {round((time.time() - self.start_time) /60, 2)} minutes")


    def snatch(self):
        print('Snatching!')
        time.sleep(random.uniform(0.2,1))
        pyautogui.click()


if __name__ == "__main__":

    s = Fishing()
    if s.config.get("Settings", "Device_check") == "on":
        s.device_check()
    else:
        pass
    proc_id = s.get_proc_id()
    hwnd = s._get_hwnd_by_pid(proc_id)
    
    s.check_screen_size(hwnd)
    tries = 0
    while not s.dev:
        tries += 1
        s.send_float()
        image = s.make_screenshot()
        place = s.find_float(image)
        if not place:
            print ('Bobber not found')
            
            continue
        print('Bobber found at ' + str(place))
        s.move_mouse(place)
        if not s.listen():
            print ('If we didn\' hear anything, lets try again')
            time.sleep(1)
            continue
        s.snatch()
        s.timing()
        time.sleep(random.uniform(0.8,1.1))
        s.catched += 1
        print ('guess we\'ve snatched something')
        if s.catched == int(s.config.get("Settings", "Catched")):
            break
        print ('catched ' + str(s.catched))
    s.p.terminate()
    print("We done!")