[app]
title = Hizli Matematik
package.name = hizlimatematik
package.domain = org.kadir

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,ogg,mp3

version = 1.0
requirements = python3==3.11.9,kivy

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.png

android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
