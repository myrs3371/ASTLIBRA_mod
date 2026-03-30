import os
import sys
import time
import webview
import tkinter as tk 
from frontend.api import Api

if __name__ == "__main__":
    # 设置项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    # 添加项目根目录到sys.path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    api = Api()
    root = tk.Tk()
    # 获取屏幕的宽度和高度
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 1280
    window_height = 800
    x = (screen_width - window_width) // 2 
    y = (screen_height - window_height) // 2
    web_dir = os.path.join(project_root, 'web')
    index_path = os.path.join(web_dir, 'index.html')
    file_url = 'file:///' + index_path.replace('\\', '/')
    window = webview.create_window(
        "ASTLIBRA MOD 工具",
        url=file_url,
        js_api=api,
        width=window_width,
        height=window_height,
        x=x, 
        y=y,
        min_size=(900, 600),
        background_color='#1a1a2e',
    )
    api.set_window(window)
    webview.start(gui='edgechromium')
    
