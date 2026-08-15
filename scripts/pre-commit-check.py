#!/usr/bin/env python3
"""
Pre-commit hook: KiCad DRC + ERC hızlı kontrol
Kullanım: python scripts/pre-commit-check.py projects/proje/proje.kicad_pcb
"""
import subprocess
import sys
import os
import glob

def run_kicad_cli(args):
    """KiCad CLI çalıştır ve çıktıyı döndür"""
    kicad_cli = os.environ.get("KICAD_CLI", "kicad-cli")
    try:
        result = subprocess.run(
            [kicad_cli] + args,
            capture_output=True, text=True, timeout=120
        )
        return result.returncode, result.stdout + result.stderr
    except FileNotFoundError:
        print("⚠ kicad-cli bulunamadı. KiCad kurulu mu?")
        return 0, ""
    except subprocess.TimeoutExpired:
        print("⚠ Zaman aşımı")
        return 1, "timeout"

def main():
    # Find all .kicad_pcb and .kicad_sch in projects/
    pcb_files = glob.glob("projects/**/*.kicad_pcb", recursive=True)
    sch_files = glob.glob("projects/**/*.kicad_sch", recursive=True)
    
    if not pcb_files and not sch_files:
        print("ℹ KiCad proje dosyası bulunamadı.")
        return 0
    
    errors = 0
    
    # ERC
    for sch in sch_files:
        print(f"\n=== ERC: {sch} ===")
        code, output = run_kicad_cli(["sch", "erc", "--output", "-", sch])
        if output.strip():
            print(output)
            if "error" in output.lower():
                errors += 1
    
    # DRC
    for pcb in pcb_files:
        print(f"\n=== DRC: {pcb} ===")
        code, output = run_kicad_cli(["pcb", "drc", "--output", "-", pcb])
        if output.strip():
            print(output)
            if "error" in output.lower():
                errors += 1
    
    if errors:
        print(f"\n❌ {errors} hata bulundu!")
        return 1
    else:
        print("\n✅ Kontroller temiz.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
