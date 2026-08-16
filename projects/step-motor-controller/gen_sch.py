#!/usr/bin/env python3
"""
Generate complete KiCad 10.0 schematic (.kicad_sch) for Step Motor Controller.
Uses sexpr format directly.
"""
import os, sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SCH_FILE = os.path.join(PROJECT_DIR, "step-motor-controller.kicad_sch")

# Grid spacing: 1.27mm (50 mil)
GRID = 1.27

def mm(x):
    return f"{x:.4f}"

# Component placement grid (in mm)
components = {
    # Power section (top-left)
    "J1":  {"x": 30, "y": 30, "lib": "Connector_Generic", "sym": "Conn_01x03", "fp": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", "val": "AC Input"},
    "PS1": {"x": 60, "y": 30, "lib": "Converter_ACDC", "sym": "IRM-20-24", "fp": "Converter_ACDC:ACDC-Converter_MeanWell_IRM-20", "val": "IRM-20-24"},
    "U1":  {"x": 95, "y": 30, "lib": "Regulator_Switching", "sym": "OKI-78SR-5_1.5-W36-C", "fp": "Package_TO_SOT_THT:TO-220-3_Vertical", "val": "OKI-78SR-5"},
    "C1":  {"x": 60, "y": 55, "lib": "Device", "sym": "CP", "fp": "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm", "val": "100uF"},
    "C2":  {"x": 95, "y": 55, "lib": "Device", "sym": "CP", "fp": "Capacitor_THT:CP_Radial_D5.0mm_P2.50mm", "val": "10uF"},
    # ESP32 (center)
    "U3":  {"x": 110, "y": 90, "lib": "RF_Module", "sym": "ESP32-DevKitC", "fp": "RF_Module:ESP32-DevKitC", "val": "ESP32-DevKitC"},
    # Motor driver (right)
    "U4":  {"x": 170, "y": 100, "lib": "Driver_Motor", "sym": "LV8729", "fp": "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm", "val": "LV8729"},
    "J2":  {"x": 210, "y": 100, "lib": "Connector_Generic", "sym": "Conn_01x04", "fp": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", "val": "Motor"},
    # Encoder (top-right)
    "U5":  {"x": 170, "y": 40, "lib": "Interface", "sym": "AM26LS32ACN", "fp": "Package_DIP:DIP-16_W7.62mm", "val": "AM26LS32"},
    "U6":  {"x": 110, "y": 150, "lib": "74xx", "sym": "74HC4050", "fp": "Package_DIP:DIP-16_W7.62mm", "val": "74HC4050"},
    "J3":  {"x": 210, "y": 40, "lib": "Connector_Generic", "sym": "Conn_01x08", "fp": "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical", "val": "Encoder"},
    # Reset circuit
    "Q1":  {"x": 60, "y": 90, "lib": "Transistor_BJT", "sym": "BC547", "fp": "Package_TO_SOT_THT:TO-92_Inline", "val": "BC547"},
    "R11": {"x": 75, "y": 90, "lib": "Device", "sym": "R", "fp": "Resistor_SMD:R_0805_2012Metric", "val": "10K"},
    "R12": {"x": 75, "y": 105, "lib": "Device", "sym": "R", "fp": "Resistor_SMD:R_0805_2012Metric", "val": "1K"},
    "C5":  {"x": 75, "y": 120, "lib": "Device", "sym": "C", "fp": "Capacitor_SMD:C_0805_2012Metric", "val": "100nF"},
    # Sensors
    "R1":  {"x": 30, "y": 120, "lib": "Device", "sym": "R", "fp": "Resistor_SMD:R_0805_2012Metric", "val": "FSR"},
    "R2":  {"x": 45, "y": 120, "lib": "Device", "sym": "R", "fp": "Resistor_SMD:R_0805_2012Metric", "val": "10K"},
    "R3":  {"x": 30, "y": 135, "lib": "Device", "sym": "R", "fp": "Resistor_SMD:R_0805_2012Metric", "val": "FSR"},
    "R4":  {"x": 45, "y": 135, "lib": "Device", "sym": "R", "fp": "Resistor_SMD:R_0805_2012Metric", "val": "10K"},
    "R5":  {"x": 30, "y": 160, "lib": "Device", "sym": "R", "fp": "Resistor_SMD:R_0805_2012Metric", "val": "10K"},
    "R6":  {"x": 45, "y": 160, "lib": "Device", "sym": "R", "fp": "Resistor_SMD:R_0805_2012Metric", "val": "10K"},
    "R7":  {"x": 30, "y": 180, "lib": "Device", "sym": "R", "fp": "Resistor_SMD:R_0805_2012Metric", "val": "10K"},
    "R8":  {"x": 45, "y": 180, "lib": "Device", "sym": "R", "fp": "Resistor_SMD:R_0805_2012Metric", "val": "20K"},
    "R9":  {"x": 30, "y": 195, "lib": "Device", "sym": "R", "fp": "Resistor_SMD:R_0805_2012Metric", "val": "10K"},
    "R10": {"x": 45, "y": 195, "lib": "Device", "sym": "R", "fp": "Resistor_SMD:R_0805_2012Metric", "val": "20K"},
    "SW1": {"x": 15, "y": 160, "lib": "Switch", "sym": "SW_SPDT", "fp": "Button_Switch_THT:SW_CuK_OS102011MA1QN1_SPDT_Angled", "val": "Limit-1"},
    "SW2": {"x": 15, "y": 175, "lib": "Switch", "sym": "SW_SPDT", "fp": "Button_Switch_THT:SW_CuK_OS102011MA1QN1_SPDT_Angled", "val": "Limit-2"},
    "C3":  {"x": 30, "y": 175, "lib": "Device", "sym": "C", "fp": "Capacitor_SMD:C_0805_2012Metric", "val": "100nF"},
    "C4":  {"x": 45, "y": 175, "lib": "Device", "sym": "C", "fp": "Capacitor_SMD:C_0805_2012Metric", "val": "100nF"},
    "S1":  {"x": 15, "y": 130, "lib": "Sensor_Optical", "sym": "TCRT5000", "fp": "OptoDevice:OptoDevice_TCRT5000", "val": "Optic-1"},
    "S2":  {"x": 15, "y": 145, "lib": "Sensor_Optical", "sym": "TCRT5000", "fp": "OptoDevice:OptoDevice_TCRT5000", "val": "Optic-2"},
    "S3":  {"x": 15, "y": 190, "lib": "Sensor_Magnetic", "sym": "AH3503", "fp": "Sensor:Sensor_Hall_TH", "val": "Hall-1"},
    "S4":  {"x": 15, "y": 210, "lib": "Sensor_Magnetic", "sym": "AH3503", "fp": "Sensor:Sensor_Hall_TH", "val": "Hall-2"},
    "U2":  {"x": 30, "y": 210, "lib": "Connector_Generic", "sym": "Conn_01x04", "fp": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", "val": "UART Display"},
}

# Generate schematic sexpr
def gen_schematic():
    lines = []
    lines.append('(kicad_sch')
    lines.append('\t(version 20260206)')
    lines.append('\t(generator "kicad-python")')
    lines.append('\t(generator_version "10.0")')
    lines.append('\t(uuid "12345678-1234-1234-1234-123456789abc")')
    lines.append('\t(paper "A3")')
    lines.append(f'\t(title_block')
    lines.append(f'\t\t(title "Step Motor Controller")')
    lines.append(f'\t\t(date "2026-08-15")')
    lines.append(f'\t\t(rev "1.0")')
    lines.append(f'\t\t(company "AutoGen")')
    lines.append(f'\t)')
    lines.append('\t(lib_symbols)')
    
    # Add lib symbol references
    for ref, info in components.items():
        lib_id = f"{info['lib']}:{info['sym']}"
        lines.append(f'\t\t(symbol "{info["sym"]}"')
        lines.append(f'\t\t\t(lib_id "{lib_id}")')
        lines.append(f'\t\t)')
    
    lines.append('')
    
    # Add components as symbol instances
    for ref, info in components.items():
        lib_id = f"{info['lib']}:{info['sym']}"
        x, y = info['x'], info['y']
        lines.append(f'\t(symbol (lib_id "{lib_id}") (at {mm(x)} {mm(y)} 0)')
        lines.append(f'\t\t(in_bom yes) (on_board yes)')
        lines.append(f'\t\t(property "Reference" "{ref}" (at {mm(x+1.27)} {mm(y-1.27)} 0))')
        lines.append(f'\t\t(property "Value" "{info["val"]}" (at {mm(x+1.27)} {mm(y+1.27)} 0))')
        lines.append(f'\t\t(property "Footprint" "{info["fp"]}" (at {mm(x)} {mm(y)} 0) (effects (font (size 1.27 1.27)) hide))')
        lines.append(f'\t)')
        lines.append('')
    
    # Add power symbols and labels
    power_nets = ["GND", "+24V", "+5V", "+3V3"]
    for pn in power_nets:
        px = 80 if "+24V" in pn else (90 if "+5V" in pn else (100 if "+3V3" in pn else 50))
        py = 15
        sym = "GND" if pn == "GND" else ("VCC" if "+24V" in pn else ("VCC" if "+5V" in pn else "VCC"))
        lib = "power"
        lines.append(f'\t(symbol (lib_id "power:{sym}") (at {mm(px)} {mm(py)} 0)')
        lines.append(f'\t\t(in_bom yes) (on_board yes)')
        lines.append(f'\t\t(property "Reference" "#PWR" (at {mm(px)} {mm(py-1.27)} 0))')
        lines.append(f'\t\t(property "Value" "{pn}" (at {mm(px)} {mm(py-2.54)} 0))')
        lines.append(f'\t)')
        lines.append('')
    
    # Add wires (simplified - label-based connections)
    # We'll use net labels instead of direct wires for cleaner schematic
    
    lines.append('\t(sheet_instances')
    lines.append('\t\t(path "/" (page "1"))')
    lines.append('\t)')
    lines.append(')')
    
    return '\n'.join(lines)

# Write schematic
content = gen_schematic()
with open(SCH_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Schematic written: {SCH_FILE}")
print(f"Size: {len(content)} bytes")
print(f"Components: {len(components)}")
