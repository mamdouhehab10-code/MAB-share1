[app]

# (str) Title of your application
title = My Application

# (str) Package name
package.name = myapp

# (str) Package domain (needed for android packaging)
package.domain = org.test

# (list) Source files to include (let it empty to include all files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of directory to include (seperated by comma)
source.include_dirs = 

# (list) Application requirements
# حط هنا الحزم اللي تطبيقك محتاجها،python3 و kivy أساسيين
requirements = python3,kivy

# (str) Custom source folders for requirements
#requirements.source.kivy = ../../../kivy

# (list) Permissions
# أضف الصلاحيات اللي تطبيقك محتاجها هنا لو فيه (مثلاً INTERNET)
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android SDK version to use
# android.sdk = 20

# (str) Android NDK version to use
# android.ndk = 25b

# (int) Android NDK version to use. If left empty, it will use the default NDK associated with the p4a release.
android.ndk_api = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Orientation (landscape, portrait, all)
orientation = portrait

# (list) List of services to declare
#android.services = NAME:gsys:maint

#
# Extras
#

# (list) The Android archs to build for,, can be arm6pi-v7a, arm64-v8a, x86, x86_64
# بنبني للنسختين الأكثر انتشاراً عشان نجنب مشاكل التوافق
android.archs = arm64-v8a, armeabi-v7a

# (bool) If True, then skip trying to update the Android SDK
# android.skip_sdk_update = False

# (str) Bootstrap to use for android builds
# p4a.bootstrap = sdl2

[buildozer]

# (int) Log level (0 = error, 1 = info, 2 = debug (with command output))
log_level = 2

# (str) Path to build artifact, relative to the spec file
bin_dir = ./bin

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_root = 1
