# projects/

KiCad projelerini bu klasöre koy.

Her proje kendi alt klasöründe olmalı:

```
projects/
├── led-blinker/
│   ├── led-blinker.kicad_pro
│   ├── led-blinker.kicad_sch
│   ├── led-blinker.kicad_pcb
│   └── led-blinker.kicad_prl
├── power-supply/
│   ├── power-supply.kicad_pro
│   ├── power-supply.kicad_sch
│   └── power-supply.kicad_pcb
```

Bir proje eklediğinde commit + push yap, CI/CD otomatik çalışır.
