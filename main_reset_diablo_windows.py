import pygetwindow as gw

def resize_window(window_title, width, height):
    # 获取窗口对象
    window = gw.getWindowsWithTitle(window_title)
    if len(window) > 0:
        window = window[0]
        # 调整窗口大小
        window.resizeTo(width, height)
        # 将窗口移动到屏幕左上角
        window.moveTo(0, 0)

# 示例调用
window_title = "《暗黑破壞神 IV》"  # 替换为你要调整的窗口标题
# window_title = "Diablo IV"  # 替换为你要调整的窗口标题
width = 800
height = 600
resize_window(window_title, width, height)

# # 或者调整为1024x768
# width = 1024
# height = 768
# resize_window(window_title, width, height)


# import win32gui
# import win32ui
# from ctypes import windll
# from PIL import Image

#
# def photo_capture():
#
#     hwnd = win32gui.FindWindow(None, '《暗黑破壞神 IV》')  # 获取窗口的句柄
#     # hwnd = 265204  # 或设置窗口句柄
#
#     # 如果使用高 DPI 显示器（或 > 100% 缩放尺寸），添加下面一行，否则注释掉
#     windll.user32.SetProcessDPIAware()
#
#     # Change the line below depending on whether you want the whole window
#     # or just the client area.
#     # 根据您是想要整个窗口还是只需要 client area 来更改下面的行。
#     left, top, right, bot = win32gui.GetClientRect(hwnd)
#     # left, top, right, bot = win32gui.GetWindowRect(hwnd)
#     w = right - left
#     h = bot - top
#
#     hwndDC = win32gui.GetWindowDC(hwnd)  # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
#     mfcDC = win32ui.CreateDCFromHandle(hwndDC)  # 根据窗口的DC获取mfcDC
#     saveDC = mfcDC.CreateCompatibleDC()  # mfcDC创建可兼容的DC
#
#     saveBitMap = win32ui.CreateBitmap()  # 创建bitmap准备保存图片
#     saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)  # 为bitmap开辟空间
#
#     saveDC.SelectObject(saveBitMap)  # 高度saveDC，将截图保存到saveBitmap中
#
#     # 选择合适的 window number，如0，1，2，3，直到截图从黑色变为正常画面
#     result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
#
#     bmpinfo = saveBitMap.GetInfo()
#     bmpstr = saveBitMap.GetBitmapBits(True)
#
#     im = Image.frombuffer(
#         'RGB',
#         (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
#         bmpstr, 'raw', 'BGRX', 0, 1)
#
#     win32gui.DeleteObject(saveBitMap.GetHandle())
#     saveDC.DeleteDC()
#     mfcDC.DeleteDC()
#     win32gui.ReleaseDC(hwnd, hwndDC)
#
#     if result == 1:
#         # PrintWindow Succeeded
#         im.save("test.png")  # 调试时可打开，不保存图片可节省大量时间（约0.2s）
#         return im  # 返回图片
#     else:
#         print("fail")
#
#
# photo_capture()