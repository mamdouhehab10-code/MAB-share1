import os
import socket
import threading
from io import BytesIO

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
from kivy.clock import Clock
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

FONT_PATH = "C:/Windows/Fonts/arial.ttf" if os.path.exists("C:/Windows/Fonts/arial.ttf") else "Roboto"

APP_NAME = "MAB Share - local & Web Transfer"
PORT = 2010

BASE_DIR = os.path.join(os.path.expanduser("~"), "MAB_Share")
SENT_FOLDER = os.path.join(BASE_DIR, "sent")
RECEIVED_FOLDER = os.path.join(BASE_DIR, "received")

os.makedirs(SENT_FOLDER, exist_ok=True)
os.makedirs(RECEIVED_FOLDER, exist_ok=True)

# =========================================================
# Flask Server
# =========================================================
flask_app = Flask(__name__)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
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
<title>MAB Share</title>
<style>
* { box-sizing: border-box; }
body { margin: 0; padding: 15px; background: #0f172a; color: #f8fafc; font-family: system-ui, sans-serif; }
.container { max-width: 600px; margin: auto; background: #1e293b; padding: 20px; border-radius: 14px; }
h1 { text-align: center; color: #38bdf8; margin-top: 0; }
.subtitle { text-align: center; color: #94a3b8; margin-bottom: 20px; font-size: 14px; }
.card { background: #334155; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
input[type=file] { width: 100%; margin: 10px 0; color: #cbd5e1; }
.btn { display: inline-block; background: #0284c7; color: white; border: none; padding: 10px 15px; border-radius: 8px; cursor: pointer; text-decoration: none; font-weight: bold; width: 100%; text-align: center; }
.refresh { background: #475569; margin-bottom: 15px; }
.section-title { color: #38bdf8; border-bottom: 1px solid #334155; padding-bottom: 5px; margin-top: 20px; font-size: 16px; }
ul { list-style: none; padding: 0; margin: 0; }
li { background: #334155; margin-bottom: 8px; padding: 10px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; word-break: break-all; }
.download { background: #22c55e; color: white; text-decoration: none; padding: 5px 10px; border-radius: 6px; font-size: 13px; font-weight: bold; white-space: nowrap; margin-right: 10px; }
</style>
</head>
<body>
<div class="container">
    <h1>⚡ MAB Share</h1>
    <div class="subtitle">مشاركة الملفات عبر الشبكة المحلية</div>
    <button onclick="location.reload()" class="btn refresh">🔄 تحديث الصفحة</button>
    <div class="card">
        <h3 style="margin-top:0;">📤 إرسال ملف</h3>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <button type="submit" class="btn">رفع وإرسال 📤</button>
        </form>
    </div>
    <h3 class="section-title">📤 الملفات المرسلة</h3>
    <ul>
    {% for file in sent_files %}
        <li><span>{{ file }}</span><a class="download" href="/download/sent/{{ file|urlencode }}" download>تحميل 📥</a></li>
    {% else %}
        <li>لا توجد ملفات</li>
    {% endfor %}
    </ul>
    <h3 class="section-title">📥 الملفات المستلمة</h3>
    <ul>
    {% for file in received_files %}
        <li><span>{{ file }}</span><a class="download" href="/download/received/{{ file|urlencode }}" download>تحميل 📥</a></li>
    {% else %}
        <li>لا توجد ملفات</li>
    {% endfor %}
    </ul>
</div>
</body>
</html>
"""

def get_sorted_files(folder):
    try:
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
        return files
    except Exception:
        return []

@flask_app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, sent_files=get_sorted_files(SENT_FOLDER), received_files=get_sorted_files(RECEIVED_FOLDER))

@flask_app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file", 400
    file = request.files["file"]
    if not file.filename:
        return "No filename", 400
    filename = secure_filename(file.filename)
    if not filename:
        return "Invalid filename", 400
    file.save(os.path.join(RECEIVED_FOLDER, filename))
    return '<script>window.location.href="/";</script>'

@flask_app.route("/download/<folder_type>/<filename>")
def download_file(folder_type, filename):
    filename = secure_filename(filename)
    folder = SENT_FOLDER if folder_type == "sent" else RECEIVED_FOLDER
    return send_from_directory(folder, filename, as_attachment=True)

def run_server():
    flask_app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False, threaded=True)

def generate_qr_texture(data):
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
    except Exception:
        return None

# =========================================================
# Kivy UI متجاوب للشاشات الصغيرة والهواتف
# =========================================================
class ResponsiveContent(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(10), padding=dp(12), **kwargs)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))

        self.server_running = False

        # --- الهيدر (العنوان + الـ QR) ---
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
            text=ar("افتح الرابط ده من المتصفح في الجهاز الثاني:"),
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

        # --- أزرار تبديل الأوضاع (Wi-Fi / Hotspot) ---
        mode_box = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(36))
        self.btn_wifi = Button(text=ar("📱 وضع Wi-Fi"), font_name=FONT_PATH, font_size=dp(12), background_color=(0.15, 0.45, 0.75, 1))
        self.btn_hotspot = Button(text=ar("📡 وضع Hotspot"), font_name=FONT_PATH, font_size=dp(12), background_color=(0.2, 0.25, 0.35, 1))
        
        mode_box.add_widget(self.btn_wifi)
        mode_box.add_widget(self.btn_hotspot)
        self.add_widget(mode_box)

        # --- أزرار التحكم الثلاثية ---
        actions = BoxLayout(orientation="horizontal", spacing=dp(6), size_hint_y=None, height=dp(40))
        
        btn_select = Button(text=ar("📂 اختيار ملف"), font_name=FONT_PATH, font_size=dp(12), bold=True, background_normal="", background_color=(0.1, 0.55, 0.9, 1))
        btn_open = Button(text=ar("📁 المجلد"), font_name=FONT_PATH, font_size=dp(12), background_normal="", background_color=(0.15, 0.25, 0.38, 1))
        btn_ref = Button(text=ar("🔄 تحديث"), font_name=FONT_PATH, font_size=dp(12), size_hint_x=0.7, background_normal="", background_color=(0.15, 0.45, 0.85, 1))

        btn_select.bind(on_press=self.select_file)
        btn_open.bind(on_press=self.open_folder)
        btn_ref.bind(on_press=lambda x: self.refresh())

        actions.add_widget(btn_select)
        actions.add_widget(btn_open)
        actions.add_widget(btn_ref)
        self.add_widget(actions)

        # --- التبويبات (الملفات المرسلة والمستلمة) ---
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
        except Exception as e:
            self.show_msg(ar("خطأ"), str(e))

    def open_folder(self, *args):
        try:
            os.startfile(BASE_DIR)
        except Exception:
            pass

    def refresh(self):
        self.refresh_list(self.sent_list, SENT_FOLDER)
        self.refresh_list(self.received_list, RECEIVED_FOLDER)

    def refresh_list(self, container, folder):
        container.clear_widgets()
        files = get_sorted_files(folder)
        if not files:
            lbl = Label(text=ar("لا توجد ملفات حالياً"), font_name=FONT_PATH, color=(0.6, 0.7, 0.8, 1), size_hint_y=None, height=dp(35))
            container.add_widget(lbl)
            return

        for filename in files:
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(6))
            name = Label(text=filename, font_name=FONT_PATH, halign="right", valign="middle")
            name.bind(size=lambda o, v: setattr(o, "text_size", v))

            btn_del = Button(text=ar("🗑️ حذف"), font_name=FONT_PATH, font_size=dp(11), size_hint_x=None, width=dp(65), background_normal="", background_color=(0.85, 0.25, 0.25, 1))
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
