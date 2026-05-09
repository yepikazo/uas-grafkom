# ⛺ Yuru Camp — Lakeside Night Scene

> Visualisasi 3D real-time lanskap perkemahan tepi Danau Motosu pada malam hari, dibangun sepenuhnya dengan **OpenGL 3.3 Core Profile** dan **Python**.

<!-- Tambahkan screenshot di sini -->
<!-- ![Screenshot](docs/screenshot.png) -->

---

## ✨ Fitur

| Kategori | Detail |
|---|---|
| 🏔️ **Terrain Prosedural** | Mesh 400×400 unit (40K vertices, 80K triangles) dengan bukit, pegunungan, dan cekungan danau |
| 🌊 **Danau Motosu** | Bentuk organik elips 160×80 unit dengan animasi gelombang real-time di vertex shader |
| 🗻 **Gunung Fuji** | Siluet prosedural di skybox — profil vulkanik, topi salju, rim glow, kawah Hoei |
| 🌙 **Langit Malam** | Bintang 2 lapisan (twinkle + variasi warna), bulan dengan halo 3 lapis, jalur Bima Sakti |
| 🔥 **Api Unggun** | 3 titik api dengan sistem partikel dinamis, kayu bakar silang, ring batu acak |
| ⛺ **Perkemahan** | Tenda A-frame, kursi lipat, meja + perlengkapan, lentera, cooler, alas duduk |
| 🌲 **Hutan** | 300+ pohon pinus prosedural tersebar di 4 zona (camp, latar belakang, sisi, tepi danau) |
| 🪲 **Kunang-Kunang** | 120 partikel bioluminesensi — melayang sinusoidal, blink realistis, menghindar kamera |
| 💡 **Pencahayaan** | Multi-source point lights + directional moonlight + fog atmosfer |
| 🎥 **Kamera** | 3 mode: Free-look (WASD), Orbital, dan Sinematik otomatis (7 titik + smoothstep) |

---

## 🚀 Memulai

### Prasyarat

- Python 3.10+
- GPU yang mendukung OpenGL 3.3

### Instalasi

```bash
# Clone repositori
git clone https://github.com/yepikazo/uas-grafkom.git
cd uas-grafkom

# Buat virtual environment (opsional tapi disarankan)
python -m venv .venv

# Aktivasi virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependensi
pip install -r requirements.txt
```

### Menjalankan

```bash
python main.py
```

---

## 🎮 Kontrol

| Input | Mode | Fungsi |
|---|---|---|
| **Mouse drag** (kiri) | Bebas & Orbital | Memutar arah pandang kamera |
| **Scroll mouse** | Bebas | Mengatur kecepatan pergerakan |
| **Scroll mouse** | Orbital | Mengatur jarak zoom |
| **W / A / S / D** | Bebas | Bergerak maju, kiri, mundur, kanan |
| **Space / Shift** | Bebas | Bergerak naik / turun |
| **C** | Semua | Toggle mode kamera (Bebas ↔ Orbital) |
| **V** | Semua | Toggle kamera sinematik otomatis |
| **R** | Orbital | Toggle auto-rotation |
| **ESC** | Semua | Keluar aplikasi |

---

## 📁 Struktur Proyek

```
uas-grafkom/
├── main.py                  # Scene manager & game loop
├── requirements.txt         # Dependensi Python
│
├── core/                    # Modul inti
│   ├── window.py            # Manajemen window Pygame + OpenGL context
│   ├── camera.py            # Sistem kamera 3 mode (free/orbital/sinematik)
│   ├── shader.py            # Kompilasi & manajemen shader GLSL
│   └── terrain_height.py    # Heightmap prosedural & layout scene
│
├── objects/                 # Objek 3D (semua prosedural, tanpa file model)
│   ├── terrain.py           # Mesh terrain 400×400
│   ├── lake.py              # Mesh danau organik
│   ├── campfire.py          # Api unggun + partikel api
│   ├── tent.py              # Tenda, furniture, pohon
│   ├── skybox.py            # Kubus skybox 500×500
│   └── firefly.py           # Sistem partikel kunang-kunang
│
└── shaders/                 # GLSL shader programs
    ├── terrain.vert/frag    # Terrain: height-based coloring + multi-light
    ├── lake.vert/frag       # Danau: wave animation + specular reflection
    ├── campfire.vert/frag   # Partikel api: additive blending + point sprites
    ├── object.vert/frag     # Tenda & objek: vertex color + multi-light
    ├── skybox.vert/frag     # Langit: stars, moon, Fuji, Milky Way
    └── firefly.vert/frag    # Kunang-kunang: glow + point sprites
```

---

## 🛠️ Teknologi

| Library | Versi | Fungsi |
|---|---|---|
| [PyOpenGL](https://pyopengl.sourceforge.net/) | 3.1.7 | API grafika OpenGL 3.3 Core Profile |
| [Pygame](https://www.pygame.org/) | 2.5.2 | Window management & input handling |
| [PyGLM](https://github.com/Zuzu-Typ/PyGLM) | 2.8.3 | Matematika vektor & matriks (MVP) |
| [NumPy](https://numpy.org/) | 1.26.0 | Pemrosesan data vertex |

---

## 🎓 Tentang Proyek

Proyek ini dibuat sebagai tugas akhir mata kuliah **Grafika Komputer** — Semester 4.

Referensi visual utama yang digunakan adalah kawasan wisata alam **Danau Motosu** (本栖湖) di Prefektur Yamanashi, Jepang — salah satu dari lima danau yang mengelilingi Gunung Fuji. Lanskap ini juga menjadi lokasi ikonik dalam anime/manga **Yuru Camp△** (ゆるキャン△).

### Pendekatan Teknis

- **100% prosedural** — Seluruh geometri dan efek visual dibangun dari kode tanpa file model (.obj) maupun tekstur gambar
- **GPU-accelerated** — Animasi gelombang, pencahayaan, dan efek atmosfer dihitung di GLSL shader
- **Modular** — Arsitektur terpisah antara core, objects, dan shaders

---

## 👥 Tim

| Nama | Kontribusi |
|---|---|
| **Yasraf** | Terrain dan Lanskap |
| **Rifki** | Danau dan Simulasi Gelombang Air |
| **Fadhlan** | Objek Perkemahan |
| **Fadel** | Api Unggun dan Pencahayaan Dinamis |
| **Yusuf** | Skybox, Kamera, dan Atmosfer |

---

<p align="center">
  <i>🏕️ "That scenery that we saw together — I'll never forget it." — Yuru Camp△</i>
</p>