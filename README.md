# KiCad projects with automated CI/CD using KiBot

GitHub Actions + KiBot ile otomatik:
- **DRC** (Design Rule Check) — PCB tasarım kural kontrolleri
- **ERC** (Electrical Rule Check) — Elektriksel kural kontrolleri
- **Gerber** — Üretim dosyaları (Gerber X2 + job file)
- **Drill** — Excellon drill + IPC-2581
- **BOM** — Bill of Materials (HTML + CSV)
- **Pick & Place** — Montaj dosyası (CSV, mm)
- **PCB PDF** — Renkli PCB layout çıktısı
- **Şematik PDF** — Şematik çıktısı
- **3D Render** — SVG formatında 3D görselleştirme
- **3D STEP** — STEP formatında 3D model

## Kullanım

1. KiCad projelerini `projects/` klasörüne koy
2. Commit ve push yap
3. GitHub Actions KiBot ile DRC/ERC çalıştırır
4. main branch'ine push'ta tüm üretim dosyaları otomatik üretilir
5. Çıktılar Actions artifacts olarak indirilir

## Klasör Yapısı

```
kicad-projects/
├── .github/workflows/
│   └── kicad-ci.yml           # KiBot CI/CD pipeline
├── kibot.yml                   # KiBot yapılandırması
├── projects/                   # KiCad projelerin buraya
├── scripts/
│   └── pre-commit-check.py    # Lokal pre-commit DRC/ERC
└── README.md
```

## Lokalde KiBot Kullanımı

```bash
# KiBot kurulu (KiCad Python ile)
"C:\Program Files\KiCad\10.0\bin\Scripts\kibot.exe" -b projects/proje/proje.kicad_pcb -e projects/proje/proje.kicad_sch -c kibot.yml -d output -v
```

## CI/CD Pipeline

| Aşama | Tetikleyici | Çıktı |
|-------|-------------|-------|
| DRC + ERC | Her push/PR | Hata raporu (txt) |
| Manufacturing | main branch push | Gerber, Drill, BOM, PnP |
| Documentation | main branch push | PCB PDF, Şematik PDF, 3D SVG |
| 3D Model | main branch push | STEP dosyası |

## Gereksinimler

- KiCad 10.0 (lokalde)
- GitHub Actions (otomatik, ek kurulum yok)
- KiBot 1.9.1 (CI container'da hazır, lokalde KiCad Python ile)
