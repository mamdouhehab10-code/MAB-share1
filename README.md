# ⚡ MAB Share - File Transfer Application

**مشاركة الملفات عبر الشبكة المحلية بسهولة وأمان**

Share files wirelessly across your local network with a simple web interface and mobile app.

---

## ✨ Features

- 📱 **Cross-Platform**: Works on Windows, macOS, Linux, and Android
- 🌐 **Web Interface**: Access via browser from any device on your network
- 🔗 **QR Code**: Quick connection with QR code scanning
- 📂 **File Management**: Upload, download, and delete files easily
- 🔐 **Local Network Only**: Files stay on your local network (no cloud)
- 🎨 **Modern UI**: Beautiful dark theme with Arabic support
- ⚡ **Fast Transfer**: Direct peer-to-peer transfer over local network

---

## 🚀 Quick Start

### Desktop (Windows/macOS/Linux)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

Then open your browser and go to `http://YOUR_IP:2010`

### Mobile (Android)

1. **Build APK** (requires buildozer and Java SDK):
```bash
bash build.sh
```

2. **Or Download Pre-built APK**: 
   - Check releases section for latest APK

3. **Install on Android**:
   - Transfer APK to your phone
   - Go to Settings > Security > Enable "Unknown Sources"
   - Tap the APK file to install
   - Open MAB Share app

---

## 📋 Requirements

### Desktop
- Python 3.8+
- Flask
- Kivy (for desktop GUI)
- QRCode
- Arabic text support libraries

### Android
- Android 5.0+ (API 21)
- 100MB free storage

---

## 🔧 Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/mamdouhehab10-code/MAB-share1
cd MAB-share1

# Install Python dependencies
pip install -r requirements.txt

# Run on desktop
python main.py
```

### Build APK

```bash
# Install build tools
pip install buildozer cython

# Make build script executable
chmod +x build.sh

# Build APK
./build.sh

# APK will be created in bin/ folder
```

---

## 📱 How to Use

### Starting the App

**Desktop:**
```bash
python main.py
```

**Android:**
- Open MAB Share from app drawer
- App starts and shows connection URL
- Scan QR code or enter URL in browser

### Connecting

1. **From another device on same network:**
   - Desktop: Open browser → http://[IP_ADDRESS]:2010
   - Mobile: Scan the QR code shown in the app
   - Or manually enter: http://192.168.1.X:2010

2. **Upload files:**
   - Click "📤 إرسال ملف" / "📤 Send File"
   - Select file and upload
   - File appears in "المرسلة" / "Sent" tab

3. **Download files:**
   - Click "📥 تحميل" / "📥 Download" next to file
   - File downloads to device

4. **Delete files:**
   - In app: Tap red "حذف" / "Delete" button
   - Browser: Right-click and delete via app

---

## 📂 File Storage

Files are stored in:

- **Desktop:** `~/MAB_Share/`
  - `sent/` - Files you uploaded
  - `received/` - Files you received

- **Android:** `/data/data/org.mab.share/files/MAB_Share/`
  - `sent/` - Files you sent
  - `received/` - Files you received

---

## 🔗 Network Setup

### How to Find Your IP Address

**Windows:**
```cmd
ipconfig
# Look for "IPv4 Address"
```

**macOS/Linux:**
```bash
ifconfig
# Look for "inet" address
```

**Or in MAB Share App:**
- The URL is displayed at the top of the app
- Scan the QR code for instant connection

---

## 🛠️ Troubleshooting

### App won't start
```bash
# Install missing dependencies
pip install -r requirements.txt

# Run with verbose output
python main.py 2>&1 | tee app.log
```

### Can't connect from another device
- Make sure both devices are on **same Wi-Fi network**
- Check device's IP address (shown in app)
- Disable firewall temporarily to test
- Try using IP address instead of QR code

### File upload fails
- Check if device has enough storage space
- Verify file is not corrupted
- Try uploading smaller file first

### Web interface looks broken
- Clear browser cache (Ctrl+Shift+Delete)
- Try different browser (Chrome, Firefox, etc.)
- Check if port 2010 is available

---

## 📊 Technical Details

- **Backend:** Flask (Python web server)
- **Frontend:** Responsive HTML5
- **Mobile:** Kivy (Python UI framework)
- **Text Support:** Full RTL (Arabic, Persian, Hebrew)
- **Transfer Protocol:** HTTP/REST API
- **Max File Size:** 500MB (configurable)
- **Port:** 2010 (customizable in code)

---

## 🔐 Security Notes

- ⚠️ Only accessible on **local network** (not internet)
- ⚠️ No authentication by default (add if needed)
- ⚠️ Files are saved to device storage
- ✅ No data sent to external servers
- ✅ No tracking or telemetry

---

## 📝 Configuration

Edit `main.py` to customize:

```python
PORT = 2010                    # Change port
FONT_PATH = "path/to/font"    # Change font
MAX_FILE_SIZE = 500 * 1024 * 1024  # Change max size
```

---

## 🐛 Known Issues

- Android: Some devices may need storage permission grant
- Large files: Transfer slows on slow networks
- QR code: Not visible on very small screens

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 👨‍💻 Author

**Mamdouh Ehab** - [@mamdouhehab10-code](https://github.com/mamdouhehab10-code)

---

## 📞 Support

- 📧 Email: mamdouhehab10@gmail.com
- 🐛 Report issues: [GitHub Issues](https://github.com/mamdouhehab10-code/MAB-share1/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/mamdouhehab10-code/MAB-share1/discussions)

---

## 🙏 Acknowledgments

- [Kivy](https://kivy.org/) - Mobile UI framework
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Python-QRCode](https://github.com/lincolnloop/python-qrcode) - QR code generation
- [Buildozer](https://buildozer.readthedocs.io/) - APK builder

---

Made with ❤️ by Mamdouh Ehab
