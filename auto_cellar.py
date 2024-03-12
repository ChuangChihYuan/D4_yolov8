
from ultralytics import YOLO
import cv2
import numpy as np
import tkinter as tk
import pyautogui
from pynput import keyboard
import win32ui
from ctypes import windll
from PIL import Image, ImageTk
import win32gui
import win32con
import win32api
import time
import random
import threading
import math
import pytesseract
import multiprocessing
import psutil


from image_list import find_img

class Script():
    def __init__(self, title):
        self.hwnd = win32gui.FindWindow(None, title)
        self.script_key_start_check = keyboard.Key.f2
        self.script_start_flag = False
        self.screenshot_data = None
        self.root = None
        self.canvas = None
        self.auto_sell_var = None
        self.script_auto_sell_flag = False
        self.bgcontrol = Bg_control(title)


    def set_tk_canvas(self, title, width, height):
        self.root = tk.Tk()
        self.root.title(title)

        self.status_label = tk.Label(self.root, text=" 腳本狀態: ")
        self.status_label.pack()

        self.status_show_label = tk.Label(self.root, text="未啟動")
        self.status_show_label.pack()

        self.start_btn = tk.Button(self.root, text="啟動腳本", command=self.start_script)
        self.start_btn.pack()

        self.stop_btn = tk.Button(self.root, text="停止腳本", command=self.stop_script, state=tk.DISABLED)
        self.stop_btn.pack()

        self.screenshot_thread = None

        # 建立框框
        self.auto_sell_var = tk.IntVar()
        checkbox = tk.Checkbutton(self.root, text="自動賣裝", variable=self.auto_sell_var , command=self.on_checkbox_change)
        checkbox.pack()

        self.canvas = tk.Canvas(self.root, width=width, height=height)
        self.canvas.pack()

        # self.set_toplevel1 = tk.Toplevel()
        # self.set_toplevel1.title(title)
        # self.set_toplevel2 = tk.Canvas(self.set_toplevel1, width=width, height=height)
        # self.set_toplevel2.pack()

        self.root.mainloop()

    def on_checkbox_change(self):
        if self.auto_sell_var.get() == 1:
            self.script_auto_sell_flag = True
        else:
            self.script_auto_sell_flag = False
        print(f"self.script_auto_sell_flag: {self.script_auto_sell_flag}")

    def start_script(self):
        self.status_show_label.config(text="啟動中")
        self.script_start_flag = True

        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)


    def stop_script(self):
        self.status_show_label.config(text="未啟動")
        self.script_start_flag = False

        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)


    def show_screenshot(self, image):
        # 转换图像为 PIL 图像对象
        pil_image = Image.fromarray(image)

        # 转换为 PhotoImage 格式
        img = ImageTk.PhotoImage(pil_image)
        # 显示屏幕截图在画布上
        self.canvas.create_image(0, 0, anchor="nw", image=img)
        self.canvas.image = img  # 保持引用，避免被垃圾回收

    def set_key_start_check(self, set_key='f2'):
        reset_key = ''
        match set_key:
            case 'f1':
                reset_key = keyboard.Key.f1
            case 'f2':
                reset_key = keyboard.Key.f2
            case 'f3':
                reset_key = keyboard.Key.f3
            case 'f4':
                reset_key = keyboard.Key.f4
            case 'f5':
                reset_key = keyboard.Key.f5
            case 'f6':
                reset_key = keyboard.Key.f6
            case 'f7':
                reset_key = keyboard.Key.f7
            case 'f8':
                reset_key = keyboard.Key.f8
            case 'f9':
                reset_key = keyboard.Key.f9
            case 'f10':
                reset_key = keyboard.Key.f10
            case 'f11':
                reset_key = keyboard.Key.f11
            case 'f12':
                reset_key = keyboard.Key.f12

        self.script_key_start_check = reset_key

    def on_key_press(self, key):
        if key == self.script_key_start_check:
            if self.script_start_flag == False:
                self.script_start_flag = True
                print(f"腳本啟動")
            elif self.script_start_flag == True:
                self.script_start_flag = False
                print(f"腳本暫停")


    def screen_capture(self, save=False):
        # 如果使用高 DPI 显示器（或 > 100% 缩放尺寸），添加下面一行，否则注释掉
        # windll.user32.SetProcessDPIAware()

        # 根据您是想要整个窗口还是只需要 client area 来更改下面的行。
        left, top, right, bot = win32gui.GetClientRect(self.hwnd)
        w = right - left
        h = bot - top

        hwndDC = win32gui.GetWindowDC(self.hwnd)  # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)  # 根据窗口的DC获取mfcDC
        saveDC = mfcDC.CreateCompatibleDC()  # mfcDC创建可兼容的DC

        saveBitMap = win32ui.CreateBitmap()  # 创建bitmap准备保存图片
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)  # 为bitmap开辟空间

        saveDC.SelectObject(saveBitMap)  # 高度saveDC，将截图保存到saveBitmap中

        # 选择合适的 window number，如0，1，2，3，直到截图从黑色变为正常画面
        result = windll.user32.PrintWindow(self.hwnd, saveDC.GetSafeHdc(), 3)

        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)

        if save == True:
            im = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1)
            im.save("screenshot.jpg")  # 调试时可打开，不保存图片可节省大量时间（约0.2s）
        else:
            im = np.frombuffer(bmpstr, dtype='uint8')
            im.shape = (h, w, 4)
            im = cv2.cvtColor(im, cv2.COLOR_BGRA2RGB)

        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, hwndDC)

        if result == 1:
            self.screenshot_data = np.array(im)
        else:
            self.screenshot_data = np.array(0)  # 返回图片

        return self.screenshot_data

    def find_image_pattern(self, find_pattern, threshold_value=0.5, mask=((0, 0, 0, 0),), show_img=False, add_return_xy=True):
        # 截圖
        screenshot_mask = self.screen_capture(save=False)

        # 遮罩
        for mask_xy in mask:
            if mask_xy[0] != 0 or mask_xy[1] != 0 or mask_xy[2] != 0 or mask_xy[3] != 0:
                # 排除指定區域
                # 30,380
                # 350,550
                x1, y1 = mask_xy[0], mask_xy[1]
                x2, y2 = mask_xy[2], mask_xy[3]
                x, y = x1, y1
                w, h = x2 - x1, y2 - y1
                screenshot_mask[y:y + h, x:x + w] = 0

        if type(find_pattern) is dict:
            find_x = None
            find_y = None
            find_flag = None
            for i in find_pattern:
                find_x, find_y, find_flag = self.find_image_pattern_function(screenshot_mask, find_pattern.get(i), threshold_value, show_img)
                # print(find_pattern.get(i))
                if find_flag == True:
                    break
            if add_return_xy == True:
                return find_x, find_y, find_flag
            else:
                return find_flag
        else:
            find_x, find_y, find_flag = self.find_image_pattern_function(screenshot_mask, find_pattern, threshold_value, show_img)

        if add_return_xy == True:
            return find_x, find_y, find_flag
        else:
            return find_flag



    def find_image_pattern_function(self, screenshot_mask, find_pattern, threshold_value, show_img):
        # 小圖案
        pattern_img = cv2.imread(find_pattern, cv2.IMREAD_UNCHANGED)
        pattern_img_mid_x = int(pattern_img.shape[1] / 2)
        pattern_img_mid_y = int(pattern_img.shape[0] / 2)

        # 创建灰度图像
        pattern_gray = cv2.cvtColor(pattern_img, cv2.COLOR_BGR2RGB)

        # 在屏幕截图中查找相似的小图像
        result = cv2.matchTemplate(screenshot_mask, pattern_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        # 获取小图像的宽度和高度
        pattern_height, pattern_width = pattern_gray.shape[:2]

        # 设置相似度阈值
        similarity_threshold = threshold_value
        top_left = None
        # 如果最大相似度大于等于阈值，则认为匹配成功
        if max_val >= similarity_threshold:
            # 在屏幕截图中绘制红色边框并显示坐标
            top_left = max_loc
            bottom_right = (top_left[0] + pattern_width, top_left[1] + pattern_height)
            cv2.rectangle(screenshot_mask, top_left, bottom_right, (255, 0, 0), 2)
            # 显示坐标信息
            cv2.putText(screenshot_mask, f"{top_left}: {find_pattern}", (top_left[0] - 150, top_left[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        # 显示结果在画布上
        if show_img == True:
            self.show_screenshot(screenshot_mask)
        if top_left != None:
            return top_left[0] + pattern_img_mid_x, top_left[1] + pattern_img_mid_y, True
        else:
            return None, None, False



class Bg_control():
    def __init__(self, title):
        self.hwnd = win32gui.FindWindow(None, title)


    def bg_hwmd_activate(self):
        win32gui.SendMessage(self.hwnd, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)

    def bg_hwmd_key_down(self, temp_key):
        win32gui.SendMessage(self.hwnd, win32con.WM_KEYDOWN, temp_key, 0)

    def bg_hwmd_key_up(self, temp_key):
        win32gui.SendMessage(self.hwnd, win32con.WM_KEYUP, temp_key, 0)

    def bg_hwmd_mouse_move(self, temp_xy=(0, 0)):
        win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.WM_MOUSEMOVE, win32api.MAKELONG(temp_xy[0], temp_xy[1]))

    def bg_hwmd_left_mouse_down(self, temp_xy=(0, 0)):
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.WM_LBUTTONDOWN, win32api.MAKELONG(temp_xy[0], temp_xy[1]))

    def bg_hwmd_left_mouse_up(self, temp_xy=(0, 0)):
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.WM_LBUTTONUP, win32api.MAKELONG(temp_xy[0], temp_xy[1]))

    def bg_hwmd_right_mouse_down(self, temp_xy=(0, 0)):
        win32api.SendMessage(self.hwnd, win32con.WM_RBUTTONDOWN, win32con.WM_RBUTTONDOWN, win32api.MAKELONG(temp_xy[0], temp_xy[1]))

    def bg_hwmd_right_mouse_up(self, temp_xy=(0, 0)):
        win32api.SendMessage(self.hwnd, win32con.WM_RBUTTONUP, win32con.WM_RBUTTONUP, win32api.MAKELONG(temp_xy[0], temp_xy[1]))

    def bg_hwmd_mid_mouse_zoom_out(self):
        win32api.SendMessage(self.hwnd, win32con.WM_MOUSEWHEEL, -win32con.WHEEL_DELTA, 0)

    def bg_hwmd_mid_mouse_zoom_in(self):
        win32api.SendMessage(self.hwnd, win32con.WM_MOUSEWHEEL, win32con.WHEEL_DELTA, 0)


    def add_random_time(self, min_random_time, max_random_time):
        return random.uniform(min_random_time, max_random_time)


    def bg_key_press_and_move(self, temp_key, delay_time=0.0, add_random_time=0.0, temp_xy=(0, 0), distance_time_cal=False):
        self.bg_hwmd_activate()
        time.sleep(delay_time + add_random_time)
        self.bg_hwmd_mouse_move(temp_xy)
        time.sleep(delay_time + add_random_time)
        self.bg_hwmd_key_down(temp_key)
        time.sleep(delay_time + add_random_time)
        self.bg_hwmd_key_up(temp_key)
        if distance_time_cal == True:
            distance = (400 - temp_xy[0]) ** 2 + (290 - temp_xy[1]) ** 2
            if distance != 0:
                distance_time = math.sqrt(distance)/250
                print(f"distance_time: {distance_time / 250}")
                time.sleep(distance_time)

    def bg_key_press(self, temp_key, delay_time=0.0, add_random_time=0.0):
        self.bg_hwmd_activate()
        time.sleep(0.05)
        self.bg_hwmd_key_down(temp_key)
        time.sleep(delay_time + add_random_time)
        self.bg_hwmd_key_up(temp_key)

    def bg_mouse_move(self, temp_xy=(0, 0), delay_time=0.0, add_random_time=0.0):
        self.bg_hwmd_activate()
        time.sleep(delay_time + add_random_time)
        self.bg_hwmd_mouse_move(temp_xy)
        time.sleep(delay_time + add_random_time)

    def bg_left_mouse_click(self, temp_xy=(0, 0), delay_time=0.0, add_random_time=0.0, distance_time_cal=False):
        self.bg_hwmd_activate()
        time.sleep(delay_time + add_random_time)
        self.bg_hwmd_mouse_move(temp_xy)
        time.sleep(delay_time + add_random_time)
        self.bg_hwmd_left_mouse_down(temp_xy)
        time.sleep(delay_time + add_random_time)
        self.bg_hwmd_left_mouse_up(temp_xy)
        if distance_time_cal == True:
            distance = (400 - temp_xy[0]) ** 2 + (290 - temp_xy[1]) ** 2
            if distance != 0:
                distance_time = math.sqrt(distance)/250
                print(f"distance_time: {distance_time / 250}")
                time.sleep(distance_time)

    def bg_right_mouse_click(self, temp_xy=(0, 0), delay_time=0.0, add_random_time=0.0):
        self.bg_hwmd_activate()
        time.sleep(delay_time + add_random_time)
        self.bg_hwmd_mouse_move(temp_xy)
        time.sleep(delay_time + add_random_time)
        self.bg_hwmd_right_mouse_down(temp_xy)
        time.sleep(delay_time + add_random_time)
        self.bg_hwmd_right_mouse_up(temp_xy)

    def bg_mid_mouse_wheel_zoom(self,zoom='+', temp_xy=(0, 0), delay_time=0.0, add_random_time=0.0):
        self.bg_hwmd_activate()
        time.sleep(delay_time + add_random_time)
        self.bg_hwmd_mouse_move(temp_xy)
        time.sleep(delay_time + add_random_time)
        if zoom == '+':
            self.bg_hwmd_mid_mouse_zoom_out()
        elif zoom == '-':
            self.bg_hwmd_mid_mouse_zoom_in()
        time.sleep(delay_time + add_random_time)




def get_all_windows():
    def callback(hwnd, windows_list):
        window_title = win32gui.GetWindowText(hwnd)
        if window_title:
            windows_list.append((hwnd, window_title))

    windows_list = []
    win32gui.EnumWindows(callback, windows_list)
    return windows_list

def get_child_windows(parent_handle):
    child_windows = []
    win32gui.EnumChildWindows(parent_handle, lambda hwnd, param: param.append(hwnd), child_windows)
    return child_windows

def print_window_hierarchy(hwnd, indent=0):
    window_title = win32gui.GetWindowText(hwnd)
    if window_title:
        print(" " * indent + f"Window: {window_title} ({hwnd})")
        children = get_child_windows(hwnd)
        for child in children:
            print_window_hierarchy(child, indent + 4)

def find_monter_attack():
    global lose_flag
    # 找怪打
    find_monster_flag = 1
    find_monster_loop_cnt = 25
    skill_loop_cnt = 0
    find_flag1 = 0
    death_cnt = 5
    while find_monster_flag:
        if script.find_image_pattern(find_pattern=find_img.get('系統').get('死亡'), threshold_value=0.8, show_img=True, add_return_xy=False) == True:
            time.sleep(6)
            while script.find_image_pattern(find_pattern=find_img.get('系統').get('復活'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                time.sleep(1)
            find_x, find_y, find_flag = script.find_image_pattern(find_pattern=find_img.get('系統').get('復活'),
                                                                  threshold_value=0.8, show_img=True)
            script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)
            time.sleep(2)

            death_cnt = death_cnt - 1
            if death_cnt == 0:
                lose_flag = True
                break

            script.bgcontrol.bg_left_mouse_click((61, 334), 0.1)
            time.sleep(1)
            script.bgcontrol.bg_left_mouse_click((162, 144), 0.1)
            time.sleep(1)
            script.bgcontrol.bg_left_mouse_click((188, 168), 0.1)
            time.sleep(1)

        # name[0] = {
        # 0: 'enemy',
        # 1: 'friend',
        # 2: 'yellow_item',
        # 3: 'blue_item',
        # 4: 'chest',
        # 5: 'healing_potion',
        # 6: 'waypoint',
        # 7: 'gold',
        # 8: 'althar',
        # 9: 'uniq_item'}
        screenshot_img = script.screen_capture()
        screenshot_img_RGB = cv2.cvtColor(screenshot_img, cv2.COLOR_BGR2RGB)
        results = model(source=screenshot_img_RGB, device=0, classes=[0], conf=0.6, verbose=False)

        if len(results[0].boxes) != 0:

            res_plotted = results[0].plot()
            res_plotted_RGB = cv2.cvtColor(res_plotted, cv2.COLOR_RGB2BGR)
            script.show_screenshot(res_plotted_RGB)
            test_cnt = 0
            boxes = results[0].boxes
            for box in boxes:
                test_cnt = test_cnt + 1
                # ! print(f"box{test_cnt} = {int(box.cls[0])}, (x,y) = {int(box.xywh[0][0])}, {int(box.xywh[0][1])}")
            find_monster_flag = 1
            find_flag1 = 1
            detect_pos_x1 = int(results[0].boxes[0].xywh[0][0])
            detect_pos_y1 = int(results[0].boxes[0].xywh[0][1])
            # ! print(f"detect_pos_x1:{detect_pos_x1}, detect_pos_y1:{detect_pos_y1}")
        else:
            find_monster_loop_cnt = find_monster_loop_cnt - 1
            if find_monster_loop_cnt == 0:
                find_monster_flag = 0

        if find_flag1 == 1:
            script.bgcontrol.bg_left_mouse_click((detect_pos_x1, detect_pos_y1), 0.1)
            script.bgcontrol.bg_key_press(ord('1'), 0.5)
            if skill_loop_cnt == 0:
                script.bgcontrol.bg_key_press(ord('5'), 0.1)
                script.bgcontrol.bg_key_press(ord('Q'), 0.1)
                skill_loop_cnt = 1
            elif skill_loop_cnt == 1:
                script.bgcontrol.bg_key_press(ord('2'), 0.1)
                skill_loop_cnt = 2
            elif skill_loop_cnt == 2:
                script.bgcontrol.bg_key_press(ord('3'), 0.1)
                skill_loop_cnt = 3
            elif skill_loop_cnt == 3:
                script.bgcontrol.bg_key_press(ord('4'), 0.1)
                skill_loop_cnt = 0

            find_flag1 = 0
            find_monster_loop_cnt = 25
        else:
            print(f"沒找到怪物")


if __name__ == "__main__":
    script = Script("《暗黑破壞神 IV》")

    print(script.hwnd)
    print(script.bgcontrol.hwnd)




    time.sleep(1)
    # D4 ScreenShot Create 1
    # script.set_tk_canvas("D4 ScreenShot", 800, 600)
    # time.sleep(1)
    # script.bgcontrol.bg_key_press(ord('I'), 0.1)
    # time.sleep(1)
    # # (774, 365)背包整理
    # script.bgcontrol.bg_left_mouse_click((200, 200), 0.1)
    # time.sleep(1)
    # script.bgcontrol.bg_key_press(ord('I'), 0.1)
    # time.sleep(1)
    # time.sleep(1)
    # script.bgcontrol.bg_key_press(ord('M'), 0.1)
    # time.sleep(1)
    # # script.bgcontrol.bg_right_mouse_click((700, 300), 0.1)
    # for i in range(0,5,1):
    #     print(f"i+:{i}")
    #     script.bgcontrol.bg_key_press(ord('M'), 0.1)
    #     script.bgcontrol.bg_mid_mouse_wheel_zoom('+', (50, 50), 0.1)
    #
    # time.sleep(3)
    # for i in range(0,5,1):
    #     print(f"i-:{i}")
    #     script.bgcontrol.bg_mid_mouse_wheel_zoom('-', (50, 50), 0.1)


    time.sleep(1)
    # script.bgcontrol.bg_key_press(ord('M'), 0.1)
    # time.sleep(1)

    run_tk_loop_thread = threading.Thread(target=script.set_tk_canvas, args=("D4 ScreenShot", 800, 600))

    # script.test_label1 = None
    # script.test_label2 = None
    # script.set_tk_toplevel("QQ", 800, 600)
    # script.set_toplevel1 = tk.Toplevel()
    # script.set_toplevel1.title("QQ")
    # script.set_toplevel2 = tk.Canvas(script.set_toplevel1, width=200, height=200)
    # script.set_toplevel2.pack()

    # 创建键盘监听器
    # listener = keyboard.Listener(on_press=script.on_key_press)
    # listener.start()
    run_tk_loop_thread.start()

    # print(f"find_img.get('地圖') : {find_img.get('地圖')}")
    #
    # print(f"find_img.get('物品') : {find_img.get('物品')}  , len(): {len(find_img.get('物品'))}")
    #
    # print(f"find_img.get('怪物血量') : {find_img.get('怪物血量')}")
    #
    # # location = image_locations.get('神聖裝備', {}).get('位置1')
    # print(f"find_img.get('物品','神聖裝備') : {find_img.get('物品').get('神聖裝備')}")

    # script.bgcontrol.bg_hwmd_activate()
    # time.sleep(0.1)
    # script.bgcontrol.bg_key_press(win32con.VK_ESCAPE, 0.5)
    # time.sleep(0.1)

    print(f"加載yolov8 model中!")
    model = YOLO("D4_Model.pt")
    screenshot_img = script.screen_capture()
    screenshot_img_RGB = cv2.cvtColor(screenshot_img, cv2.COLOR_BGR2RGB)
    results = model(source=screenshot_img_RGB, device=0, classes=[0], conf=0.6, verbose=False)
    print(f"加載yolov8 model 完成!")

    # name[0] = {
    # 0: 'enemy',
    # 1: 'friend',
    # 2: 'yellow_item',
    # 3: 'blue_item',
    # 4: 'chest',
    # 5: 'healing_potion',
    # 6: 'waypoint',
    # 7: 'gold',
    # 8: 'althar',
    # 9: 'uniq_item'}

    # while True:
    #     print(f"qq")
    #     time.sleep(0.1)
    #     screenshot_img = script.screen_capture()
    #     screenshot_img_RGB = cv2.cvtColor(screenshot_img, cv2.COLOR_BGR2RGB)
    #     results = model(source=screenshot_img_RGB, device=0, classes=[6], conf=0.6, verbose=False)
    #     print(f"name[0] = {results[0].names}")
    #     if len(results[0].boxes) != 0:
    #         res_plotted = results[0].plot()
    #         res_plotted_RGB = cv2.cvtColor(res_plotted, cv2.COLOR_RGB2BGR)
    #         script.show_screenshot(res_plotted_RGB)
    #         test_cnt = 0
    #         boxes = results[0].boxes



    while True:
        lose_flag = False
        if script.script_start_flag == True:
            if script.script_auto_sell_flag == True:
                print("自動賣裝勾")

            if script.script_auto_sell_flag == False:
                print("自動賣裝不勾")


            # 檢查是否回到隱士居所
            while script.find_image_pattern(find_pattern=find_img.get('系統').get('隱士居所'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                print("還沒回到隱士居所")
                time.sleep(0.5)
            # 檢查包包
            # 按下I
            time.sleep(1)
            # 打開包包
            script.bgcontrol.bg_key_press(ord('I'), 0.5)
            time.sleep(1)
            if script.find_image_pattern(find_pattern=find_img.get('系統').get('背包'), threshold_value=0.8,show_img=True, add_return_xy=False) == True:
                print(f"背包還很大")
                script.bgcontrol.bg_key_press(ord('I'), 0.5)
                time.sleep(0.5)
            else:
                # 執行自動清包包 或 等待手動清包包
                print(f"背包滿出來")
                # 關閉包包
                script.bgcontrol.bg_key_press(ord('I'), 0.5)
                time.sleep(1)
                # 打開地圖
                script.bgcontrol.bg_key_press(ord('M'), 0.5)
                time.sleep(2)
                # 找聖修亞瑞
                find_x, find_y, find_flag = script.find_image_pattern(find_pattern=find_img.get('系統').get('聖修亞瑞'), threshold_value=0.8, show_img=True, add_return_xy=True)
                script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)
                time.sleep(2)
                # 找TP
                find_x, find_y, find_flag = script.find_image_pattern(find_pattern=find_img.get('系統').get('傳送點'), threshold_value=0.7, show_img=True, add_return_xy=True)
                script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)
                time.sleep(2)
                # 找接受
                find_x, find_y, find_flag = script.find_image_pattern(find_pattern=find_img.get('系統').get('接受'), threshold_value=0.8, show_img=True, add_return_xy=True)
                script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)

                time.sleep(6)
                # 等待回到村莊 馬格雷夫
                while script.find_image_pattern(find_pattern=find_img.get('系統').get('馬格雷夫'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                    time.sleep(1)

                time.sleep(2)
                script.bgcontrol.bg_key_press_and_move(temp_key=ord('8'), delay_time=0.1, temp_xy=(25, 225), distance_time_cal=True)
                script.bgcontrol.bg_key_press_and_move(temp_key=ord('8'), delay_time=0.1, temp_xy=(72, 142), distance_time_cal=True)
                script.bgcontrol.bg_key_press_and_move(temp_key=ord('F'), delay_time=0.5, temp_xy=(459, 74), distance_time_cal=True)
                time.sleep(1)

                if script.script_auto_sell_flag == True:
                    # 開始賣裝備
                    for y in range(0,3,1):
                        # 起始位置
                        temp_y = 400 + 40 * y
                        for x in range(0,11,1):
                            temp_x = 510 + 25 * x
                            script.bgcontrol.bg_mouse_move((temp_x, temp_y), 0.25)
                            time.sleep(0.25)
                            if script.find_image_pattern(find_pattern=find_img.get('物品欄'), threshold_value=0.8, show_img=True, add_return_xy=False) == True:
                                print(f"傳奇")
                            else:
                                print(f"不是傳奇")
                                script.bgcontrol.bg_right_mouse_click((temp_x, temp_y), 0.1)

                    # 裝備重新排序
                    time.sleep(0.5)
                    script.bgcontrol.bg_left_mouse_click((774, 365), 0.1)

                    # 關閉 裝備欄
                    time.sleep(1)
                    script.bgcontrol.bg_key_press(win32con.VK_ESCAPE, 0.5)
                    script.bgcontrol.bg_key_press_and_move(temp_key=ord('8'), delay_time=0.1, temp_xy=(421, 512),distance_time_cal=True)
                    script.bgcontrol.bg_key_press_and_move(temp_key=ord('8'), delay_time=0.1, temp_xy=(788, 308),distance_time_cal=True)
                    script.bgcontrol.bg_key_press_and_move(temp_key=ord('8'), delay_time=0.1, temp_xy=(669, 484),distance_time_cal=True)

                    # 找傳送門
                    time.sleep(1)
                    # screenshot_img = script.screen_capture()
                    # screenshot_img_RGB = cv2.cvtColor(screenshot_img, cv2.COLOR_BGR2RGB)
                    # results = model(source=screenshot_img_RGB, device=0, classes=[6], conf=0.6, verbose=False)
                    #
                    # if len(results[0].boxes) != 0:
                    #
                    #     res_plotted = results[0].plot()
                    #     res_plotted_RGB = cv2.cvtColor(res_plotted, cv2.COLOR_RGB2BGR)
                    #     script.show_screenshot(res_plotted_RGB)
                    #     test_cnt = 0
                    #     boxes = results[0].boxes
                    #     for box in boxes:
                    #         test_cnt = test_cnt + 1
                    #     find_flag1 = 1
                    #     detect_pos_x1 = int(results[0].boxes[0].xywh[0][0])
                    #     detect_pos_y1 = int(results[0].boxes[0].xywh[0][1])
                    #     script.bgcontrol.bg_left_mouse_click((detect_pos_x1, detect_pos_y1), 0.1, distance_time_cal=True)
                    script.bgcontrol.bg_left_mouse_click((559, 188), 0.1)
                    time.sleep(5)

                while script.find_image_pattern(find_pattern=find_img.get('系統').get('隱士居所'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                    time.sleep(1)
                    print("還沒回到隱士居所 Q1")



            # 走到定點
            script.bgcontrol.bg_left_mouse_click((61, 334), 0.1)
            time.sleep(1)
            script.bgcontrol.bg_left_mouse_click((162, 144), 0.1)
            time.sleep(1)
            script.bgcontrol.bg_left_mouse_click((188, 168), 0.1)
            time.sleep(2)
            # 到達定點


            # name[0] = {
            # 0: 'enemy',
            # 1: 'friend',
            # 2: 'yellow_item',
            # 3: 'blue_item',
            # 4: 'chest',
            # 5: 'healing_potion',
            # 6: 'waypoint',
            # 7: 'gold',
            # 8: 'althar',
            # 9: 'uniq_item'}

            # 找事件_箱子_開始
            screenshot_img = script.screen_capture()
            screenshot_img_RGB = cv2.cvtColor(screenshot_img, cv2.COLOR_BGR2RGB)
            results = model(source=screenshot_img_RGB, device=0, classes=[4], conf=0.6, verbose=False)

            if len(results[0].boxes) != 0:
                res_plotted = results[0].plot()
                res_plotted_RGB = cv2.cvtColor(res_plotted, cv2.COLOR_RGB2BGR)
                script.show_screenshot(res_plotted_RGB)
                test_cnt = 0
                boxes = results[0].boxes
                for box in boxes:
                    test_cnt = test_cnt + 1
                find_flag1 = 1
                detect_pos_x1 = int(results[0].boxes[0].xywh[0][0])
                detect_pos_y1 = int(results[0].boxes[0].xywh[0][1])
                script.bgcontrol.bg_left_mouse_click((detect_pos_x1, detect_pos_y1), 0.1, distance_time_cal=True)

            # 找怪打
            print(f"開始找怪物")
            find_monter_attack()

            # 找事件1_開始 1
            find_x, find_y, find_flag = script.find_image_pattern(find_pattern=find_img.get('任務').get('事件1_開始'), threshold_value=0.8, mask=((600, 0, 800, 600),), show_img=True, add_return_xy=True)
            if find_flag == True:
                script.bgcontrol.bg_left_mouse_click((find_x + 10, find_y + 60), 0.1)
                print(f"找事件1_開始 1")
                for i in range(0, 5, 1):
                    find_monter_attack()

            # 找事件1_開始 2
            find_x, find_y, find_flag = script.find_image_pattern(find_pattern=find_img.get('任務').get('事件1_開始'), threshold_value=0.8, mask=((600, 0, 800, 600),), show_img=True, add_return_xy=True)
            if find_flag == True:
                script.bgcontrol.bg_left_mouse_click((find_x + 10, find_y + 60), 0.1)
                print(f"找事件1_開始 2")
                for i in range(0, 5, 1):
                    find_monter_attack()

            # 找事件1_完成
            find_x, find_y, find_flag = script.find_image_pattern(find_pattern=find_img.get('任務').get('事件1_完成'), threshold_value=0.8, mask=((600, 0, 800, 600),), show_img=True, add_return_xy=True)
            if find_flag == True:
                script.bgcontrol.bg_left_mouse_click((find_x, find_y + 30), 0.1)
                print(f"找事件1_完成")
                for i in range(0, 5, 1):
                    find_monter_attack()

            # 找事件2_完成
            find_x, find_y, find_flag = script.find_image_pattern(find_pattern=find_img.get('任務').get('事件2_完成'), threshold_value=0.8, mask=((600, 0, 800, 600),), show_img=True, add_return_xy=True)
            if find_flag == True:
                script.bgcontrol.bg_left_mouse_click((find_x + 10, find_y + 60), 0.1)
                print(f"找事件2_完成")
                for i in range(0, 5, 1):
                    find_monter_attack()





            # 找物品
            print(f"開始找物品")
            find_flag_item_loop = 1
            find_item_loop_cnt = 10
            death_cnt = 5
            while find_flag_item_loop and lose_flag == False:
                if script.find_image_pattern(find_pattern=find_img.get('系統').get('死亡'), threshold_value=0.8, show_img=True, add_return_xy=False) == True:
                    time.sleep(6)
                    while script.find_image_pattern(find_pattern=find_img.get('系統').get('復活'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                        time.sleep(1)
                    find_x, find_y, find_flag = script.find_image_pattern(find_pattern=find_img.get('系統').get('復活'),threshold_value=0.8, show_img=True)
                    script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)

                    death_cnt = death_cnt - 1
                    if death_cnt == 0:
                        break

                    script.bgcontrol.bg_left_mouse_click((61, 334), 0.1)
                    time.sleep(1)
                    script.bgcontrol.bg_left_mouse_click((162, 144), 0.1)
                    time.sleep(1)
                    script.bgcontrol.bg_left_mouse_click((188, 168), 0.1)
                    time.sleep(1)

                    # 找怪打
                    find_monter_attack()

                # 判斷圖
                # find_x, find_y, find_flag = script.find_image_pattern(find_pattern=find_img.get('物品'), threshold_value=0.8, show_img=True)
                # if find_flag == True:
                #     find_item_loop_cnt = 20
                #     script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)
                #     time.sleep(0.5)

                # name[0] = {
                # 0: 'enemy',
                # 1: 'friend',
                # 2: 'yellow_item',
                # 3: 'blue_item',
                # 4: 'chest',
                # 5: 'healing_potion',
                # 6: 'waypoint',
                # 7: 'gold',
                # 8: 'althar',
                # 9: 'uniq_item'}

                screenshot_img = script.screen_capture()
                screenshot_img_RGB = cv2.cvtColor(screenshot_img, cv2.COLOR_BGR2RGB)
                results = model(source=screenshot_img_RGB, device=0, classes=[2, 3, 4, 5, 7, 9], conf=0.6, verbose=False)

                if len(results[0].boxes) != 0:

                    res_plotted = results[0].plot()
                    res_plotted_RGB = cv2.cvtColor(res_plotted, cv2.COLOR_RGB2BGR)
                    script.show_screenshot(res_plotted_RGB)
                    test_cnt = 0
                    boxes = results[0].boxes
                    for box in boxes:
                        test_cnt = test_cnt + 1
                    find_flag1 = 1
                    detect_pos_x1 = int(results[0].boxes[0].xywh[0][0])
                    detect_pos_y1 = int(results[0].boxes[0].xywh[0][1])
                    script.bgcontrol.bg_left_mouse_click((detect_pos_x1, detect_pos_y1), 0.1, distance_time_cal=True)
                    find_item_loop_cnt = 10

                find_x, find_y, find_flag = script.find_image_pattern(find_pattern=find_img.get('物品'), threshold_value=0.8, show_img=True)
                if find_flag == True:
                    find_item_loop_cnt = 10
                    script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1, distance_time_cal=True)

                find_item_loop_cnt = find_item_loop_cnt - 1
                script.bgcontrol.bg_left_mouse_click((400 + random.randint(-100, 100), 300 + random.randint(-100, 100)), 0.1)
                if find_item_loop_cnt == 0:
                   find_flag_item_loop = 0

            print(f"reset game")

            if script.script_start_flag == True:
                time.sleep(0.5)
                while script.find_image_pattern(find_pattern=find_img.get('系統').get('隱士居所'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                    print("還沒回到隱士居所 Q2")
                    time.sleep(1)
                    # 按下ESC
                    script.bgcontrol.bg_hwmd_activate()
                    time.sleep(0.1)
                    script.bgcontrol.bg_key_press(win32con.VK_ESCAPE, 0.5)
                    time.sleep(0.1)
                    print(f"1")

                # 按下E
                script.bgcontrol.bg_key_press(ord('E'), 0.5)

                while script.find_image_pattern(find_pattern=find_img.get('系統').get('離開地城'), threshold_value=0.6, show_img=True, add_return_xy=False) != True:
                    time.sleep(1)
                    print(f"2")
                    if script.find_image_pattern(find_pattern=find_img.get('系統').get('死亡'), threshold_value=0.8, show_img=True, add_return_xy=False) == True:
                        time.sleep(6)
                        while script.find_image_pattern(find_pattern=find_img.get('系統').get('復活'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                            time.sleep(1)
                        find_x, find_y, find_flag = script.find_image_pattern(
                            find_pattern=find_img.get('系統').get('復活'), threshold_value=0.8, show_img=True)
                        script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)
                        time.sleep(2)

                        # 按下E
                        script.bgcontrol.bg_key_press(ord('E'), 0.5)

                # 找到'離開地城' 並按下
                find_x, find_y, find_flag = script.find_image_pattern(find_pattern=find_img.get('系統').get('離開地城'),
                                                                      threshold_value=0.6, show_img=True)
                script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)

                # 等待6秒傳送
                time.sleep(6)

                # 檢查是否回到美德角
                break_flag = 0
                start_time = time.time()
                print(f"start_time: {start_time}")
                while script.find_image_pattern(find_pattern=find_img.get('系統').get('美德角'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                    end_time = time.time()
                    print(f"end_time: {end_time}")
                    total_time = end_time - start_time
                    print(f"start_time - end_time: {total_time}")
                    if total_time >= 60.0:
                        time.sleep(1)
                        # 按下E
                        script.bgcontrol.bg_key_press(ord('E'), 0.5)

                        while script.find_image_pattern(find_pattern=find_img.get('系統').get('離開地城'), threshold_value=0.6, show_img=True, add_return_xy=False) != True:
                            time.sleep(1)
                            if script.find_image_pattern(find_pattern=find_img.get('系統').get('美德角'), threshold_value=0.8, show_img=True, add_return_xy=False) == True:
                                break_flag = 1
                                break
                            print(f"3")

                        if break_flag == 1:
                            break

                        # 找到'離開地城' 並按下
                        find_x, find_y, find_flag = script.find_image_pattern(
                            find_pattern=find_img.get('系統').get('離開地城'), threshold_value=0.6, show_img=True)
                        script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)

                        # 等待6秒傳送
                        time.sleep(6)
                        print(f"break 1")
                        break_flag = 1
                        break


                    time.sleep(0.1)
                    # 檢查是否死亡
                    if script.find_image_pattern(find_pattern=find_img.get('系統').get('死亡'), threshold_value=0.8, show_img=True, add_return_xy=False) == True:
                        time.sleep(6)
                        while script.find_image_pattern(find_pattern=find_img.get('系統').get('復活'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                            time.sleep(1)
                        find_x, find_y, find_flag = script.find_image_pattern(
                            find_pattern=find_img.get('系統').get('復活'), threshold_value=0.8, show_img=True)
                        script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)
                        time.sleep(2)

                        # 按下E
                        script.bgcontrol.bg_key_press(ord('E'), 0.5)

                        while script.find_image_pattern(find_pattern=find_img.get('系統').get('離開地城'), threshold_value=0.6, show_img=True, add_return_xy=False) != True:
                            time.sleep(1)
                            print(f"4")
                            if script.find_image_pattern(find_pattern=find_img.get('系統').get('美德角'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                                time.sleep(1)
                                break_flag = 1
                                print(f"break 2")
                                break

                        # 找到'離開地城' 並按下
                        if break_flag == 0:
                            find_x, find_y, find_flag = script.find_image_pattern(find_pattern=find_img.get('系統').get('離開地城'), threshold_value=0.6, show_img=True)
                            script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)

                            # 等待6秒傳送
                            time.sleep(6)

                        if break_flag == 1:
                            print(f"break 3")
                            break

                    if break_flag == 1:
                        print(f"break 4")
                        break

                while script.find_image_pattern(find_pattern=find_img.get('系統').get('美德角'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                    time.sleep(0.5)
                    # 檢查是否死亡
                    print(f"Q1")
                    if break_flag == 1 and script.find_image_pattern(find_pattern=find_img.get('系統').get('離開地城'), threshold_value=0.5, show_img=True, add_return_xy=False) == True:
                        find_x, find_y, find_flag = script.find_image_pattern(
                            find_pattern=find_img.get('系統').get('離開地城'), threshold_value=0.6, show_img=True)
                        script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)

                        # 等待6秒傳送
                        time.sleep(6)


                    if script.find_image_pattern(find_pattern=find_img.get('系統').get('死亡'), threshold_value=0.8, show_img=True, add_return_xy=False) == True:
                        time.sleep(6)
                        while script.find_image_pattern(find_pattern=find_img.get('系統').get('復活'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                            time.sleep(1)
                        find_x, find_y, find_flag = script.find_image_pattern(
                            find_pattern=find_img.get('系統').get('復活'), threshold_value=0.8, show_img=True)
                        script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)
                        time.sleep(2)

                        # 按下E
                        script.bgcontrol.bg_key_press(ord('E'), 0.5)
                        time.sleep(1)
                        print("找不到??")
                        while script.find_image_pattern(find_pattern=find_img.get('系統').get('離開地城'), threshold_value=0.5, show_img=True, add_return_xy=False) != True:
                            time.sleep(1)
                            print(f"4")
                            if script.find_image_pattern(find_pattern=find_img.get('系統').get('美德角'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                                time.sleep(1)
                                break_flag = 1
                                print(f"break 2")
                                break

                        print(f"Q2")
                        # 找到'離開地城' 並按下
                        if break_flag == 0:
                            find_x, find_y, find_flag = script.find_image_pattern(find_pattern=find_img.get('系統').get('離開地城'), threshold_value=0.6, show_img=True)
                            script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)

                            # 等待6秒傳送
                            time.sleep(6)

                            print(f"死掉離開地下城")
                            break

                print(f"準備離開遊戲")
                # 按下ESC
                script.bgcontrol.bg_hwmd_activate()
                time.sleep(0.1)
                script.bgcontrol.bg_key_press(win32con.VK_ESCAPE, 0.5)
                time.sleep(0.1)

                # 檢查是出現ESC_離開遊戲
                while script.find_image_pattern(find_pattern=find_img.get('系統').get('ESC_離開遊戲'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                    time.sleep(0.5)

                find_x, find_y, find_flag = script.find_image_pattern(find_pattern=find_img.get('系統').get('ESC_離開遊戲'), threshold_value=0.8, show_img=True)
                script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)

                time.sleep(20)

                # 檢查是出現開始遊戲
                while script.find_image_pattern(find_pattern=find_img.get('系統').get('開始遊戲'), threshold_value=0.9, show_img=True, add_return_xy=False) != True:
                    time.sleep(1)

                find_x, find_y, find_flag = script.find_image_pattern(find_pattern=find_img.get('系統').get('開始遊戲'), threshold_value=0.7, show_img=True)
                script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)

                # 檢查是否回到美德角
                while script.find_image_pattern(find_pattern=find_img.get('系統').get('美德角'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                    time.sleep(2)
                    # 檢查是否死亡
                    if script.find_image_pattern(find_pattern=find_img.get('系統').get('死亡'), threshold_value=0.8, show_img=True, add_return_xy=False) == True:
                        time.sleep(6)
                        # 按下ESC
                        script.bgcontrol.bg_hwmd_activate()
                        time.sleep(0.1)
                        script.bgcontrol.bg_key_press(win32con.VK_ESCAPE, 0.5)
                        time.sleep(0.1)

                        # 檢查是出現ESC_離開遊戲
                        while script.find_image_pattern(find_pattern=find_img.get('系統').get('ESC_離開遊戲'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                            time.sleep(1)

                        find_x, find_y, find_flag = script.find_image_pattern(
                            find_pattern=find_img.get('系統').get('ESC_離開遊戲'), threshold_value=0.8, show_img=True)
                        script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)

                        time.sleep(15)

                        # 檢查是出現開始遊戲
                        while script.find_image_pattern(find_pattern=find_img.get('系統').get('開始遊戲'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                            time.sleep(1)

                        find_x, find_y, find_flag = script.find_image_pattern(find_pattern=find_img.get('系統').get('開始遊戲'), threshold_value=0.8, show_img=True)
                        script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)

                script.bgcontrol.bg_left_mouse_click((310, 200), 0.1)


                while script.find_image_pattern(find_pattern=find_img.get('系統').get('隱士居所'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                    print("還沒回到隱士居所 Q3")
                    time.sleep(1)
                    # 檢查是否死亡
                    if script.find_image_pattern(find_pattern=find_img.get('系統').get('死亡'), threshold_value=0.8, show_img=True, add_return_xy=False) == True:
                        time.sleep(6)
                        # 按下ESC
                        script.bgcontrol.bg_hwmd_activate()
                        time.sleep(0.1)
                        script.bgcontrol.bg_key_press(win32con.VK_ESCAPE, 0.5)
                        time.sleep(0.1)

                        # 檢查是出現ESC_離開遊戲
                        while script.find_image_pattern(find_pattern=find_img.get('系統').get('ESC_離開遊戲'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                            time.sleep(1)

                        find_x, find_y, find_flag = script.find_image_pattern(
                            find_pattern=find_img.get('系統').get('ESC_離開遊戲'), threshold_value=0.8, show_img=True)
                        script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)

                        time.sleep(15)

                        # 檢查是出現開始遊戲
                        while script.find_image_pattern(find_pattern=find_img.get('系統').get('開始遊戲'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                            time.sleep(1)

                        find_x, find_y, find_flag = script.find_image_pattern(
                            find_pattern=find_img.get('系統').get('開始遊戲'), threshold_value=0.8, show_img=True)
                        script.bgcontrol.bg_left_mouse_click((find_x, find_y), 0.1)

                        # 檢查是否回到美德角
                        while script.find_image_pattern(find_pattern=find_img.get('系統').get('美德角'), threshold_value=0.8, show_img=True, add_return_xy=False) != True:
                            time.sleep(1)

                        script.bgcontrol.bg_left_mouse_click((310, 200), 0.1)

            # script.show_screenshot(script.screen_capture(save=False))

            # mask = ((0, 0, 400, 300), (400, 300, 800, 600))
            # qq1, qq2, qq3 = script.find_image_pattern(find_pattern=find_img.get('系統'), threshold_value=0.8, show_img=True)
            # print(f"qq1, qq2, qq3 : {qq1}, {qq2}, {qq3}")
        # 開始測量
        # start = time.time()
        #
        #
        # # 結束測量
        # end = time.time()
        #
        # # 輸出結果
        # print("執行時間：%f 豪秒" % ((end - start)*1000))




