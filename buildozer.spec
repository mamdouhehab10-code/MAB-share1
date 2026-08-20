[app]
title = My Application
package.name = myapp
package.domain = org.test
source.include_exts = py,png,jpg,kv,atlas
requirements = python3,kivy,pillow,plyer,qrcode
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
