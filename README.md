# StretchLab — Putaran Bahu v1.0

## Isi paket
- `stretchlab_putaran_bahu_v1.py`: generator scene Blender.
- Scene menghasilkan mannequin 3D sederhana untuk memeriksa alur produksi, timing, kamera, dan pipeline MP4.

## Cara menjalankan
1. Instal Blender versi desktop.
2. Buka Blender → workspace **Scripting**.
3. Buka file `stretchlab_putaran_bahu_v1.py`.
4. Klik **Run Script**.
5. File `.blend` akan dibuat di folder kerja Blender.
6. Untuk membuat video, pilih **Render → Render Animation**.

## Batasan penting
Ini adalah **motion blockout**, bukan animasi manusia fotorealistis final. Bentuk tubuh dan overlay deltoid masih berupa geometri proxy. Animasi bahu belum menjadi simulasi anatomi lengkap skapula-klavikula. Kamera front/45°/side disiapkan sebagai marker; aktifkan *Bind Camera to Markers* di Timeline bila ingin render dengan pergantian kamera otomatis.

Untuk standar final StretchLab diperlukan:
- model manusia 3D berlisensi dengan mesh berkualitas tinggi;
- rig tubuh yang mendukung tulang belikat, klavikula, dan sendi bahu;
- mesh/overlay anatomi deltoid yang mengikuti deformasi;
- motion capture atau animasi keyframe yang diverifikasi secara biomekanika;
- pemeriksaan oleh fisioterapis/pelatih kompeten sebelum dijadikan instruksi latihan.

## Parameter default
- 1920 × 1080
- 60 FPS
- 8 detik
- MP4 / H.264
- Cycles render, 96 samples

Ubah `OUTPUT_PATH` pada bagian konfigurasi jika ingin menyimpan video ke lokasi lain.
