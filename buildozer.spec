[app]
title = MAB Share
package.name = mabshare
package.domain = org.mab
source.include_exts = py,png,jpg,kv,atlas
source.include_patterns = assets/**/*, *.kv
requirements = python3,kivy,pillow,plyer,qrcode,flask,werkzeug,arabic_reshaper,python-bidi
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.private_storage = True
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_root = 1
p4a.branch = release-2023.06.14
