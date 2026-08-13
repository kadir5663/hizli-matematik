[app]
title = Hizli Matematik
package.name = hizlimatematik
package.domain = org.kadir

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,ogg,mp3

version = 1.0
requirements = python3,kivy

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
