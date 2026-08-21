import os
import sys
import platform
import socket
import threading
import logging
from io import BytesIO
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from flask import (
    Flask,
    render_template_string,
    request,
    send_from_directory,
)
from werkzeug.utils import secure_filename

# ============================================================================
# SECTION 1: Arabic Text Support (دعم النص العربي)
# ============================================================================
try:
    import arabic_reshaper
    from bidi.algorithm import get_display

    def ar(text):
        """تحويل النص العربي إلى الشكل الصحيح"""
        if not text:
            return ""
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except Exception as e:
            logger.warning(f"Arabic text conversion error: {e}")
            return text
except ImportError:
    logger.warning("arabic_reshaper not found - Arabic text may not display correctly")
    def ar(text):
        """Fallback: Return text as-is"""
        return text if text else ""

# ============================================================================
# SECTION 2: QR Code Support (دعم رموز QR)
# ============================================================================
try:
    import qrcode
    HAS_QR = True
    logger.info("QR code support enabled")
except ImportError:
    HAS_QR = False
    logger.warning("qrcode not found - QR codes will not be generated")

# ============================================================================
# SECTION 3: Kivy Imports (استيراد Kivy)
# ============================================================================
try:
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
    logger.info("Kivy loaded successfully")
except ImportError as e:
    logger.error(f"Kivy import error: {e}")
    sys.exit(1)

# ============================================================================
# SECTION 4: Platform Detection (كشف نظام التشغيل)
# ============================================================================
def is_android():
    """Check if running on Android"""
    android_env_vars = ['ANDROID_APP_PATH', 'ANDROID_BOOTLOADER', 'ANDROID_DEVICE']
    return any(var in os.environ for var in android_env_vars) or 'android' in sys.platform.lower()

def is_ios():
    """Check if running on iOS"""
    return sys.platform == 'darwin' and 'IPHONEOS_DEPLOYMENT_TARGET' in os.environ

# ============================================================================
# SECTION 5: Storage Path Detection (كشف مسار التخزين)
# ============================================================================
def get_storage_path():
    """Get appropriate storage path for all platforms"""
    try:
        if is_android():
            logger.info("Android detected - using app private storage")
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                context = activity.getApplicationContext()
                files_dir = context.getFilesDir().toString()
                storage_path = os.path.join(files_dir, "MAB_Share")
                logger.info(f"Android storage path: {storage_path}")
                return storage_path
            except Exception as e:
                logger.error(f"Failed to get Android storage: {e}")
                # Fallback
                return os.path.join(os.path.expanduser("~"), "MAB_Share")
        
        if is_ios():
            logger.info("iOS detected - using app documents")
            import platform as plat
            return os.path.join(os.path.expanduser("~"), "Documents", "MAB_Share")
        
        # Desktop (Windows, macOS, Linux)
        storage = os.path.join(os.path.expanduser("~"), "MAB_Share")
        logger.info(f"Desktop storage path: {storage}")
        return storage
        
    except Exception as e:
        logger.error(f"Storage path detection error: {e}")
        return os.path.join(os.path.expanduser("~"), "MAB_Share")

# ============================================================================
# SECTION 6: Font Detection (كشف الخطوط)
# ============================================================================
def get_system_font():
    """Get system font path that supports Arabic across all platforms"""
    system = platform.system()
    
    # Android
    if is_android():
        logger.info("Using Roboto font for Android")
        return "Roboto"
    
    # Windows
    if system == "Windows":
        windows_fonts = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",  # Alternative format
        ]
        for font_path in windows_fonts:
            if os.path.exists(font_path):
                logger.info(f"Windows font found: {font_path}")
                return font_path
    
    # Linux
    elif system == "Linux":
        linux_fonts = [
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]
        for font_path in linux_fonts:
            if os.path.exists(font_path):
                logger.info(f"Linux font found: {font_path}")
                return font_path
    
    # macOS
    elif system == "Darwin":
        macos_fonts = [
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Noto Sans.ttf",
            "/System/Library/Fonts/SF Compact Display.ttf",
        ]
        for font_path in macos_fonts:
            if os.path.exists(font_path):
                logger.info(f"macOS font found: {font_path}")
                return font_path
    
    logger.warning("No system font found - using Roboto fallback")
    return "Roboto"

FONT_PATH = get_system_font()

# ============================================================================
# SECTION 7: Configuration (الإعدادات)
# ============================================================================
APP_NAME = "⚡ MAB Share"
PORT = 2010
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

# Setup storage directories
STORAGE_PATH = get_storage_path()
BASE_DIR = STORAGE_PATH
SENT_FOLDER = os.path.join(BASE_DIR, "sent")
RECEIVED_FOLDER = os.path.join(BASE_DIR, "received")

try:
    os.makedirs(SENT_FOLDER, exist_ok=True)
    os.makedirs(RECEIVED_FOLDER, exist_ok=True)
    logger.info(f"Storage directories created: {BASE_DIR}")
except Exception as e:
    logger.error(f"Failed to create directories: {e}")

# ============================================================================
# SECTION 8: Cross-Platform Folder Opening (فتح المجلدات)
# ============================================================================
def open_folder_cross_platform(path):
    """Open folder with cross-platform support"""
    try:
        if not os.path.exists(path):
            logger.warning(f"Path does not exist: {path}")
            return
        
        if is_android():
            logger.info("Opening folder on Android via Intent")
            try:
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
                logger.info(f"Opened folder: {path}")
            except Exception as e:
                logger.error(f"Android folder open failed: {e}")
        else:
            system = platform.system()
            if system == "Windows":
                os.startfile(path)
                logger.info(f"Opened folder on Windows: {path}")
            elif system == "Darwin":  # macOS
                os.system(f"open '{path}'")
                logger.info(f"Opened folder on macOS: {path}")
            else:  # Linux
                os.system(f"xdg-open '{path}'")
                logger.info(f"Opened folder on Linux: {path}")
    except Exception as e:
        logger.error(f"Error opening folder: {e}")

# ============================================================================
# SECTION 9: Flask Server Setup (إعداد خادم Flask)
# ============================================================================
flask_app = Flask(__name__)
flask_app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
flask_app.config['UPLOAD_FOLDER'] = RECEIVED_FOLDER

def get_local_ip():
    """Get local IP address with multiple fallback methods"""
    methods = [
        ("8.8.8.8", 80),      # Google DNS
        ("1.1.1.1", 80),      # Cloudflare DNS
        ("10.255.255.255", 1) # Broadcast
    ]
    
    for host, port in methods:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(2)
            s.connect((host, port))
            ip = s.getsockname()[0]
            s.close()
            if ip and ip != "127.0.0.1":
                logger.info(f"Local IP detected: {ip}")
                return ip
        except Exception:
            continue
    
    # Try hostname resolution
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        if ip and ip != "127.0.0.1":
            logger.info(f"Hostname IP detected: {ip}")
            return ip
    except Exception:
        pass
    
    logger.warning("Could not detect local IP - using 127.0.0.1")
    return "127.0.0.1"

LOCAL_IP = get_local_ip()

# ============================================================================
# SECTION 10: HTML Template (قالب HTML)
# ============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>⚡ MAB Share</title>
<style>
* { 
    box-sizing: border-box; 
    -webkit-user-select: none;
    user-select: none;
}

html, body { 
    margin: 0; 
    padding: 0; 
    height: 100%;
    width: 100%;
}

body { 
    padding: 12px; 
    background: linear-gradient(135deg, #0f172a 0%, #1a1f3a 100%);
    color: #f8fafc; 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
}

.container { 
    max-width: 650px; 
    margin: 0 auto; 
    background: rgba(30, 41, 59, 0.95);
    padding: 16px; 
    border-radius: 16px; 
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    backdrop-filter: blur(10px);
}

h1 { 
    text-align: center; 
    color: #38bdf8; 
    margin: 0 0 8px 0; 
    font-size: 2.2em;
    font-weight: 800;
}

.subtitle { 
    text-align: center; 
    color: #cbd5e1; 
    margin-bottom: 16px; 
    font-size: 13px;
    font-weight: 500;
}

.card { 
    background: rgba(51, 65, 85, 0.7);
    padding: 16px; 
    border-radius: 12px; 
    margin-bottom: 16px; 
    border-left: 4px solid #38bdf8;
    backdrop-filter: blur(5px);
}

.card h3 { 
    margin: 0 0 12px 0; 
    color: #e0f2fe;
    font-size: 16px;
    font-weight: 600;
}

input[type=file] { 
    width: 100%; 
    margin: 12px 0; 
    color: #cbd5e1; 
    padding: 10px;
    border: 1px solid #475569;
    border-radius: 8px;
    background: rgba(15, 23, 42, 0.5);
}

input[type=file]::-webkit-file-upload-button {
    background: #0284c7;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: bold;
}

.btn { 
    display: inline-block; 
    background: linear-gradient(135deg, #0284c7, #0369a1);
    color: white; 
    border: none; 
    padding: 12px 16px; 
    border-radius: 10px; 
    cursor: pointer; 
    text-decoration: none; 
    font-weight: 600; 
    width: 100%; 
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    font-size: 14px;
    box-shadow: 0 4px 12px rgba(2, 132, 199, 0.2);
}

.btn:active { 
    background: linear-gradient(135deg, #0369a1, #0284c7);
    transform: scale(0.98);
    box-shadow: 0 2px 8px rgba(2, 132, 199, 0.4);
}

.refresh { 
    background: linear-gradient(135deg, #475569, #64748b);
    box-shadow: 0 4px 12px rgba(71, 85, 105, 0.2);
}

.refresh:active { 
    background: linear-gradient(135deg, #64748b, #475569);
}

.section-title { 
    color: #38bdf8; 
    border-bottom: 2px solid #1e293b; 
    padding-bottom: 12px; 
    margin: 20px 0 12px 0; 
    font-size: 16px; 
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

ul { 
    list-style: none; 
    padding: 0; 
    margin: 0; 
}

li { 
    background: rgba(51, 65, 85, 0.6);
    margin-bottom: 10px; 
    padding: 12px; 
    border-radius: 10px; 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    word-break: break-word;
    transition: all 0.2s ease;
    border: 1px solid rgba(71, 85, 105, 0.3);
}

li:active { 
    background: rgba(71, 85, 105, 0.8);
    transform: translateX(-2px);
}

.filename { 
    flex: 1; 
    margin-right: 12px; 
    color: #e0f2fe;
    font-size: 13px;
    word-wrap: break-word;
}

.download { 
    background: linear-gradient(135deg, #22c55e, #16a34a);
    color: white; 
    text-decoration: none; 
    padding: 8px 12px; 
    border-radius: 8px; 
    font-size: 11px; 
    font-weight: 600; 
    white-space: nowrap;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(34, 197, 94, 0.2);
    border: none;
}

.download:active { 
    background: linear-gradient(135deg, #16a34a, #15803d);
    transform: scale(0.95);
}

.empty { 
    color: #94a3b8; 
    text-align: center; 
    font-size: 13px;
    padding: 20px;
}

@media (max-width: 480px) {
    body { padding: 8px; }
    .container { padding: 12px; }
    h1 { font-size: 1.8em; }
    .btn { padding: 10px 12px; font-size: 13px; }
}
</style>
</head>
<body>
<div class="container">
    <h1>⚡ MAB Share</h1>
    <div class="subtitle">مشاركة الملفات عبر الشبكة المحلية</div>
    <button onclick="location.reload()" class="btn refresh">🔄 تحديث</button>
    
    <div class="card">
        <h3>📤 إرسال ملف</h3>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required accept="*/*">
            <button type="submit" class="btn">رفع 📤</button>
        </form>
    </div>
    
    <h3 class="section-title">📤 المرسلة</h3>
    <ul>
    {% for file in sent_files %}
        <li>
            <span class="filename">{{ file[:45] }}{% if file|length > 45 %}...{% endif %}</span>
            <a class="download" href="/download/sent/{{ file|urlencode }}" download>📥</a>
        </li>
    {% else %}
        <li class="empty">لا توجد ملفات</li>
    {% endfor %}
    </ul>
    
    <h3 class="section-title">📥 المستلمة</h3>
    <ul>
    {% for file in received_files %}
        <li>
            <span class="filename">{{ file[:45] }}{% if file|length > 45 %}...{% endif %}</span>
            <a class="download" href="/download/received/{{ file|urlencode }}" download>📥</a>
        </li>
    {% else %}
        <li class="empty">لا توجد ملفات</li>
    {% endfor %}
    </ul>
</div>
</body>
</html>
"""

# ============================================================================
# SECTION 11: Flask Routes (مسارات Flask)
# ============================================================================
def get_sorted_files(folder):
    """Get sorted list of files from folder"""
    try:
        if not os.path.exists(folder):
            return []
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and not f.startswith('.')]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
        return files
    except Exception as e:
        logger.error(f"Error listing files in {folder}: {e}")
        return []

@flask_app.route("/", methods=["GET"])
def index():
    try:
        sent = get_sorted_files(SENT_FOLDER)
        received = get_sorted_files(RECEIVED_FOLDER)
        return render_template_string(HTML_TEMPLATE, sent_files=sent, received_files=received)
    except Exception as e:
        logger.error(f"Index route error: {e}")
        return "Server error", 500

@flask_app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            logger.warning("Upload request without file field")
            return "No file part", 400
        
        file = request.files["file"]
        if not file or not file.filename:
            logger.warning("Upload request with empty filename")
            return "No selected file", 400
        
        filename = secure_filename(file.filename)
        if not filename:
            logger.warning(f"Invalid filename after sanitization: {file.filename}")
            return "Invalid filename", 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File too large: {file_size} bytes")
            return f"File too large (max {MAX_FILE_SIZE/1024/1024}MB)", 413
        
        filepath = os.path.join(RECEIVED_FOLDER, filename)
        file.save(filepath)
        logger.info(f"File uploaded: {filename} ({file_size} bytes)")
        
        return '<script>window.location.href="/";</script>'
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return f"Upload error: {str(e)}", 500

@flask_app.route("/download/<folder_type>/<filename>")
def download_file(folder_type, filename):
    try:
        filename = secure_filename(filename)
        folder = SENT_FOLDER if folder_type == "sent" else RECEIVED_FOLDER
        
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            logger.warning(f"Download file not found: {filepath}")
            return "File not found", 404
        
        logger.info(f"Downloading: {filename}")
        return send_from_directory(folder, filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Download error: {e}")
        return f"Download error: {str(e)}", 500

@flask_app.errorhandler(404)
def not_found(error):
    return render_template_string(HTML_TEMPLATE, sent_files=[], received_files=[])

# ============================================================================
# SECTION 12: Server Setup (إعداد الخادم)
# ============================================================================
def run_server():
    """Run Flask server"""
    try:
        logger.info(f"Starting Flask server on {LOCAL_IP}:{PORT}")
        flask_app.run(
            host="0.0.0.0",
            port=PORT,
            debug=False,
            use_reloader=False,
            threaded=True,
            ssl_context=None
        )
    except Exception as e:
        logger.error(f"Server error: {e}")

# ============================================================================
# SECTION 13: QR Code Generation (توليد رموز QR)
# ============================================================================
def generate_qr_texture(data):
    """Generate QR code texture for Kivy"""
    if not HAS_QR:
        logger.warning("QR generation skipped - qrcode not available")
        return None
    try:
        qr = qrcode.QRCode(version=1, box_size=4, border=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        texture = CoreImage(buffer, ext="png").texture
        logger.info(f"QR code generated for: {data}")
        return texture
    except Exception as e:
        logger.error(f"QR generation error: {e}")
        return None

# ============================================================================
# SECTION 14: Kivy UI (واجهة Kivy)
# ============================================================================
class ResponsiveContent(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(10), padding=dp(12), **kwargs)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        self.server_running = False
        
        logger.info("Building Kivy UI...")

        # Header Section
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
        self.btn_wifi = Button(text=ar("📱 Wi-Fi"), font_name=FONT_PATH, font_size=dp(12), background_color=(0.15, 0.45, 0.75, 1))
        self.btn_hotspot = Button(text=ar("📡 Hotspot"), font_name=FONT_PATH, font_size=dp(12), background_color=(0.2, 0.25, 0.35, 1))
        mode_box.add_widget(self.btn_wifi)
        mode_box.add_widget(self.btn_hotspot)
        self.add_widget(mode_box)

        # Action buttons
        actions = BoxLayout(orientation="horizontal", spacing=dp(6), size_hint_y=None, height=dp(40))
        btn_select = Button(text=ar("📂 ملف"), font_name=FONT_PATH, font_size=dp(12), bold=True, background_normal="", background_color=(0.1, 0.55, 0.9, 1))
        btn_open = Button(text=ar("📁 مجلد"), font_name=FONT_PATH, font_size=dp(12), background_normal="", background_color=(0.15, 0.25, 0.38, 1))
        btn_ref = Button(text=ar("🔄 تحديث"), font_name=FONT_PATH, font_size=dp(12), size_hint_x=0.7, background_normal="", background_color=(0.15, 0.45, 0.85, 1))

        btn_select.bind(on_press=self.select_file)
        btn_open.bind(on_press=self.open_folder)
        btn_ref.bind(on_press=lambda x: self.refresh())

        actions.add_widget(btn_select)
        actions.add_widget(btn_open)
        actions.add_widget(btn_ref)
        self.add_widget(actions)

        # Tabs for files
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

        # Start services
        self.start_server()
        self.update_qr()
        self.refresh()
        logger.info("Kivy UI initialized successfully")

    def start_server(self):
        if self.server_running:
            return
        logger.info("Starting Flask server thread...")
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
            logger.info("Opening file chooser...")
            filechooser.open_file(on_selection=self.file_selected, filters=[("All files", "*/*")])
        except Exception as e:
            logger.error(f"File chooser error: {e}")
            self.show_msg(ar("خطأ"), str(e))

    def file_selected(self, selection):
        if not selection:
            logger.info("No file selected")
            return
        src = selection[0]
        try:
            fname = secure_filename(os.path.basename(src))
            if fname:
                dst = os.path.join(SENT_FOLDER, fname)
                with open(src, "rb") as s, open(dst, "wb") as d:
                    while chunk := s.read(1024 * 1024):
                        d.write(chunk)
                logger.info(f"File copied: {fname}")
                self.refresh()
                self.show_msg(ar("نجح"), ar("تم تحميل الملف بنجاح"))
        except Exception as e:
            logger.error(f"File selection error: {e}")
            self.show_msg(ar("خطأ"), str(e))

    def open_folder(self, *args):
        logger.info("Opening MAB Share folder...")
        open_folder_cross_platform(BASE_DIR)

    def refresh(self):
        self.refresh_list(self.sent_list, SENT_FOLDER)
        self.refresh_list(self.received_list, RECEIVED_FOLDER)

    def refresh_list(self, container, folder):
        container.clear_widgets()
        files = get_sorted_files(folder)
        if not files:
            lbl = Label(text=ar("لا توجد ملفات"), font_name=FONT_PATH, color=(0.6, 0.7, 0.8, 1), size_hint_y=None, height=dp(35))
            container.add_widget(lbl)
            return

        for filename in files:
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(6))
            display_name = filename[:35] + "..." if len(filename) > 35 else filename
            name = Label(text=display_name, font_name=FONT_PATH, halign="right", valign="middle")
            name.bind(size=lambda o, v: setattr(o, "text_size", v))

            btn_del = Button(text=ar("حذف"), font_name=FONT_PATH, font_size=dp(11), size_hint_x=None, width=dp(65), background_normal="", background_color=(0.85, 0.25, 0.25, 1))
            btn_del.bind(on_press=lambda b, f=filename, fld=folder: self.delete_file(f, fld))

            row.add_widget(name)
            row.add_widget(btn_del)
            container.add_widget(row)

    def delete_file(self, filename, folder):
        try:
            p = os.path.join(folder, filename)
            if os.path.exists(p):
                os.remove(p)
                logger.info(f"File deleted: {filename}")
            self.refresh()
        except Exception as e:
            logger.error(f"Delete error: {e}")
            self.show_msg(ar("خطأ"), str(e))

    def show_msg(self, title, msg):
        c = BoxLayout(orientation="vertical", padding=dp(10))
        c.add_widget(Label(text=msg, font_name=FONT_PATH, size_hint_y=0.8))
        b = Button(text=ar("موافق"), font_name=FONT_PATH, size_hint_y=None, height=dp(38))
        c.add_widget(b)
        p = Popup(title=title, content=c, size_hint=(0.85, 0.4))
        b.bind(on_press=p.dismiss)
        p.open()

# ============================================================================
# SECTION 15: Main App (التطبيق الرئيسي)
# ============================================================================
class MABShareApp(App):
    def build(self):
        self.title = APP_NAME
        Window.clearcolor = (0.1, 0.14, 0.2, 1)
        root_scroll = ScrollView()
        root_scroll.add_widget(ResponsiveContent())
        logger.info("MAB Share app started")
        return root_scroll

# ============================================================================
# SECTION 16: Entry Point (نقطة الدخول)
# ============================================================================
if __name__ == "__main__":
    logger.info("="*60)
    logger.info("MAB Share Application Starting")
    logger.info(f"Platform: {platform.system()}")
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Storage Path: {BASE_DIR}")
    logger.info(f"Connection URL: http://{LOCAL_IP}:{PORT}")
    logger.info("="*60)
    
    try:
        MABShareApp().run()
    except Exception as e:
        logger.critical(f"Application error: {e}", exc_info=True)
        sys.exit(1)
