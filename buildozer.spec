[app]
title = MAB Share
package.name = mabshare
package.domain = org.mab.share
source.dir = .
source.include_exts = py,png,jpg,jpeg,gif,kv
version = 1.0.0

# Requirements - optimized for Android
requirements = python3,kivy==2.3.0,pillow,plyer,qrcode[pil],flask,werkzeug,arabic_reshaper,python-bidi,jnius,pyjnius

# UI Settings
orientation = portrait
fullscreen = 0
fullscreen = 0
icon.filename = %(source.dir)s/data/icon.png
presplash.filename = %(source.dir)s/data/presplash.png

# Android specific
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE
android.features = android.hardware.usb.host
android.api = 33
android.minapi = 21
android.ndk_api = 25
android.private_storage = True
android.archs = arm64-v8a,armeabi-v7a
android.bootstrap = sdl2
android.accept_sdk_license = True
android.gradle_dependencies = androidx.appcompat:appcompat:1.6.1
android.add_src = 

# Permissions (important!)
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

# Network timeout
android.meta_data = com.google.android.gms.version=@integer/google_play_services_version

# Storage access
android.request_permissions = android.permission.READ_EXTERNAL_STORAGE,android.permission.WRITE_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_root = 1
p4a.branch = develop
p4a.bootstrap = sdl2
p4a.hook = patches/patchozer.py
android.skip_update = False
android.skip_update_check = False
