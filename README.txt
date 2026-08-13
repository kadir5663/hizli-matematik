HIZLI MATEMATİK - Tam Sürüm
=============================

ÇALIŞTIRMAK İÇİN (venv aktifken, Kivy zaten kurulu):
   cd Desktop\HizliMatematik
   venv\Scripts\activate
   python main.py

YENİ EKLENEN ÖZELLİKLER:

👤 Oyuncu Adı
   Ana menüde sol üstteki "👤 Oyuncu" butonuna dokunup adını değiştirebilirsin.

🪙 Coin Sistemi
   Her doğru cevap +2 coin kazandırır. Coin'lerini Mağaza'da harcayabilirsin.

🛒 Mağaza (Temalar)
   4 farklı renk teması var: Klasik (ücretsiz), Orman (100 coin),
   Gün Batımı (150 coin), Okyanus (200 coin). Satın aldığın temayı
   seçtiğinde tüm ekranların arka plan rengi değişir.

🏆 Başarımlar
   6 farklı başarım var (ilk oyun, 100 doğru cevap, 10 kombo, tek oyunda
   500+ skor, tüm zorlukları deneme, 500 coin biriktirme). Kilidini
   açtıkça Başarımlar ekranında ✅ ile işaretlenir.

📊 İstatistik & Rekor
   Oynanan oyun sayısı, toplam doğru/yanlış, doğruluk yüzdesi, en yüksek
   kombo ve her zorluk için ayrı rekor burada gösterilir.

📅 Günlük Görev
   Her gün 20 doğru cevap vermek +50 coin kazandırır. İlerleme ana
   menüde görünür, gece yarısı sıfırlanır.

🎵 Müzik
   Oyun sırasında döngüsel bir arka plan melodisi çalar. Ayarlar'dan
   ses efektlerinden bağımsız olarak açıp kapatabilirsin.

💾 Kayıt Sistemi
   Oyuncu adı, coin, rekorlar, istatistikler, başarımlar, sahip olunan
   temalar ve günlük görev durumu bilgisayarında kalıcı olarak saklanır
   (playerdata.json). Uygulamayı kapatıp açsan bile kaybolmaz.

MEVCUT (önceki sürümden):
   Kombo sistemi, hız bonusu, 4 zorluk seviyesi (Kolay/Orta/Zor/Deli
   Modu), ses efektleri, skor bazlı seviye sistemi.

❤️ Can Hakkı
   3 canın var. Her yanlış cevap bir can götürür, canlar biterse süre
   dolmasa bile oyun biter. Kalan canlar üst kısımda kalp ikonlarıyla
   gösterilir.

🃏 Joker Sistemi
   3 tür joker var:
   - ⏸️ Süre Dondur: 5 saniyeliğine süreyi durdurur
   - ⏭️ Soru Atla: cevapsız, cezasız yeni soruya geçer
   - 💡 İpucu: cevabın hangi aralıkta olduğunu gösterir
   Her oyuncu başlangıçta 2'şer tane ücretsiz joker ile başlar,
   Mağaza'dan coin karşılığı +3'lük paketler satın alınabilir.
   Joker stokun kalıcıdır, oyunlar arasında biriktirebilirsin.

➕ Yeni Soru Türleri
   Orta ve Zor zorluklarda artık yüzde ("150'nin %20'si") ve karekök
   ("√144") soruları da çıkabiliyor. Zor'da ayrıca aynı paydalı kesir
   toplama soruları var ("3/4 + 1/4"). Cevaplar hep tam sayı çıkacak
   şekilde tasarlandı (örn. kesirler her zaman tam sayıya tamamlanacak
   şekilde seçiliyor). Deli Modu'na da karekök içeren yeni bir soru
   şablonu eklendi.

🎉 Görsel Efektler
   Doğru cevapta ekranda küçük bir konfeti patlaması ve uçan "+puan"
   yazısı beliriyor. Yanlış cevapta ekran hafifçe sallanıyor.

📺 Reklam İzleyerek Devam Et
   Canların biterse "Reklam İzle (+1 Can)" seçeneği çıkıyor. Bu ŞU AN
   SİMÜLE EDİLMİŞ bir reklam (3 saniyelik sahte geri sayım) — gerçek
   bir reklam ağına (AdMob gibi) henüz bağlı değil. Her oyunda sadece
   bir kez kullanılabiliyor. Gerçek reklamlarla kazanç elde etmek
   istersen, ileride bir AdMob hesabı açıp python-for-android'in
   admob eklentisini (recipe) buildozer.spec'e eklememiz gerekir —
   bu, Google Play Console'da uygulamayı yayınlamayı da gerektiren
   ayrı bir aşamadır.

🎨 Uygulama İkonu
   icon.png artık projede, buildozer.spec zaten bunu APK ikonu olarak
   kullanacak şekilde ayarlı.

SONRAKİ ADIM:
   Test ettikten sonra APK oluşturma aşamasına geçebiliriz.

=============================================
APK OLUŞTURMA (GitHub Actions ile, kurulum gerektirmez)
=============================================

1) GitHub'da yeni bir repo (depo) oluştur:
   - github.com'a giriş yap, sağ üstten "+" -> "New repository"
   - İsim ver (örn: hizli-matematik), "Public" veya "Private" fark etmez
   - "Create repository" de

2) Bu klasördeki TÜM dosyaları (main.py, sounds/, buildozer.spec,
   icon.png, .github/ klasörü dahil) o repoya yükle:
   - En kolay yol: repo sayfasında "uploading an existing file" linkine
     tıkla, tüm dosya ve klasörleri sürükle-bırak yap, "Commit changes" de
   - ÖNEMLİ: .github klasörü gizli görünebilir, dosya gezgininde
     gizli dosyaları göster ayarını aç ki onu da sürükleyebilesin

3) Yükleme bitince GitHub otomatik olarak APK derlemeye başlar.
   Bunu görmek için repo sayfasında üstteki "Actions" sekmesine gir.
   Sarı nokta = devam ediyor, yeşil tik = başarılı (yaklaşık 10-15 dk sürer).

4) Yeşil tik geldiğinde, o çalışmanın (workflow run) sayfasına gir,
   en altta "Artifacts" bölümünde "HizliMatematik-APK" göreceksin.
   Tıklayıp indir (bir .zip iner, içinde .apk dosyası var).

5) .apk dosyasını telefonuna aktar (USB kablo, WhatsApp'a kendine
   gönderme, Google Drive vb.) ve telefonda dosyaya dokunup kur.
   Telefon "bilinmeyen kaynaklardan yükleme" izni isteyebilir,
   izin ver.

Kırmızı çarpı (❌) gelirse, "Actions" sekmesinde o çalışmaya tıklayıp
hata loglarını buraya yapıştır, birlikte çözeriz.
