STRETCHLAB — PWA ANDROID OFFLINE

Isi:
- index.html: aplikasi
- manifest.webmanifest: metadata PWA
- sw.js: cache offline
- icon.svg: ikon aplikasi

CARA PAKAI:
1. Ekstrak ZIP ini.
2. Untuk uji cepat, buka index.html di browser. Fungsi aplikasi dan penyimpanan lokal berjalan, tetapi instalasi PWA/offline cache tidak aktif pada file://.
3. Untuk memasang sebagai PWA, unggah seluruh isi folder ke hosting HTTPS statis (misalnya GitHub Pages atau Netlify).
4. Buka URL HTTPS tersebut di Chrome Android, pilih menu browser > Tambahkan ke layar utama / Install app.
5. Buka sekali saat online agar service worker menyimpan file. Setelah itu aplikasi dapat dibuka offline.

CATATAN:
- Data disimpan di localStorage browser/perangkat yang digunakan.
- Ekspor cadangan tersedia di Pengaturan.
- Timer berjalan selama sesi aplikasi terbuka; bukan timer latar belakang.
- Waktu pagi/malam adalah jadwal tampilan, belum mengirim notifikasi terjadwal.
- Panduan gerakan berupa ilustrasi emoji + instruksi teks, agar ukuran kecil dan bisa offline.
