"""
python-for-android'daki bozuk 'venv oluştur + pip install -U pip' akışını
'virtualenv' ile değiştirir. GitHub Actions'ın kendi Python 3.11.15
kurulumunda, p4a'nın kendi derlediği hostpython3 içine gömülü pip
tutarsız/bozuk geliyor (ensurepip kaynaklı). virtualenv aracı kendi
bağımsız, güvenilir pip kopyasını kullandığı için bu sorunu atlıyoruz.
"""
path = "p4a-src/pythonforandroid/build.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old1 = "shprint(host_python, '-m', 'venv', 'venv')"
new1 = 'shprint(sh.Command("virtualenv"), "--python", ctx.hostpython, "venv")'

old2 = "source venv/bin/activate && pip install -U pip"
new2 = "source venv/bin/activate && python -m pip install -U pip"

if old1 not in content:
    raise SystemExit("HATA: ilk kalıp (venv oluşturma satırı) bulunamadı!")
if old2 not in content:
    raise SystemExit("HATA: ikinci kalıp (pip install -U pip satırı) bulunamadı!")

content = content.replace(old1, new1)
content = content.replace(old2, new2)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("build.py başarıyla yamalandı.")
