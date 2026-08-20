[app]
title = MAB Share
package.name = mabshare
package.domain = org.mab
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.1
requirements = python3,kivy,qrcode,arabic_reshaper,python-bidi,pillow,plyer
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_WIFI_STATE,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 30
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
