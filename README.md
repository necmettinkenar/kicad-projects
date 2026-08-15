# KiCad Projects with CI/CD

Automated KiCad workflow using GitHub Actions:
- **DRC** (Design Rule Check) — PCB tasarım kural kontrolleri
- **ERC** (Electrical Rule Check) — Elektriksel kural kontrolleri
- **Gerber** — Üretim dosyaları otomatik üretimi
- **BOM** — Bill of Materials (CSV/HTML)
- **Pick & Place** — Montaj dosyası
- **3D Render** — PCB 3D görselleştirme

## Kullanım

1. KiCad projelerini `projects/` klasörüne koy
2. Commit ve push yap
3. GitHub Actions otomatik olarak DRC/ERC çalıştırır
4. Kontroller geçerse Gerber + BOM + render üretilir
5. Çıktılar Actions artifacts olarak indirilebilir

## Klasör Yapısı

```
kicad-projects/
├── .github/workflows/
│   ├── kicad-ci.yml          # DRC + ERC + Gerber + BOM
│   └── kicad-render.yml      # 3D render
├── projects/                  # KiCad projelerin buraya
├── scripts/                   # Yardımcı scriptler
└── README.md
```

## Gereksinimler

- KiCad 10.0 (lokalde)
- GitHub Actions (otomatik çalışır, ek kurulum gerekmez)
