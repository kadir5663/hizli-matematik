"""
Hızlı Matematik - Tam Sürüm

İçerik:
  Ana Menü -> Zorluk Seç -> Oyun -> Oyun Bitti
  + Oyuncu adı, Coin, Mağaza (temalar), Başarımlar,
    İstatistikler/Rekorlar, Günlük Görev, Müzik, Ayarlar

Çalıştırmak için (venv aktifken):
    python main.py
"""

import json
import math
import os
import random
import datetime

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.animation import Animation
from kivy.metrics import sp

# ----------------------------------------------------------------------
# Genel ayarlar
# ----------------------------------------------------------------------

from kivy.utils import platform
if platform not in ("android", "ios"):
    Window.size = (400, 700)

DIFFICULTIES = ["Kolay", "Orta", "Zor", "Deli Modu"]

BASE_POINTS = {"Kolay": 5, "Orta": 10, "Zor": 20, "Deli Modu": 30}
DURATIONS = [30, 60, 90]
COIN_PER_CORRECT = 2
DAILY_TARGET = 20
DAILY_REWARD = 50

LEVEL_THRESHOLDS = [0, 150, 350, 600, 900, 1300]

STARTING_LIVES = 3

JOKER_LABELS = {"dondur": "Süre Dondur", "atla": "Soru Atla", "ipucu": "İpucu"}
JOKER_PRICES = {"dondur": 60, "atla": 40, "ipucu": 50}
JOKER_PACK_SIZE = 3
HINT_MARGIN = {"Kolay": 8, "Orta": 15, "Zor": 40, "Deli Modu": 60}

THEMES = {
    "Klasik": {"bg": (0.07, 0.08, 0.12, 1), "accent": (0.2, 0.7, 0.3, 1), "price": 0},
    "Orman": {"bg": (0.04, 0.14, 0.07, 1), "accent": (0.15, 0.55, 0.25, 1), "price": 100},
    "Gün Batımı": {"bg": (0.18, 0.08, 0.05, 1), "accent": (0.85, 0.45, 0.15, 1), "price": 150},
    "Okyanus": {"bg": (0.03, 0.10, 0.18, 1), "accent": (0.10, 0.55, 0.75, 1), "price": 200},
}

ACHIEVEMENTS = [
    {"id": "ilk_oyun", "title": "İlk Adım", "desc": "İlk oyununu tamamla"},
    {"id": "yuz_dogru", "title": "Yüzler Kulübü", "desc": "Toplamda 100 doğru cevap ver"},
    {"id": "kombo_10", "title": "Kombo Ustası", "desc": "Bir oyunda 10 kombo yap"},
    {"id": "bes_yuz_skor", "title": "Puan Canavarı", "desc": "Tek oyunda 500+ skor yap"},
    {"id": "tum_zorluklar", "title": "Her Şeyi Denedim", "desc": "Tüm zorlukları en az bir kez oyna"},
    {"id": "coin_biriktir", "title": "Cimri", "desc": "500 coin biriktir"},
]


def load_sound(path):
    try:
        return SoundLoader.load(path)
    except Exception:
        return None


# ----------------------------------------------------------------------
# Kalıcı veri (oyuncu adı, coin, rekorlar, istatistikler, başarımlar...)
# ----------------------------------------------------------------------

def data_file_path():
    app = App.get_running_app()
    directory = app.user_data_dir if app else "."
    return os.path.join(directory, "playerdata.json")


def default_data():
    return {
        "name": "Oyuncu",
        "coins": 0,
        "high_scores": {d: 0 for d in DIFFICULTIES},
        "stats": {
            "games_played": 0,
            "total_correct": 0,
            "total_wrong": 0,
            "best_combo_ever": 0,
            "difficulties_played": [],
        },
        "achievements": [],
        "daily": {"date": "", "progress": 0, "completed": False},
        "owned_themes": ["Klasik"],
        "selected_theme": "Klasik",
        "jokers": {"dondur": 2, "atla": 2, "ipucu": 2},
    }


def load_data():
    path = data_file_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = default_data()
            merged.update(data)
            merged["stats"] = {**default_data()["stats"], **data.get("stats", {})}
            merged["daily"] = {**default_data()["daily"], **data.get("daily", {})}
            merged["jokers"] = {**default_data()["jokers"], **data.get("jokers", {})}
            return merged
        except Exception:
            pass
    return default_data()


def save_data(data):
    path = data_file_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


def today_str():
    return datetime.date.today().isoformat()


# ----------------------------------------------------------------------
# Soru üretimi
# ----------------------------------------------------------------------

def pick_percent_question(max_k):
    # Sonuç her zaman tam sayı çıksın diye base, yüzdeye göre uygun katlarda seçilir
    percent = random.choice([10, 20, 25, 50, 75])
    g = math.gcd(percent, 100)
    denom = 100 // g
    k = random.randint(1, max_k)
    base = denom * k
    answer = base * percent // 100
    return f"{base}'in %{percent}'i", answer


def pick_sqrt_question(low, high):
    n = random.randint(low, high)
    return f"√{n * n}", n


def pick_fraction_question(denom_choices, max_k):
    # Aynı paydalı iki kesrin toplamı tam sayı çıkacak şekilde seçilir
    d = random.choice(denom_choices)
    k = random.randint(1, max_k)
    total = k * d
    n1 = random.randint(1, total - 1)
    n2 = total - n1
    return f"{n1}/{d} + {n2}/{d}", k


def generate_question(difficulty):
    if difficulty == "Kolay":
        op = random.choice(["+", "-"])
        if op == "+":
            a, b = random.randint(1, 50), random.randint(1, 50)
            return f"{a} + {b}", a + b
        a = random.randint(1, 50)
        b = random.randint(1, a)
        return f"{a} - {b}", a - b

    if difficulty == "Orta":
        op = random.choice(["+", "-", "×", "yüzde", "karekök"])
        if op == "+":
            a, b = random.randint(10, 99), random.randint(10, 99)
            return f"{a} + {b}", a + b
        if op == "-":
            a = random.randint(10, 99)
            b = random.randint(1, a)
            return f"{a} - {b}", a - b
        if op == "×":
            a, b = random.randint(2, 20), random.randint(2, 12)
            return f"{a} × {b}", a * b
        if op == "yüzde":
            return pick_percent_question(max_k=10)
        return pick_sqrt_question(4, 15)

    if difficulty == "Zor":
        op = random.choice(["+", "-", "×", "yüzde", "kesir", "karekök"])
        if op == "+":
            a, b = random.randint(100, 500), random.randint(100, 500)
            return f"{a} + {b}", a + b
        if op == "-":
            a = random.randint(100, 500)
            b = random.randint(1, a)
            return f"{a} - {b}", a - b
        if op == "×":
            a, b = random.randint(10, 30), random.randint(2, 20)
            return f"{a} × {b}", a * b
        if op == "yüzde":
            return pick_percent_question(max_k=25)
        if op == "kesir":
            return pick_fraction_question([2, 3, 4, 5, 6, 8], max_k=4)
        return pick_sqrt_question(15, 35)

    template = random.choice(["A", "B", "C", "D"])
    if template == "A":
        a, b, c = random.randint(5, 20), random.randint(2, 12), random.randint(1, 50)
        return f"{a} × {b} - {c}", a * b - c
    if template == "B":
        a, b, c = random.randint(2, 40), random.randint(2, 40), random.randint(2, 12)
        return f"({a} + {b}) × {c}", (a + b) * c
    if template == "C":
        b = random.randint(2, 12)
        a = b * random.randint(2, 20)
        c, d = random.randint(2, 15), random.randint(2, 12)
        return f"{a} ÷ {b} + {c} × {d}", (a // b) + (c * d)
    n = random.randint(4, 15)
    a, b = random.randint(2, 12), random.randint(2, 20)
    return f"√{n * n} + {a} × {b}", n + a * b


def combo_multiplier(streak):
    if streak >= 5:
        return 2.0
    if streak >= 3:
        return 1.5
    return 1.0


def speed_bonus(response_time):
    if response_time < 1.0:
        return 20
    if response_time < 3.0:
        return 10
    return 5


def level_for_score(score):
    level = 1
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if score >= threshold:
            level = i + 1
    return level


# ----------------------------------------------------------------------
# Görsel efektler: konfeti, ekran titremesi, uçan puan yazısı
# ----------------------------------------------------------------------

CONFETTI_COLORS = [
    (0.95, 0.3, 0.3, 1), (0.3, 0.8, 0.95, 1), (0.95, 0.85, 0.2, 1),
    (0.4, 0.9, 0.4, 1), (0.8, 0.4, 0.9, 1),
]


class ConfettiParticle(Widget):
    def __init__(self, color, **kwargs):
        super().__init__(**kwargs)
        self.size = (10, 10)
        with self.canvas:
            Color(*color)
            self.ellipse = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *a):
        self.ellipse.pos = self.pos
        self.ellipse.size = self.size


def spawn_confetti(screen, center):
    for _ in range(10):
        particle = ConfettiParticle(color=random.choice(CONFETTI_COLORS))
        particle.pos = (center[0] - 5, center[1] - 5)
        screen.add_widget(particle)
        dx = random.uniform(-90, 90)
        dy = random.uniform(30, 130)
        anim = Animation(
            pos=(particle.x + dx, particle.y + dy), opacity=0,
            duration=0.6, t="out_quad",
        )
        anim.bind(on_complete=lambda *a, w=particle: screen.remove_widget(w))
        anim.start(particle)


def shake_widget(widget):
    orig_x = widget.x
    anim = (
        Animation(x=orig_x - 10, duration=0.04)
        + Animation(x=orig_x + 10, duration=0.04)
        + Animation(x=orig_x - 6, duration=0.04)
        + Animation(x=orig_x + 6, duration=0.04)
        + Animation(x=orig_x, duration=0.04)
    )
    anim.start(widget)


def spawn_flying_text(screen, start_pos, text, color=(1, 0.85, 0.2, 1)):
    label = Label(
        text=text, font_size=sp(18), bold=True, color=color,
        size_hint=(None, None), size=(90, 30),
    )
    label.pos = start_pos
    screen.add_widget(label)
    anim = Animation(y=start_pos[1] + 50, opacity=0, duration=0.7, t="out_quad")
    anim.bind(on_complete=lambda *a: screen.remove_widget(label))
    anim.start(label)


# ----------------------------------------------------------------------
# Ortak: temalı arka planlı ekran taban sınıfı
# ----------------------------------------------------------------------

class ThemedScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.bg_color = Color(0.07, 0.08, 0.12, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._sync_bg, pos=self._sync_bg)

    def _sync_bg(self, *a):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def apply_theme(self, theme_name):
        theme = THEMES.get(theme_name, THEMES["Klasik"])
        self.bg_color.rgba = theme["bg"]


def apply_theme_everywhere(sm, theme_name):
    for screen in sm.screens:
        if isinstance(screen, ThemedScreen):
            screen.apply_theme(theme_name)


# ----------------------------------------------------------------------
# Ana Menü
# ----------------------------------------------------------------------

class MenuScreen(ThemedScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=28, spacing=8)

        top_row = BoxLayout(orientation="horizontal", size_hint=(1, 0.08))
        self.name_btn = Button(text="Oyuncu", font_size=sp(14),
                                background_color=(0.25, 0.25, 0.3, 1))
        self.name_btn.bind(on_release=lambda *a: setattr(self.manager, "current", "name"))
        self.coin_label = Label(text="Coin: 0", font_size=sp(16))
        top_row.add_widget(self.name_btn)
        top_row.add_widget(self.coin_label)
        layout.add_widget(top_row)

        title = Label(text="HIZLI MATEMATİK", font_size=sp(26), bold=True, size_hint=(1, 0.14))
        layout.add_widget(title)

        self.daily_label = Label(text="", font_size=sp(13), size_hint=(1, 0.1), color=(1, 0.85, 0.3, 1))
        layout.add_widget(self.daily_label)

        play_btn = Button(text="OYNA", font_size=sp(20), size_hint=(1, 0.11),
                           background_color=(0.2, 0.7, 0.3, 1))
        play_btn.bind(on_release=lambda *a: setattr(self.manager, "current", "difficulty"))
        layout.add_widget(play_btn)

        def menu_btn(text, target, color):
            b = Button(text=text, font_size=sp(16), size_hint=(1, 0.09), background_color=color)
            b.bind(on_release=lambda *a: setattr(self.manager, "current", target))
            return b

        layout.add_widget(menu_btn("MAGAZA", "shop", (0.55, 0.4, 0.15, 1)))
        layout.add_widget(menu_btn("BASARIMLAR", "achievements", (0.25, 0.45, 0.75, 1)))
        layout.add_widget(menu_btn("ISTATISTIK & REKOR", "stats", (0.35, 0.3, 0.55, 1)))
        layout.add_widget(menu_btn("AYARLAR", "settings", (0.35, 0.35, 0.4, 1)))

        exit_btn = Button(text="ÇIKIŞ", font_size=sp(16), size_hint=(1, 0.09),
                           background_color=(0.6, 0.2, 0.2, 1))
        exit_btn.bind(on_release=lambda *a: App.get_running_app().stop())
        layout.add_widget(exit_btn)

        self.add_widget(layout)

    def on_pre_enter(self, *a):
        app = App.get_running_app()
        self.name_btn.text = app.data["name"]
        self.coin_label.text = f"Coin: {app.data['coins']}"

        daily = app.data["daily"]
        if daily["date"] != today_str():
            daily["date"] = today_str()
            daily["progress"] = 0
            daily["completed"] = False
            save_data(app.data)

        if daily["completed"]:
            self.daily_label.text = f"Gunluk Gorev Tamamlandi! (+{DAILY_REWARD} coin alindi)"
        else:
            self.daily_label.text = f"Gunluk Gorev: {daily['progress']}/{DAILY_TARGET} dogru cevap"


# ----------------------------------------------------------------------
# Oyuncu adı ekranı
# ----------------------------------------------------------------------

class NameScreen(ThemedScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=40, spacing=16)
        layout.add_widget(Label(text="OYUNCU ADI", font_size=sp(24), bold=True, size_hint=(1, 0.2)))

        self.input = TextInput(text="", font_size=sp(22), multiline=False, size_hint=(1, 0.15),
                                halign="center", padding=[10, 20, 10, 10])
        layout.add_widget(self.input)

        save_btn = Button(text="KAYDET", font_size=sp(18), size_hint=(1, 0.13),
                           background_color=(0.2, 0.7, 0.3, 1))
        save_btn.bind(on_release=self.save_name)
        layout.add_widget(save_btn)

        back_btn = Button(text="Geri", font_size=sp(15), size_hint=(1, 0.11),
                           background_color=(0.3, 0.3, 0.3, 1))
        back_btn.bind(on_release=lambda *a: setattr(self.manager, "current", "menu"))
        layout.add_widget(back_btn)
        layout.add_widget(Label(size_hint=(1, 0.3)))

        self.add_widget(layout)

    def on_pre_enter(self, *a):
        app = App.get_running_app()
        self.input.text = app.data["name"]
        self.apply_theme(app.data["selected_theme"])

    def save_name(self, *a):
        app = App.get_running_app()
        new_name = self.input.text.strip()
        if new_name:
            app.data["name"] = new_name
            save_data(app.data)
        self.manager.current = "menu"


# ----------------------------------------------------------------------
# Zorluk Seçimi
# ----------------------------------------------------------------------

class DifficultyScreen(ThemedScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=40, spacing=14)
        layout.add_widget(Label(text="ZORLUK SEÇ", font_size=sp(26), bold=True, size_hint=(1, 0.2)))

        colors = {
            "Kolay": (0.2, 0.7, 0.3, 1),
            "Orta": (0.85, 0.7, 0.1, 1),
            "Zor": (0.8, 0.3, 0.15, 1),
            "Deli Modu": (0.55, 0.15, 0.65, 1),
        }
        for diff in DIFFICULTIES:
            btn = Button(text=diff.upper(), font_size=sp(20), size_hint=(1, 0.15),
                         background_color=colors[diff])
            btn.bind(on_release=lambda inst, d=diff: self.start(d))
            layout.add_widget(btn)

        back_btn = Button(text="Geri", font_size=sp(16), size_hint=(1, 0.12),
                           background_color=(0.3, 0.3, 0.3, 1))
        back_btn.bind(on_release=lambda *a: setattr(self.manager, "current", "menu"))
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def on_pre_enter(self, *a):
        self.apply_theme(App.get_running_app().data["selected_theme"])

    def start(self, difficulty):
        self.manager.current = "game"
        self.manager.get_screen("game").start_game(difficulty)


# ----------------------------------------------------------------------
# Ayarlar
# ----------------------------------------------------------------------

class SettingsScreen(ThemedScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=40, spacing=14)
        self.layout.add_widget(Label(text="AYARLAR", font_size=sp(26), bold=True, size_hint=(1, 0.16)))

        self.duration_label = Label(text="", font_size=sp(17), size_hint=(1, 0.1))
        self.layout.add_widget(self.duration_label)

        duration_row = BoxLayout(orientation="horizontal", size_hint=(1, 0.13), spacing=10)
        for d in DURATIONS:
            btn = Button(text=f"{d} sn", font_size=sp(17))
            btn.bind(on_release=lambda inst, dur=d: self.set_duration(dur))
            duration_row.add_widget(btn)
        self.layout.add_widget(duration_row)

        self.sound_btn = Button(text="", font_size=sp(17), size_hint=(1, 0.12),
                                 background_color=(0.25, 0.45, 0.75, 1))
        self.sound_btn.bind(on_release=self.toggle_sound)
        self.layout.add_widget(self.sound_btn)

        self.music_btn = Button(text="", font_size=sp(17), size_hint=(1, 0.12),
                                 background_color=(0.45, 0.25, 0.65, 1))
        self.music_btn.bind(on_release=self.toggle_music)
        self.layout.add_widget(self.music_btn)

        back_btn = Button(text="Geri", font_size=sp(15), size_hint=(1, 0.11),
                           background_color=(0.3, 0.3, 0.3, 1))
        back_btn.bind(on_release=lambda *a: setattr(self.manager, "current", "menu"))
        self.layout.add_widget(back_btn)
        self.layout.add_widget(Label(size_hint=(1, 0.16)))

        self.add_widget(self.layout)

    def on_pre_enter(self, *a):
        self.apply_theme(App.get_running_app().data["selected_theme"])
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        self.duration_label.text = f"Süre: {app.game_duration} saniye"
        self.sound_btn.text = "Ses Efektleri: ACIK" if app.sound_enabled else "Ses Efektleri: KAPALI"
        self.music_btn.text = "Muzik: ACIK" if app.music_enabled else "Muzik: KAPALI"

    def set_duration(self, duration):
        App.get_running_app().game_duration = duration
        self.refresh()

    def toggle_sound(self, *a):
        app = App.get_running_app()
        app.sound_enabled = not app.sound_enabled
        self.refresh()

    def toggle_music(self, *a):
        app = App.get_running_app()
        app.music_enabled = not app.music_enabled
        if not app.music_enabled and app.music:
            app.music.stop()
        self.refresh()


# ----------------------------------------------------------------------
# Mağaza (Temalar)
# -----------------------------------------------------
