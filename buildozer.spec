[app]
title = MAB Share - Moved to APK build
package.name = mabshare
package.domain = org.mabd
source.include_exts = py,png,jpg,kv,atlas
# Include all Python dependencies used by the app (Flask + werkzeug used by the local server)
requirements = python3,kivy,pillow,plyer,qrcode,flask,werkzeug,arabic_reshaper,python-bidi
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.private_storage = True
orientation = portrait
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_root = 1
# دي أهم حتة يا بدر، عشان نرجع لنسخة أقدم وأضمن
p4a.branch = release-2023.06.14
