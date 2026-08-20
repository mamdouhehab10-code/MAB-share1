[app]
title = MAB Share
package.name = mabshare
package.domain = org.mab
source.include_exts = py,png,jpg,kv,atlas
source.dir = . 
version = 1.1
requirements = python3,kivy,flask,werkzeug,qrcode,arabic_reshaper,python-bidi,pillow,plyer,requests,urllib3,idna,charset-normalizer,certifi
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_WIFI_STATE,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 30
android.accept_sdk_license = True
p4s_branch = master

[buildozer]
log_level = 2
warn_on_root = 1
