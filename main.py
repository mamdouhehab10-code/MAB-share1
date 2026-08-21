import os
import sys
import platform
import socket
import threading
from io import BytesIO
from pathlib import Path

from flask import (
    Flask,
    render_template_string,
    request,
    send_from_directory,
)
from werkzeug.utils import secure_filename

# دعم النص العربي
try:
    import arabic_reshaper
    from bidi.algorithm import get_display

    def ar(text):
        if not text:
            return ""
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
except ImportError:
    def ar(text):
        return text

# دعم الـ QR Code
try:
    import qrcode
    HAS_QR = True
except ImportError:
    HAS_QR = False

from kivy.app import App
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.popup import Popup

# =========================================================
# Android Detection and Storage Setup
# =========================================================
def is_android():
    """Check if running on Android"""
    return 'ANDROID_APP_PATH' in os.environ or hasattr(sys, 'argv') and 'android' in sys.argv[0]

def get_storage_path():
    """Get appropriate storage path for Android and other platforms"""
    try:
        if is_android():
            # Android: Use app's private storage
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            context = activity.getApplicationContext()
            files_dir = context.getFilesDir().toString()
            return os.path.join(files_dir, "MAB_Share")
    except Exception:
        pass
    
    # Fallback to home directory for desktop
    return os.path.join(os.path.expanduser("~"), "MAB_Share")

# Get appropriate storage directory
STORAGE_PATH = get_storage_path()
BASE_DIR = STORAGE_PATH
SENT_FOLDER = os.path.join(BASE_DIR, "sent")
RECEIVED_FOLDER = os.path.join(BASE_DIR, "received")

try:
    os.makedirs(SENT_FOLDER, exist_ok=True)
    os.makedirs(RECEIVED_FOLDER, exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create directories: {e}")

APP_NAME = "⚡ MAB Share"
PORT = 2010

# =========================================================
# Cross-platform Font Detection
# =========================================================
def get_system_font():
    """Get system font path that supports Arabic"""
    system = platform.system()
    
    # Android uses Roboto by default
    if is_android():
        return "Roboto"
    
    # Windows font paths
    if system == "Windows":
        windows_fonts = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/tahoma.ttf"
        ]
        for font_path in windows_fonts:
            if os.path.exists(font_path):
                return font_path
    
    # Linux font paths
    elif system == "Linux":
        linux_fonts = [
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
        for font_path in linux_fonts:
            if os.path.exists(font_path):
                return font_path
    
    # macOS font paths
    elif system == "Darwin":
        macos_fonts = [
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Noto Sans.ttf",
        ]
        for font_path in macos_fonts:
            if os.path.exists(font_path):
                return font_path
    
    # Fallback to Kivy's default
    return "Roboto"

FONT_PATH = get_system_font()

# =========================================================
# Cross-platform Folder Opening
# =========================================================
def open_folder_cross_platform(path):
    """Open folder with cross-platform support"""
    try:
        if is_android():
            # Android: Use Intent to open file manager
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            File = autoclass('java.io.File')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            
            intent = Intent()
            intent.setAction(Intent.ACTION_VIEW)
            uri = Uri.fromFile(File(path))
            intent.setData(uri)
            
            activity = PythonActivity.mActivity
            activity.startActivity(intent)
        else:
            system = platform.system()
            if system == "Windows":
                os.startfile(path)
            elif system == "Darwin":  # macOS
                os.system(f"open '{path}'")
            else:  # Linux
                os.system(f"xdg-open '{path}'")
    except Exception as e:
        print(f"Error opening folder: {e}")

# =========================================================
# Flask Server - Android Compatible
# =========================================================
flask_app = Flask(__name__)
flask_app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 500  # 500MB max file

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and ip != "127.0.0.1":
            return ip
    except Exception:
        pass

    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        if ip and ip != "127.0.0.1":
            return ip
    except Exception:
        pass

    return "127.0.0.1"

LOCAL_IP = get_local_ip()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>⚡ MAB Share</title>
<style>
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; height: 100%; }
body { 
    padding: 15px; 
    background: linear-gradient(135deg, #0f172a 0%, #1a1f3a 100%);
    color: #f8fafc; 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    min-height: 100vh;
}
.container { max-width: 600px; margin: 0 auto; background: #1e293b; padding: 20px; border-radius: 14px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
h1 { text-align: center; color: #38bdf8; margin: 0 0 10px 0; font-size: 2.5em; }
.subtitle { text-align: center; color: #94a3b8; margin-bottom: 20px; font-size: 14px; }
.card { background: #334155; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #38bdf8; }
.card h3 { margin-top: 0; color: #e0f2fe; }
input[type=file] { width: 100%; margin: 10px 0; color: #cbd5e1; padding: 8px; }
.btn { 
    display: inline-block; 
    background: linear-gradient(135deg, #0284c7, #0369a1);
    color: white; 
    border: none; 
    padding: 12px 15px; 
    border-radius: 8px; 
    cursor: pointer; 
    text-decoration: none; 
    font-weight: bold; 
    width: 100%; 
    text-align: center;
    transition: all 0.3s ease;
    font-size: 14px;
}
.btn:hover, .btn:active { 
    background: linear-gradient(135deg, #0369a1, #0284c7);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4);
}
.refresh { background: #475569; }
.refresh:hover { background: #64748b; }
.section-title { color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 10px; margin-top: 25px; font-size: 16px; font-weight: bold; }
ul { list-style: none; padding: 0; margin: 0; }
li { 
    background: #334155; 
    margin-bottom: 10px; 
    padding: 12px; 
    border-radius: 8px; 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    word-break: break-all;
    transition: background 0.2s ease;
}
li:hover { background: #475569; }
.filename { flex: 1; margin-right: 10px; color: #e0f2fe; }
.download { 
    background: linear-gradient(135deg, #22c55e, #16a34a);
    color: white; 
    text-decoration: none; 
    padding: 8px 12px; 
    border-radius: 6px; 
    font-size: 12px; 
    font-weight: bold; 
    white-space: nowrap;
    transition: all 0.2s ease;
}
.download:hover { 
    background: linear-gradient(135deg, #16a34a, #15803d);
    transform: scale(1.05);
}
.empty { color: #94a3b8; text-align: center; }
</style>
</head>
<body>
<div class="container">
    <h1>⚡ MAB Share</h1>
    <div class="subtitle">مشاركة الملفات عبر الشبكة المحلية</div>
    <button onclick="location.reload()" class="btn refresh">🔄 تحديث الصفحة</button>
    
    <div class="card">
        <h3>📤 إرسال ملف</h3>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required accept="*/*">
            <button type="submit" class="btn">رفع وإرسال 📤</button>
        </form>
    </div>
    
    <h3 class="section-title">📤 الملفات المرسلة</h3>
    <ul>
    {% for file in sent_files %}
        <li>
            <span class="filename">{{ file }}</span>
            <a class="download" href="/download/sent/{{ file|urlencode }}" download>تحميل 📥</a>
        </li>
    {% else %}
        <li class="empty">لا توجد ملفات</li>
    {% endfor %}
    </ul>
    
    <h3 class="section-title">📥 الملفات المستلمة</h3>
    <ul>
    {% for file in received_files %}
        <li>
            <span class="filename">{{ file }}</span>
            <a class="download" href="/download/received/{{ file|urlencode }}" download>تحميل 📥</a>
        </li>
    {% else %}
        <li class="empty">لا توجد ملفات</li>
    {% endfor %}
    </ul>
</div>
</body>
</html>
"""

def get_sorted_files(folder):
    """Get sorted list of files from folder"""
    try:
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
        return files
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

@flask_app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE, 
        sent_files=get_sorted_files(SENT_FOLDER), 
        received_files=get_sorted_files(RECEIVED_FOLDER)
    )

@flask_app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file part", 400
    
    file = request.files["file"]
    if not file or not file.filename:
        return "No selected file", 400
    
    filename = secure_filename(file.filename)
    if not filename:
        return "Invalid filename", 400
    
    try:
        file.save(os.path.join(RECEIVED_FOLDER, filename))
        return '<script>window.location.href="/";</script>'
    except Exception as e:
        return f"Upload error: {str(e)}", 500

@flask_app.route("/download/<folder_type>/<filename>")
def download_file(folder_type, filename):
    filename = secure_filename(filename)
    folder = SENT_FOLDER if folder_type == "sent" else RECEIVED_FOLDER
    try:
        return send_from_directory(folder, filename, as_attachment=True)
    except Exception as e:
        return f"Download error: {str(e)}", 404

def run_server():
    """Run Flask server"""
    try:
        flask_app.run(
            host="0.0.0.0", 
            port=PORT, 
            debug=False, 
            use_reloader=False, 
            threaded=True,
            ssl_context=None
        )
    except Exception as e:
        print(f"Server error: {e}")

def generate_qr_texture(data):
    """Generate QR code texture"""
    if not HAS_QR:
        return None
    try:
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return CoreImage(buffer, ext="png").texture
    except Exception as e:
        print(f"QR generation error: {e}")
        return None

# =========================================================
# Kivy UI
# =========================================================
class ResponsiveContent(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(10), padding=dp(12), **kwargs)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        self.server_running = False

        # Header
        header = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(100))
        
        info = BoxLayout(orientation="vertical", spacing=dp(2))
        
        title = Label(
            text="⚡ MAB Share",
            font_size=dp(20),
            bold=True,
            color=(0.3, 0.75, 1, 1),
            font_name=FONT_PATH,
            halign="right"
        )
        title.bind(size=lambda o, v: setattr(o, 'text_size', v))

        self.sub = Label(
            text=ar("افتح الرابط من المتصفح:"),
            font_size=dp(11),
            color=(0.7, 0.8, 0.9, 1),
            font_name=FONT_PATH,
            halign="right"
        )
        self.sub.bind(size=lambda o, v: setattr(o, 'text_size', v))

        self.url_label = Label(
            text=f"http://{LOCAL_IP}:{PORT}",
            font_size=dp(14),
            bold=True,
            color=(0.2, 0.65, 0.95, 1),
            font_name=FONT_PATH,
            halign="right"
        )
        self.url_label.bind(size=lambda o, v: setattr(o, 'text_size', v))

        info.add_widget(title)
        info.add_widget(self.sub)
        info.add_widget(self.url_label)

        self.qr_image = Image(size_hint=(None, None), size=(dp(95), dp(95)))
        
        header.add_widget(info)
        header.add_widget(self.qr_image)
        self.add_widget(header)

        # Mode buttons
        mode_box = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(36))
        self.btn_wifi = Button(
            text=ar("📱 Wi-Fi"), 
            font_name=FONT_PATH, 
            font_size=dp(12), 
            background_color=(0.15, 0.45, 0.75, 1)
        )
        self.btn_hotspot = Button(
            text=ar("📡 Hotspot"), 
            font_name=FONT_PATH, 
            font_size=dp(12), 
            background_color=(0.2, 0.25, 0.35, 1)
        )
        
        mode_box.add_widget(self.btn_wifi)
        mode_box.add_widget(self.btn_hotspot)
        self.add_widget(mode_box)

        # Action buttons
        actions = BoxLayout(orientation="horizontal", spacing=dp(6), size_hint_y=None, height=dp(40))
        
        btn_select = Button(
            text=ar("📂 ملف"), 
            font_name=FONT_PATH, 
            font_size=dp(12), 
            bold=True, 
            background_normal="", 
            background_color=(0.1, 0.55, 0.9, 1)
        )
        btn_open = Button(
            text=ar("📁 مجلد"), 
            font_name=FONT_PATH, 
            font_size=dp(12), 
            background_normal="", 
            background_color=(0.15, 0.25, 0.38, 1)
        )
        btn_ref = Button(
            text=ar("🔄 تحديث"), 
            font_name=FONT_PATH, 
            font_size=dp(12), 
            size_hint_x=0.7, 
            background_normal="", 
            background_color=(0.15, 0.45, 0.85, 1)
        )

        btn_select.bind(on_press=self.select_file)
        btn_open.bind(on_press=self.open_folder)
        btn_ref.bind(on_press=lambda x: self.refresh())

        actions.add_widget(btn_select)
        actions.add_widget(btn_open)
        actions.add_widget(btn_ref)
        self.add_widget(actions)

        # Tabs
        self.tabs = TabbedPanel(do_default_tab=False, size_hint_y=None, height=dp(320), tab_width=dp(120))
        self.sent_tab = TabbedPanelItem(text=ar("📤 المرسلة"), font_name=FONT_PATH)
        self.received_tab = TabbedPanelItem(text=ar("📥 المستلمة"), font_name=FONT_PATH)

        self.sent_list = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.sent_list.bind(minimum_height=self.sent_list.setter("height"))
        sent_scroll = ScrollView()
        sent_scroll.add_widget(self.sent_list)
        self.sent_tab.add_widget(sent_scroll)

        self.received_list = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.received_list.bind(minimum_height=self.received_list.setter("height"))
        received_scroll = ScrollView()
        received_scroll.add_widget(self.received_list)
        self.received_tab.add_widget(received_scroll)

        self.tabs.add_widget(self.sent_tab)
        self.tabs.add_widget(self.received_tab)
        self.add_widget(self.tabs)

        self.start_server()
        self.update_qr()
        self.refresh()

    def start_server(self):
        if self.server_running:
            return
        threading.Thread(target=run_server, daemon=True).start()
        self.server_running = True

    def update_qr(self):
        url = f"http://{LOCAL_IP}:{PORT}"
        tex = generate_qr_texture(url)
        if tex:
            self.qr_image.texture = tex

    def select_file(self, *args):
        try:
            from plyer import filechooser
            filechooser.open_file(on_selection=self.file_selected)
        except Exception as e:
            self.show_msg(ar("خطأ"), str(e))

    def file_selected(self, selection):
        if not selection:
            return
        src = selection[0]
        try:
            fname = secure_filename(os.path.basename(src))
            if fname:
                dst = os.path.join(SENT_FOLDER, fname)
                with open(src, "rb") as s, open(dst, "wb") as d:
                    while chunk := s.read(1024 * 1024):
                        d.write(chunk)
                self.refresh()
                self.show_msg(ar("نجح"), ar("تم تحميل الملف بنجاح"))
        except Exception as e:
            self.show_msg(ar("خطأ"), str(e))

    def open_folder(self, *args):
        open_folder_cross_platform(BASE_DIR)

    def refresh(self):
        self.refresh_list(self.sent_list, SENT_FOLDER)
        self.refresh_list(self.received_list, RECEIVED_FOLDER)

    def refresh_list(self, container, folder):
        container.clear_widgets()
        files = get_sorted_files(folder)
        if not files:
            lbl = Label(
                text=ar("لا توجد ملفات"), 
                font_name=FONT_PATH, 
                color=(0.6, 0.7, 0.8, 1), 
                size_hint_y=None, 
                height=dp(35)
            )
            container.add_widget(lbl)
            return

        for filename in files:
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(6))
            name = Label(
                text=filename[:40] + "..." if len(filename) > 40 else filename, 
                font_name=FONT_PATH, 
                halign="right", 
                valign="middle"
            )
            name.bind(size=lambda o, v: setattr(o, "text_size", v))

            btn_del = Button(
                text=ar("حذف"), 
                font_name=FONT_PATH, 
                font_size=dp(11), 
                size_hint_x=None, 
                width=dp(65), 
                background_normal="", 
                background_color=(0.85, 0.25, 0.25, 1)
            )
            btn_del.bind(on_press=lambda b, f=filename, fld=folder: self.delete_file(f, fld))

            row.add_widget(name)
            row.add_widget(btn_del)
            container.add_widget(row)

    def delete_file(self, filename, folder):
        try:
            p = os.path.join(folder, filename)
            if os.path.exists(p):
                os.remove(p)
            self.refresh()
        except Exception as e:
            self.show_msg(ar("خطأ"), str(e))

    def show_msg(self, title, msg):
        c = BoxLayout(orientation="vertical", padding=dp(10))
        c.add_widget(Label(text=msg, font_name=FONT_PATH))
        b = Button(text=ar("موافق"), font_name=FONT_PATH, size_hint_y=None, height=dp(38))
        c.add_widget(b)
        p = Popup(title=title, content=c, size_hint=(0.85, 0.4))
        b.bind(on_press=p.dismiss)
        p.open()

class MABShareApp(App):
    def build(self):
        self.title = APP_NAME
        Window.clearcolor = (0.1, 0.14, 0.2, 1)
        root_scroll = ScrollView()
        root_scroll.add_widget(ResponsiveContent())
        return root_scroll

if __name__ == "__main__":
    MABShareApp().run()
