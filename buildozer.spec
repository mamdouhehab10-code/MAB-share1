[app]
title = MAB Share
package.name = mabshare
package.domain = org.mab.share

source.dir = .
source.include_exts = py,png,jpg,jpeg,gif

version = 1.0.0

requirements = python3,kivy==2.3.0,pillow,plyer,qrcode,flask,werkzeug,arabic_reshaper,python-bidi,jnius,pyjnius

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk_api = 25
android.private_storage = True
android.archs = arm64-v8a,armeabi-v7a

android.bootstrap = sdl2
android.accept_sdk_license = True

# Gradle settings
android.gradle_dependencies = androidx.appcompat:appcompat:1.3.0

[buildozer]
log_level = 2
warn_root = 1
p4a.branch = develop
