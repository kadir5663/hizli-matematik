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

JOKER_LABELS = {"dondur": "⏸️ Süre Dondur", "atla": "⏭️ Soru Atla", "ipucu": "💡 İpucu"}
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
        text=text, font_size=18, bold=True, color=color,
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
        self.name_btn = Button(text="👤 Oyuncu", font_size=14,
                                background_color=(0.25, 0.25, 0.3, 1))
        self.name_btn.bind(on_release=lambda *a: setattr(self.manager, "current", "name"))
        self.coin_label = Label(text="🪙 0", font_size=16)
        top_row.add_widget(self.name_btn)
        top_row.add_widget(self.coin_label)
        layout.add_widget(top_row)

        title = Label(text="HIZLI MATEMATİK", font_size=26, bold=True, size_hint=(1, 0.14))
        layout.add_widget(title)

        self.daily_label = Label(text="", font_size=13, size_hint=(1, 0.1), color=(1, 0.85, 0.3, 1))
        layout.add_widget(self.daily_label)

        play_btn = Button(text="OYNA", font_size=20, size_hint=(1, 0.11),
                           background_color=(0.2, 0.7, 0.3, 1))
        play_btn.bind(on_release=lambda *a: setattr(self.manager, "current", "difficulty"))
        layout.add_widget(play_btn)

        def menu_btn(text, target, color):
            b = Button(text=text, font_size=16, size_hint=(1, 0.09), background_color=color)
            b.bind(on_release=lambda *a: setattr(self.manager, "current", target))
            return b

        layout.add_widget(menu_btn("🛒 MAĞAZA", "shop", (0.55, 0.4, 0.15, 1)))
        layout.add_widget(menu_btn("🏆 BAŞARIMLAR", "achievements", (0.25, 0.45, 0.75, 1)))
        layout.add_widget(menu_btn("📊 İSTATİSTİK & REKOR", "stats", (0.35, 0.3, 0.55, 1)))
        layout.add_widget(menu_btn("⚙️ AYARLAR", "settings", (0.35, 0.35, 0.4, 1)))

        exit_btn = Button(text="ÇIKIŞ", font_size=16, size_hint=(1, 0.09),
                           background_color=(0.6, 0.2, 0.2, 1))
        exit_btn.bind(on_release=lambda *a: App.get_running_app().stop())
        layout.add_widget(exit_btn)

        self.add_widget(layout)

    def on_pre_enter(self, *a):
        app = App.get_running_app()
        self.name_btn.text = f"👤 {app.data['name']}"
        self.coin_label.text = f"🪙 {app.data['coins']}"

        daily = app.data["daily"]
        if daily["date"] != today_str():
            daily["date"] = today_str()
            daily["progress"] = 0
            daily["completed"] = False
            save_data(app.data)

        if daily["completed"]:
            self.daily_label.text = f"✅ Günlük Görev Tamamlandı! (+{DAILY_REWARD} coin alındı)"
        else:
            self.daily_label.text = f"📅 Günlük Görev: {daily['progress']}/{DAILY_TARGET} doğru cevap"


# ----------------------------------------------------------------------
# Oyuncu adı ekranı
# ----------------------------------------------------------------------

class NameScreen(ThemedScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=40, spacing=16)
        layout.add_widget(Label(text="OYUNCU ADI", font_size=24, bold=True, size_hint=(1, 0.2)))

        self.input = TextInput(text="", font_size=22, multiline=False, size_hint=(1, 0.15),
                                halign="center", padding=[10, 20, 10, 10])
        layout.add_widget(self.input)

        save_btn = Button(text="KAYDET", font_size=18, size_hint=(1, 0.13),
                           background_color=(0.2, 0.7, 0.3, 1))
        save_btn.bind(on_release=self.save_name)
        layout.add_widget(save_btn)

        back_btn = Button(text="Geri", font_size=15, size_hint=(1, 0.11),
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
        layout.add_widget(Label(text="ZORLUK SEÇ", font_size=26, bold=True, size_hint=(1, 0.2)))

        colors = {
            "Kolay": (0.2, 0.7, 0.3, 1),
            "Orta": (0.85, 0.7, 0.1, 1),
            "Zor": (0.8, 0.3, 0.15, 1),
            "Deli Modu": (0.55, 0.15, 0.65, 1),
        }
        for diff in DIFFICULTIES:
            btn = Button(text=diff.upper(), font_size=20, size_hint=(1, 0.15),
                         background_color=colors[diff])
            btn.bind(on_release=lambda inst, d=diff: self.start(d))
            layout.add_widget(btn)

        back_btn = Button(text="Geri", font_size=16, size_hint=(1, 0.12),
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
        self.layout.add_widget(Label(text="AYARLAR", font_size=26, bold=True, size_hint=(1, 0.16)))

        self.duration_label = Label(text="", font_size=17, size_hint=(1, 0.1))
        self.layout.add_widget(self.duration_label)

        duration_row = BoxLayout(orientation="horizontal", size_hint=(1, 0.13), spacing=10)
        for d in DURATIONS:
            btn = Button(text=f"{d} sn", font_size=17)
            btn.bind(on_release=lambda inst, dur=d: self.set_duration(dur))
            duration_row.add_widget(btn)
        self.layout.add_widget(duration_row)

        self.sound_btn = Button(text="", font_size=17, size_hint=(1, 0.12),
                                 background_color=(0.25, 0.45, 0.75, 1))
        self.sound_btn.bind(on_release=self.toggle_sound)
        self.layout.add_widget(self.sound_btn)

        self.music_btn = Button(text="", font_size=17, size_hint=(1, 0.12),
                                 background_color=(0.45, 0.25, 0.65, 1))
        self.music_btn.bind(on_release=self.toggle_music)
        self.layout.add_widget(self.music_btn)

        back_btn = Button(text="Geri", font_size=15, size_hint=(1, 0.11),
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
        self.sound_btn.text = "🔊 Ses Efektleri: AÇIK" if app.sound_enabled else "🔇 Ses Efektleri: KAPALI"
        self.music_btn.text = "🎵 Müzik: AÇIK" if app.music_enabled else "🎵 Müzik: KAPALI"

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
# ----------------------------------------------------------------------

class ShopScreen(ThemedScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=28, spacing=10)
        self.layout.add_widget(Label(text="MAĞAZA", font_size=26, bold=True, size_hint=(1, 0.12)))
        self.coin_label = Label(text="🪙 0", font_size=18, size_hint=(1, 0.08))
        self.layout.add_widget(self.coin_label)

        self.scroll = ScrollView(size_hint=(1, 0.66))
        self.items_box = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None, padding=[0, 4])
        self.items_box.bind(minimum_height=self.items_box.setter("height"))
        self.scroll.add_widget(self.items_box)
        self.layout.add_widget(self.scroll)

        back_btn = Button(text="Geri", font_size=15, size_hint=(1, 0.1),
                           background_color=(0.3, 0.3, 0.3, 1))
        back_btn.bind(on_release=lambda *a: setattr(self.manager, "current", "menu"))
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)

    def on_pre_enter(self, *a):
        app = App.get_running_app()
        self.apply_theme(app.data["selected_theme"])
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        self.coin_label.text = f"🪙 {app.data['coins']}"
        self.items_box.clear_widgets()

        for theme_name, theme in THEMES.items():
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=70, spacing=8)

            swatch = Label(text="", size_hint=(0.15, 1))
            with swatch.canvas.before:
                Color(*theme["bg"])
                swatch_rect = Rectangle(pos=swatch.pos, size=swatch.size)
            swatch.bind(pos=lambda inst, val, r=swatch_rect: setattr(r, "pos", val))
            swatch.bind(size=lambda inst, val, r=swatch_rect: setattr(r, "size", val))
            row.add_widget(swatch)

            owned = theme_name in app.data["owned_themes"]
            selected = app.data["selected_theme"] == theme_name
            info = Label(
                text=f"{theme_name}\n{'Sahipsin' if owned else str(theme['price']) + ' coin'}",
                font_size=14, size_hint=(0.5, 1),
            )
            row.add_widget(info)

            if selected:
                action_btn = Button(text="SEÇİLİ", font_size=13, size_hint=(0.35, 1),
                                     background_color=(0.3, 0.3, 0.3, 1), disabled=True)
            elif owned:
                action_btn = Button(text="SEÇ", font_size=13, size_hint=(0.35, 1),
                                     background_color=(0.25, 0.45, 0.75, 1))
                action_btn.bind(on_release=lambda inst, t=theme_name: self.select_theme(t))
            else:
                action_btn = Button(text="SATIN AL", font_size=13, size_hint=(0.35, 1),
                                     background_color=(0.55, 0.4, 0.15, 1))
                action_btn.bind(on_release=lambda inst, t=theme_name: self.buy_theme(t))

            row.add_widget(action_btn)
            self.items_box.add_widget(row)

        self.items_box.add_widget(
            Label(text="JOKERLER", font_size=16, bold=True, size_hint_y=None, height=34)
        )
        for key, label_text in JOKER_LABELS.items():
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=60, spacing=8)
            info = Label(
                text=f"{label_text}\nStok: {app.data['jokers'].get(key, 0)}",
                font_size=14, size_hint=(0.65, 1),
            )
            row.add_widget(info)
            buy_btn = Button(
                text=f"+{JOKER_PACK_SIZE} ({JOKER_PRICES[key]} coin)", font_size=12,
                size_hint=(0.35, 1), background_color=(0.55, 0.4, 0.15, 1),
            )
            buy_btn.bind(on_release=lambda inst, k=key: self.buy_joker(k))
            row.add_widget(buy_btn)
            self.items_box.add_widget(row)

    def buy_joker(self, key):
        app = App.get_running_app()
        price = JOKER_PRICES[key]
        if app.data["coins"] >= price:
            app.data["coins"] -= price
            app.data["jokers"][key] = app.data["jokers"].get(key, 0) + JOKER_PACK_SIZE
            save_data(app.data)
            self.refresh()

    def buy_theme(self, theme_name):
        app = App.get_running_app()
        price = THEMES[theme_name]["price"]
        if app.data["coins"] >= price:
            app.data["coins"] -= price
            app.data["owned_themes"].append(theme_name)
            app.data["selected_theme"] = theme_name
            save_data(app.data)
            apply_theme_everywhere(self.manager, theme_name)
            self.refresh()

    def select_theme(self, theme_name):
        app = App.get_running_app()
        app.data["selected_theme"] = theme_name
        save_data(app.data)
        apply_theme_everywhere(self.manager, theme_name)
        self.refresh()


# ----------------------------------------------------------------------
# Başarımlar
# ----------------------------------------------------------------------

class AchievementsScreen(ThemedScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=28, spacing=10)
        self.layout.add_widget(Label(text="BAŞARIMLAR", font_size=26, bold=True, size_hint=(1, 0.12)))

        self.scroll = ScrollView(size_hint=(1, 0.76))
        self.items_box = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None, padding=[0, 4])
        self.items_box.bind(minimum_height=self.items_box.setter("height"))
        self.scroll.add_widget(self.items_box)
        self.layout.add_widget(self.scroll)

        back_btn = Button(text="Geri", font_size=15, size_hint=(1, 0.1),
                           background_color=(0.3, 0.3, 0.3, 1))
        back_btn.bind(on_release=lambda *a: setattr(self.manager, "current", "menu"))
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)

    def on_pre_enter(self, *a):
        app = App.get_running_app()
        self.apply_theme(app.data["selected_theme"])
        self.items_box.clear_widgets()

        unlocked = set(app.data["achievements"])
        for ach in ACHIEVEMENTS:
            is_unlocked = ach["id"] in unlocked
            icon = "✅" if is_unlocked else "🔒"
            color = (0.3, 0.9, 0.3, 1) if is_unlocked else (0.6, 0.6, 0.6, 1)
            label = Label(
                text=f"{icon} {ach['title']}\n{ach['desc']}",
                font_size=14, color=color,
                size_hint_y=None, height=60,
            )
            self.items_box.add_widget(label)


# ----------------------------------------------------------------------
# İstatistik & Rekorlar
# ----------------------------------------------------------------------

class StatsScreen(ThemedScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=28, spacing=8)
        self.layout.add_widget(Label(text="İSTATİSTİK & REKOR", font_size=22, bold=True, size_hint=(1, 0.12)))

        self.scroll = ScrollView(size_hint=(1, 0.78))
        self.content = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None, padding=[0, 4])
        self.content.bind(minimum_height=self.content.setter("height"))
        self.scroll.add_widget(self.content)
        self.layout.add_widget(self.scroll)

        back_btn = Button(text="Geri", font_size=15, size_hint=(1, 0.1),
                           background_color=(0.3, 0.3, 0.3, 1))
        back_btn.bind(on_release=lambda *a: setattr(self.manager, "current", "menu"))
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)

    def on_pre_enter(self, *a):
        app = App.get_running_app()
        self.apply_theme(app.data["selected_theme"])
        self.content.clear_widgets()
        data = app.data
        stats = data["stats"]

        def add_line(text, size=16, bold=False):
            lbl = Label(text=text, font_size=size, bold=bold, size_hint_y=None, height=32)
            self.content.add_widget(lbl)

        add_line(f"Oyuncu: {data['name']}", 18, True)
        add_line(f"🪙 Coin: {data['coins']}")
        add_line("")
        add_line("Rekorlar (zorluğa göre):", 16, True)
        for diff in DIFFICULTIES:
            add_line(f"  {diff}: {data['high_scores'].get(diff, 0)}")
        add_line("")
        add_line("Genel İstatistikler:", 16, True)
        add_line(f"  Oynanan oyun: {stats['games_played']}")
        add_line(f"  Toplam doğru: {stats['total_correct']}")
        add_line(f"  Toplam yanlış: {stats['total_wrong']}")

        total_answers = stats["total_correct"] + stats["total_wrong"]
        accuracy = (stats["total_correct"] / total_answers * 100) if total_answers else 0
        add_line(f"  Doğruluk oranı: %{accuracy:.0f}")
        add_line(f"  🔥 En yüksek kombo: {stats['best_combo_ever']}")


# ----------------------------------------------------------------------
# Oyun Ekranı
# ----------------------------------------------------------------------

class GameScreen(ThemedScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.correct_sound = load_sound("sounds/correct.wav")
        self.wrong_sound = load_sound("sounds/wrong.wav")
        self.levelup_sound = load_sound("sounds/levelup.wav")

        root = BoxLayout(orientation="vertical", padding=24, spacing=8)

        top_row = BoxLayout(orientation="horizontal", size_hint=(1, 0.09))
        self.timer_label = Label(text="⏱️ 60", font_size=20)
        self.score_label = Label(text="⭐ 0", font_size=20)
        self.coin_label = Label(text="🪙 0", font_size=16)
        top_row.add_widget(self.timer_label)
        top_row.add_widget(self.score_label)
        top_row.add_widget(self.coin_label)
        root.add_widget(top_row)

        self.lives_label = Label(text="❤️❤️❤️", font_size=16, size_hint=(1, 0.05))
        root.add_widget(self.lives_label)

        self.level_label = Label(text="Seviye 1", font_size=14, size_hint=(1, 0.05))
        root.add_widget(self.level_label)

        self.combo_label = Label(text="", font_size=18, size_hint=(1, 0.07), color=(1, 0.6, 0.1, 1))
        root.add_widget(self.combo_label)

        root.add_widget(Label(size_hint=(1, 0.06)))

        self.question_label = Label(text="", font_size=40, bold=True, size_hint=(1, 0.2))
        root.add_widget(self.question_label)

        self.answer_input = TextInput(
            text="", font_size=28, multiline=False, input_filter="int",
            size_hint=(1, 0.11), halign="center", padding=[10, 20, 10, 10],
        )
        self.answer_input.bind(on_text_validate=self.submit_answer)
        root.add_widget(self.answer_input)

        submit_btn = Button(text="ONAYLA", font_size=19, size_hint=(1, 0.11),
                             background_color=(0.2, 0.7, 0.3, 1))
        submit_btn.bind(on_release=self.submit_answer)
        root.add_widget(submit_btn)

        joker_row = BoxLayout(orientation="horizontal", size_hint=(1, 0.09), spacing=6)
        self.freeze_btn = Button(text="⏸️ Dondur", font_size=11)
        self.freeze_btn.bind(on_release=lambda *a: self.use_joker("dondur"))
        self.skip_btn = Button(text="⏭️ Atla", font_size=11)
        self.skip_btn.bind(on_release=lambda *a: self.use_joker("atla"))
        self.hint_btn = Button(text="💡 İpucu", font_size=11)
        self.hint_btn.bind(on_release=lambda *a: self.use_joker("ipucu"))
        joker_row.add_widget(self.freeze_btn)
        joker_row.add_widget(self.skip_btn)
        joker_row.add_widget(self.hint_btn)
        root.add_widget(joker_row)
        self.joker_buttons = {"dondur": self.freeze_btn, "atla": self.skip_btn, "ipucu": self.hint_btn}

        self.feedback_label = Label(text="", font_size=20, size_hint=(1, 0.1))
        root.add_widget(self.feedback_label)

        self.hint_label = Label(text="", font_size=13, size_hint=(1, 0.06), color=(0.3, 0.85, 0.95, 1))
        root.add_widget(self.hint_label)

        self.add_widget(root)
        self.root_layout = root

        # "Reklam izle, devam et" kutusu (can bitince gösterilir, önceden oluşturulur ama eklenmez)
        self.continue_overlay = BoxLayout(
            orientation="vertical", size_hint=(0.85, 0.4),
            pos_hint={"center_x": 0.5, "center_y": 0.5}, spacing=10, padding=16,
        )
        with self.continue_overlay.canvas.before:
            Color(0.05, 0.05, 0.08, 0.94)
            self.continue_bg = Rectangle(pos=self.continue_overlay.pos, size=self.continue_overlay.size)
        self.continue_overlay.bind(
            pos=lambda *a: (setattr(self.continue_bg, "pos", self.continue_overlay.pos)),
            size=lambda *a: (setattr(self.continue_bg, "size", self.continue_overlay.size)),
        )

        self.continue_title = Label(text="💔 Canın Bitti!", font_size=20, bold=True, size_hint=(1, 0.3))
        self.continue_overlay.add_widget(self.continue_title)

        self.watch_ad_btn = Button(text="📺 Reklam İzle (+1 Can)", font_size=15, size_hint=(1, 0.35),
                                    background_color=(0.2, 0.55, 0.85, 1))
        self.watch_ad_btn.bind(on_release=self.watch_ad)
        self.continue_overlay.add_widget(self.watch_ad_btn)

        end_now_btn = Button(text="Oyunu Bitir", font_size=14, size_hint=(1, 0.3),
                              background_color=(0.5, 0.2, 0.2, 1))
        end_now_btn.bind(on_release=self.end_now_from_overlay)
        self.continue_overlay.add_widget(end_now_btn)

        self.joker_sound = load_sound("sounds/joker.wav")

        self.difficulty = "Kolay"
        self.time_left = 60
        self.score = 0
        self.streak = 0
        self.max_combo = 0
        self.total_questions = 0
        self.correct_count = 0
        self.wrong_count = 0
        self.current_answer = 0
        self.question_start_time = 0
        self.current_level = 1
        self.lives = STARTING_LIVES
        self.frozen = False
        self.ad_used = False
        self._clock_event = None
        self._ad_event = None

    def start_game(self, difficulty):
        app = App.get_running_app()
        self.apply_theme(app.data["selected_theme"])

        self.difficulty = difficulty
        self.time_left = app.game_duration
        self.score = 0
        self.streak = 0
        self.max_combo = 0
        self.total_questions = 0
        self.correct_count = 0
        self.wrong_count = 0
        self.current_level = 1

        self.score_label.text = "⭐ 0"
        self.timer_label.text = f"⏱️ {self.time_left}"
        self.timer_label.color = (1, 1, 1, 1)
        self.coin_label.text = f"🪙 {app.data['coins']}"
        self.level_label.text = "Seviye 1"
        self.combo_label.text = ""
        self.feedback_label.text = ""
        self.lives = STARTING_LIVES
        self.frozen = False
        self.ad_used = False
        self.update_lives_label()
        self.refresh_joker_buttons()

        if self.continue_overlay.parent is not None:
            self.remove_widget(self.continue_overlay)

        self.next_question()
        self.answer_input.text = ""
        Clock.schedule_once(lambda dt: setattr(self.answer_input, "focus", True), 0.3)

        if self._clock_event is None:
            self._clock_event = Clock.schedule_interval(self.tick, 1.0)

        if app.music_enabled and app.music:
            app.music.loop = True
            app.music.play()

    def next_question(self):
        text, answer = generate_question(self.difficulty)
        self.question_label.text = f"{text} = ?"
        self.current_answer = answer
        self.question_start_time = Clock.get_boottime()
        self.answer_input.text = ""
        self.hint_label.text = ""

    def tick(self, dt):
        if self.frozen:
            return
        self.time_left -= 1
        self.timer_label.text = f"⏱️ {max(self.time_left, 0)}"
        if self.time_left <= 0:
            self.end_game()

    def update_lives_label(self):
        self.lives_label.text = "❤️" * self.lives + "🖤" * (STARTING_LIVES - self.lives)

    def refresh_joker_buttons(self):
        app = App.get_running_app()
        jokers = app.data["jokers"]
        for key, btn in self.joker_buttons.items():
            count = jokers.get(key, 0)
            base_text = JOKER_LABELS[key].split(" ", 1)[1]
            icon = JOKER_LABELS[key].split(" ", 1)[0]
            btn.text = f"{icon} {base_text} x{count}"
            btn.disabled = count <= 0

    def use_joker(self, kind):
        if self.time_left <= 0 or self.lives <= 0:
            return
        app = App.get_running_app()
        if app.data["jokers"].get(kind, 0) <= 0:
            return

        app.data["jokers"][kind] -= 1
        save_data(app.data)
        self.refresh_joker_buttons()
        if app.sound_enabled and self.joker_sound:
            self.joker_sound.play()

        if kind == "dondur":
            self.frozen = True
            self.timer_label.color = (0.3, 0.85, 0.95, 1)
            Clock.schedule_once(self._unfreeze, 5)
        elif kind == "atla":
            self.next_question()
        elif kind == "ipucu":
            margin = HINT_MARGIN.get(self.difficulty, 15)
            lower = self.current_answer - margin
            upper = self.current_answer + margin
            self.hint_label.text = f"💡 İpucu: cevap {lower} ile {upper} arasında"

    def _unfreeze(self, dt):
        self.frozen = False
        self.timer_label.color = (1, 1, 1, 1)

    def show_continue_overlay(self):
        if self._clock_event is not None:
            self._clock_event.cancel()
            self._clock_event = None

        if self.ad_used:
            # Bu oyunda reklam hakkı zaten kullanıldı, doğrudan oyunu bitir
            self.end_game()
            return

        self.watch_ad_btn.disabled = False
        self.watch_ad_btn.text = "📺 Reklam İzle (+1 Can)"
        self.continue_title.text = "💔 Canın Bitti!"
        self.add_widget(self.continue_overlay)

    def watch_ad(self, *a):
        # NOT: Bu simüle edilmiş bir reklamdır. Gerçek AdMob/reklam ağı
        # entegrasyonu için ayrı bir SDK kurulumu gerekir (bkz. README).
        self.watch_ad_btn.disabled = True
        self._ad_countdown = 3
        self.continue_title.text = f"📺 Reklam oynatılıyor... {self._ad_countdown}"
        self._ad_event = Clock.schedule_interval(self._ad_tick, 1.0)

    def _ad_tick(self, dt):
        self._ad_countdown -= 1
        if self._ad_countdown <= 0:
            if self._ad_event is not None:
                self._ad_event.cancel()
                self._ad_event = None
            self.finish_ad()
        else:
            self.continue_title.text = f"📺 Reklam oynatılıyor... {self._ad_countdown}"

    def finish_ad(self):
        self.lives = 1
        self.ad_used = True
        self.update_lives_label()
        self.remove_widget(self.continue_overlay)

        self.feedback_label.text = "🎉 Reklam sayesinde devam ediyorsun!"
        self.feedback_label.color = (0.3, 0.9, 0.3, 1)

        if self._clock_event is None:
            self._clock_event = Clock.schedule_interval(self.tick, 1.0)

        self.next_question()
        self.answer_input.focus = True

    def end_now_from_overlay(self, *a):
        self.remove_widget(self.continue_overlay)
        self.end_game()

    def submit_answer(self, *args):
        if self.time_left <= 0:
            return
        raw = self.answer_input.text.strip()
        if raw == "" or raw == "-":
            return
        try:
            given = int(raw)
        except ValueError:
            return

        response_time = Clock.get_boottime() - self.question_start_time
        self.total_questions += 1
        app = App.get_running_app()

        if given == self.current_answer:
            self.correct_count += 1
            self.streak += 1
            self.max_combo = max(self.max_combo, self.streak)

            points = int(BASE_POINTS[self.difficulty] * combo_multiplier(self.streak))
            points += speed_bonus(response_time)
            self.score += points

            app.data["coins"] += COIN_PER_CORRECT
            self.coin_label.text = f"🪙 {app.data['coins']}"

            daily = app.data["daily"]
            if daily["date"] == today_str() and not daily["completed"]:
                daily["progress"] += 1
                if daily["progress"] >= DAILY_TARGET:
                    daily["completed"] = True
                    app.data["coins"] += DAILY_REWARD
                    self.coin_label.text = f"🪙 {app.data['coins']}"

            self.feedback_label.text = f"✅ DOĞRU!  +{points} PUAN"
            self.feedback_label.color = (0.3, 0.9, 0.3, 1)
            if app.sound_enabled and self.correct_sound:
                self.correct_sound.play()

            spawn_confetti(self, self.question_label.center)
            spawn_flying_text(self, self.score_label.pos, f"+{points}")

            self.combo_label.text = f"🔥 {self.streak}X KOMBO!" if self.streak >= 3 else ""

            new_level = level_for_score(self.score)
            if new_level > self.current_level:
                self.current_level = new_level
                self.level_label.text = f"Seviye {self.current_level}"
                if app.sound_enabled and self.levelup_sound:
                    self.levelup_sound.play()
        else:
            self.wrong_count += 1
            self.streak = 0
            self.combo_label.text = ""
            self.feedback_label.text = f"❌ YANLIŞ! (Doğrusu: {self.current_answer})"
            self.feedback_label.color = (0.9, 0.3, 0.3, 1)
            if app.sound_enabled and self.wrong_sound:
                self.wrong_sound.play()

            self.lives -= 1
            self.update_lives_label()
            shake_widget(self.root_layout)

        self.score_label.text = f"⭐ {self.score}"

        if self.lives <= 0:
            self.show_continue_overlay()
            return

        self.next_question()
        self.answer_input.focus = True

    def end_game(self):
        if self._clock_event is not None:
            self._clock_event.cancel()
            self._clock_event = None
        if self._ad_event is not None:
            self._ad_event.cancel()
            self._ad_event = None

        app = App.get_running_app()
        if app.music:
            app.music.stop()

        data = app.data
        is_new_record = self.score > data["high_scores"].get(self.difficulty, 0)
        if is_new_record:
            data["high_scores"][self.difficulty] = self.score

        stats = data["stats"]
        stats["games_played"] += 1
        stats["total_correct"] += self.correct_count
        stats["total_wrong"] += self.wrong_count
        stats["best_combo_ever"] = max(stats["best_combo_ever"], self.max_combo)
        if self.difficulty not in stats["difficulties_played"]:
            stats["difficulties_played"].append(self.difficulty)

        newly_unlocked = self.check_achievements(data)
        save_data(data)

        result_screen = self.manager.get_screen("gameover")
        result_screen.show_results(
            difficulty=self.difficulty,
            score=self.score,
            total=self.total_questions,
            correct=self.correct_count,
            wrong=self.wrong_count,
            max_combo=self.max_combo,
            high_score=data["high_scores"].get(self.difficulty, 0),
            is_new_record=is_new_record,
            newly_unlocked=newly_unlocked,
        )
        self.manager.current = "gameover"

    def check_achievements(self, data):
        unlocked = set(data["achievements"])
        newly = []
        stats = data["stats"]

        def unlock(ach_id):
            if ach_id not in unlocked:
                unlocked.add(ach_id)
                newly.append(ach_id)

        if stats["games_played"] >= 1:
            unlock("ilk_oyun")
        if stats["total_correct"] >= 100:
            unlock("yuz_dogru")
        if self.max_combo >= 10:
            unlock("kombo_10")
        if self.score >= 500:
            unlock("bes_yuz_skor")
        if set(DIFFICULTIES).issubset(set(stats["difficulties_played"])):
            unlock("tum_zorluklar")
        if data["coins"] >= 500:
            unlock("coin_biriktir")

        data["achievements"] = list(unlocked)
        return newly


# ----------------------------------------------------------------------
# Oyun Bitti
# ----------------------------------------------------------------------

class GameOverScreen(ThemedScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=32, spacing=6)

        self.title_label = Label(text="OYUN BİTTİ", font_size=26, bold=True, size_hint=(1, 0.11))
        self.score_label = Label(text="", font_size=24, bold=True, size_hint=(1, 0.11))
        self.stats_label = Label(text="", font_size=14, size_hint=(1, 0.2))
        self.record_label = Label(text="", font_size=16, size_hint=(1, 0.09))
        self.achievements_label = Label(text="", font_size=13, size_hint=(1, 0.14),
                                         color=(1, 0.85, 0.3, 1))

        self.layout.add_widget(Label(size_hint=(1, 0.03)))
        self.layout.add_widget(self.title_label)
        self.layout.add_widget(self.score_label)
        self.layout.add_widget(self.stats_label)
        self.layout.add_widget(self.record_label)
        self.layout.add_widget(self.achievements_label)

        retry_btn = Button(text="TEKRAR OYNA", font_size=19, size_hint=(1, 0.12),
                            background_color=(0.2, 0.7, 0.3, 1))
        retry_btn.bind(on_release=self.retry)
        menu_btn = Button(text="ANA MENÜ", font_size=17, size_hint=(1, 0.11),
                           background_color=(0.3, 0.3, 0.35, 1))
        menu_btn.bind(on_release=lambda *a: setattr(self.manager, "current", "menu"))

        self.layout.add_widget(retry_btn)
        self.layout.add_widget(menu_btn)

        self.add_widget(self.layout)
        self._difficulty = "Kolay"

    def show_results(self, difficulty, score, total, correct, wrong, max_combo,
                      high_score, is_new_record, newly_unlocked):
        self.apply_theme(App.get_running_app().data["selected_theme"])
        self._difficulty = difficulty
        self.score_label.text = f"⭐ SKOR: {score}"
        self.stats_label.text = (
            f"Zorluk: {difficulty}\n"
            f"Sorular: {total}   Doğru: {correct}   Yanlış: {wrong}\n"
            f"🔥 En yüksek kombo: {max_combo}"
        )
        if is_new_record:
            self.record_label.text = f"🎉 YENİ REKOR! ({high_score})"
            self.record_label.color = (1, 0.85, 0.2, 1)
        else:
            self.record_label.text = f"🏆 REKOR: {high_score}"
            self.record_label.color = (0.8, 0.8, 0.8, 1)

        if newly_unlocked:
            titles = []
            for ach_id in newly_unlocked:
                match = next((a for a in ACHIEVEMENTS if a["id"] == ach_id), None)
                if match:
                    titles.append(match["title"])
            self.achievements_label.text = "🏆 Yeni Başarım: " + ", ".join(titles) if titles else ""
        else:
            self.achievements_label.text = ""

    def retry(self, *a):
        self.manager.current = "game"
        self.manager.get_screen("game").start_game(self._difficulty)


# ----------------------------------------------------------------------
# Uygulama
# ----------------------------------------------------------------------

class HizliMatematikApp(App):
    def build(self):
        self.game_duration = 60
        self.sound_enabled = True
        self.music_enabled = True
        self.data = load_data()
        self.music = load_sound("sounds/music.wav")

        sm = ScreenManager(transition=FadeTransition(duration=0.15))
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(NameScreen(name="name"))
        sm.add_widget(DifficultyScreen(name="difficulty"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(ShopScreen(name="shop"))
        sm.add_widget(AchievementsScreen(name="achievements"))
        sm.add_widget(StatsScreen(name="stats"))
        sm.add_widget(GameScreen(name="game"))
        sm.add_widget(GameOverScreen(name="gameover"))
        sm.current = "menu"

        apply_theme_everywhere(sm, self.data["selected_theme"])
        return sm

    def on_stop(self):
        save_data(self.data)


if __name__ == "__main__":
    HizliMatematikApp().run()
