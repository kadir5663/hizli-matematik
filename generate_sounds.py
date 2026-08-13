"""
Hızlı Matematik için basit .wav ses efektleri üretir.
Harici kütüphane gerekmez, sadece Python'un yerleşik 'wave' modülünü kullanır.
Bu script sadece bir kereye mahsus çalıştırıldı, tekrar çalıştırman gerekmez.
"""
import wave
import struct
import math

SAMPLE_RATE = 44100


def make_tone(filename, segments):
    frames = []
    for freq, duration, volume in segments:
        n_samples = int(SAMPLE_RATE * duration)
        for i in range(n_samples):
            t = i / SAMPLE_RATE
            fade_len = int(SAMPLE_RATE * 0.01)
            fade = 1.0
            if i < fade_len:
                fade = i / fade_len
            elif i > n_samples - fade_len:
                fade = (n_samples - i) / fade_len
            value = math.sin(2 * math.pi * freq * t) * volume * fade
            frames.append(int(value * 32767))

    with wave.open(filename, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        for sample in frames:
            wf.writeframesraw(struct.pack("<h", sample))


# Doğru cevap: net, yükselen iki nota
make_tone("sounds/correct.wav", [
    (700, 0.06, 0.4),
    (1000, 0.09, 0.4),
])

# Yanlış cevap: kısa, alçak, hafif tırmalayıcı
make_tone("sounds/wrong.wav", [
    (220, 0.08, 0.4),
    (160, 0.12, 0.4),
])

# Seviye atlama: kısa üç notalık yükselen arpej
make_tone("sounds/levelup.wav", [
    (500, 0.08, 0.35),
    (650, 0.08, 0.35),
    (900, 0.14, 0.4),
])

# Oyun bitti: alçalan ton
make_tone("sounds/gameover.wav", [
    (400, 0.15, 0.4),
    (300, 0.15, 0.4),
    (200, 0.25, 0.4),
])

# Arka plan müziği: kısa, döngüye uygun basit bir arpej (C majör + D minör)
make_tone("sounds/music.wav", [
    (261.63, 0.18, 0.22),  # C4
    (329.63, 0.18, 0.22),  # E4
    (392.00, 0.18, 0.22),  # G4
    (523.25, 0.18, 0.22),  # C5
    (392.00, 0.18, 0.22),  # G4
    (329.63, 0.18, 0.22),  # E4
    (293.66, 0.18, 0.22),  # D4
    (349.23, 0.18, 0.22),  # F4
    (440.00, 0.18, 0.22),  # A4
    (587.33, 0.18, 0.22),  # D5
    (440.00, 0.18, 0.22),  # A4
    (349.23, 0.18, 0.22),  # F4
])

# Joker kullanımı: kısa, hafif "pop" sesi
make_tone("sounds/joker.wav", [
    (600, 0.05, 0.3),
    (450, 0.08, 0.3),
])

print("Sesler oluşturuldu.")
