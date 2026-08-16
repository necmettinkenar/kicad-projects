#!/usr/bin/env python3
"""
Generate KiCad 10.0 project file (.kicad_pro) and PCB file (.kicad_pcb).
Uses pcbnew Python API for PCB layout.
"""
import os, sys, json

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PRO_FILE = os.path.join(PROJECT_DIR, "step-motor-controller.kicad_pro")
PCB_FILE = os.path.join(PROJECT_DIR, "step-motor-controller.kicad_pcb")

# Generate project file
project = {
    "board": {
        "3dviewports": [],
        "design_settings": {
            "defaults": {
                "board_outline_line_width": 0.1,
                "copper_line_width": 0.2,
                "copper_text_size_h": 1.5,
                "copper_text_size_v": 1.5,
                "copper_text_thickness": 0.3,
                "other_line_width": 0.15,
                "silk_line_width": 0.15,
                "silk_text_size_h": 1.0,
                "silk_text_size_v": 1.0,
                "silk_text_thickness": 0.15
            },
            "diff_pair_dimensions": [],
            "drc_exclusions": [],
            "rules": {
                "min_clearance": 0.2,
                "min_track_width": 0.2,
                "min_via_diameter": 0.4,
                "min_via_drill": 0.2
            },
            "track_widths": [0.0, 0.2, 0.25, 0.3, 0.5, 0.8],
            "via_dimensions": [
                {"diameter": 0.0, "drill": 0.0},
                {"diameter": 0.6, "drill": 0.3},
                {"diameter": 0.8, "drill": 0.4}
            ]
        },
        "ipc2581": {"dist": "", "distpn": "", "internal_id": "", "mfg": "", "mpn": ""},
        "layer_presets": [],
        "viewports": []
    },
    "boards": [],
    "cvpcb": {"equivalence_files": []},
    "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
    "meta": {"filename": "step-motor-controller.kicad_pro", "version": 3},
    "net_settings": {"classes": [
        {
            "bus_width": 12,
            "clearance": 0.2,
            "diff_pair_gap": 0.25,
            "diff_pair_via_gap": 0.25,
            "diff_pair_width": 0.2,
            "line_style": 0,
            "microvia_diameter": 0.3,
            "microvia_drill": 0.1,
            "name": "Default",
            "pcb_color": "rgba(0, 0, 0, 0.000)",
            "schematic_color": "rgba(0, 0, 0, 0.000)",
            "track_width": 0.25,
            "via_diameter": 0.6,
            "via_drill": 0.3,
            "wire_width": 6
        },
        {
            "bus_width": 12,
            "clearance": 0.5,
            "diff_pair_gap": 0.25,
            "diff_pair_via_gap": 0.25,
            "diff_pair_width": 0.2,
            "line_style": 0,
            "microvia_diameter": 0.3,
            "microvia_drill": 0.1,
            "name": "Power",
            "pcb_color": "rgba(255, 0, 0, 1.000)",
            "schematic_color": "rgba(255, 0, 0, 1.000)",
            "track_width": 0.8,
            "via_diameter": 0.8,
            "via_drill": 0.4,
            "wire_width": 6
        }
    ], "meta": {"version": 4}, "net_colors": None, "netclass_assignments": None, "netclass_patterns": [
        {"netclass": "Power", "pattern": "/+24V"},
        {"netclass": "Power", "pattern": "/+5V"},
        {"netclass": "Power", "pattern": "/+3V3"},
        {"netclass": "Power", "pattern": "/GND"}
    ]},
    "pcbnew": {
        "last_paths": {"gencad": "", "idf": "", "netlist": "", "plot": "", "pos_files": "", "specctra_dsn": "", "step": "", "svg": "", "vrml": ""},
        "page_layout_descr_file": ""
    },
    "schematic": {
        "annotate_start_num": 0,
        "bom_export_filename": "",
        "bom_fmt_presets": [],
        "bom_fmt_settings": {"field_delimiter": ",", "keep_line_breaks": False, "keep_tabs": False, "name": "CSV", "ref_delimiter": ",", "ref_range_delimiter": "", "string_delimiter": "\""},
        "bom_presets": [],
        "bom_settings": {"exclude_dnp": False, "fields_ordered": [], "filter_string": "", "group_symbols": True, "name": "Grouped By Value", "sort_asc": True, "sort_field": "Reference"},
        "connection_grid_size": 50.0,
        "drawing": {"dashed_lines_dash_length_ratio": 12.0, "dashed_lines_gap_length_ratio": 3.0, "default_line_thickness": 6.0, "default_text_size": 50.0, "field_names": [], "intersheets_ref_own_page": False, "intersheets_ref_prefix": "", "intersheets_ref_short": False, "intersheets_ref_show": False, "intersheets_ref_suffix": "", "junction_size_choice": 3, "label_size_ratio": 0.375, "operating_point_overlay_i_precision": 3, "operating_point_overlay_v_precision": 3, "pin_symbol_size": 25.0, "text_offset_ratio": 0.15},
        "legacy_lib_dir": "",
        "legacy_lib_list": [],
        "meta": {"version": 1},
        "net_format_name": "",
        "page_layout_descr_file": "",
        "plot_directory": "",
        "spice_current_sheet_as_root": False,
        "spice_external_command": "spice \"%I\"",
        "spice_model_current_sheet_as_root": True,
        "spice_save_all_currents": False,
        "spice_save_all_dissipations": False,
        "spice_save_all_voltages": False,
        "subpart_first_id": 65,
        "subpart_id_separator": 0
    },
    "sheets": [["step-motor-controller.kicad_sch", ""]],
    "text_variables": {}
}

with open(PRO_FILE, 'w', encoding='utf-8') as f:
    json.dump(project, f, indent=2)
print(f"Project file: {PRO_FILE}")

# Now generate PCB using pcbnew API
sys.path.insert(0, r'C:\Program Files\KiCad\10.0\bin\lib\site-packages')
sys.path.insert(0, r'C:\Program Files\KiCad\10.0\bin')
import pcbnew

board = pcbnew.BOARD()

# Board setup
board.SetGenerator("kicad-python-autogen")

# Set up layers - standard 2-layer board
# Layers are predefined in KiCad

# Board outline: 100mm x 80mm
edge_width = pcbnew.FromMM(0.15)
outline_pts = [
    pcbnew.VECTOR2I(pcbnew.FromMM(0), pcbnew.FromMM(0)),
    pcbnew.FromMM(100), pcbnew.FromMM(0),
    pcbnew.FromMM(100), pcbnew.FromMM(80),
    pcbnew.FromMM(0), pcbnew.FromMM(80),
]

# Draw board outline
for i in range(4):
    x1 = [0, 100, 100, 0][i]
    y1 = [0, 0, 80, 80][i]
    x2 = [100, 100, 0, 0][i]
    y2 = [0, 80, 80, 0][i]
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
    seg.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
    seg.SetWidth(edge_width)
    seg.SetLayer(pcbnew.Edge_Cuts)
    board.Add(seg)

# Component footprints - simplified placement
# Grid: 5mm spacing, components placed for minimal area
footprints = [
    # (ref, fp, x_mm, y_mm, rotation, side)
    ("J1", "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", 10, 15, 0, pcbnew.F_Cu),
    ("PS1", "Converter_ACDC:ACDC-Converter_MeanWell_IRM-20", 25, 15, 0, pcbnew.F_Cu),
    ("U1", "Package_TO_SOT_THT:TO-220-3_Vertical", 45, 15, 0, pcbnew.F_Cu),
    ("C1", "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm", 25, 30, 0, pcbnew.F_Cu),
    ("C2", "Capacitor_THT:CP_Radial_D5.0mm_P2.50mm", 45, 30, 0, pcbnew.F_Cu),
    ("U3", "RF_Module:ESP32-DevKitC", 50, 45, 0, pcbnew.F_Cu),
    ("U4", "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm", 75, 45, 0, pcbnew.F_Cu),
    ("J2", "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", 90, 45, 0, pcbnew.F_Cu),
    ("U5", "Package_DIP:DIP-16_W7.62mm", 75, 20, 0, pcbnew.F_Cu),
    ("J3", "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical", 90, 20, 0, pcbnew.F_Cu),
    ("U6", "Package_DIP:DIP-16_W7.62mm", 50, 65, 0, pcbnew.F_Cu),
    ("Q1", "Package_TO_SOT_THT:TO-92_Inline", 30, 45, 0, pcbnew.F_Cu),
    ("R11", "Resistor_SMD:R_0805_2012Metric", 35, 45, 0, pcbnew.F_Cu),
    ("R12", "Resistor_SMD:R_0805_2012Metric", 35, 50, 0, pcbnew.F_Cu),
    ("C5", "Capacitor_SMD:C_0805_2012Metric", 35, 55, 0, pcbnew.F_Cu),
    ("R1", "Resistor_SMD:R_0805_2012Metric", 10, 55, 0, pcbnew.F_Cu),
    ("R2", "Resistor_SMD:R_0805_2012Metric", 15, 55, 0, pcbnew.F_Cu),
    ("R3", "Resistor_SMD:R_0805_2012Metric", 10, 60, 0, pcbnew.F_Cu),
    ("R4", "Resistor_SMD:R_0805_2012Metric", 15, 60, 0, pcbnew.F_Cu),
    ("R5", "Resistor_SMD:R_0805_2012Metric", 10, 65, 0, pcbnew.F_Cu),
    ("R6", "Resistor_SMD:R_0805_2012Metric", 15, 65, 0, pcbnew.F_Cu),
    ("R7", "Resistor_SMD:R_0805_2012Metric", 10, 70, 0, pcbnew.F_Cu),
    ("R8", "Resistor_SMD:R_0805_2012Metric", 15, 70, 0, pcbnew.F_Cu),
    ("R9", "Resistor_SMD:R_0805_2012Metric", 10, 75, 0, pcbnew.F_Cu),
    ("R10", "Resistor_SMD:R_0805_2012Metric", 15, 75, 0, pcbnew.F_Cu),
    ("SW1", "Button_Switch_THT:SW_CuK_OS102011MA1QN1_SPDT_Angled", 5, 55, 0, pcbnew.F_Cu),
    ("SW2", "Button_Switch_THT:SW_CuK_OS102011MA1QN1_SPDT_Angled", 5, 65, 0, pcbnew.F_Cu),
    ("C3", "Capacitor_SMD:C_0805_2012Metric", 10, 50, 0, pcbnew.F_Cu),
    ("C4", "Capacitor_SMD:C_0805_2012Metric", 15, 50, 0, pcbnew.F_Cu),
    ("S1", "OptoDevice:OptoDevice_TCRT5000", 5, 45, 0, pcbnew.F_Cu),
    ("S2", "OptoDevice:OptoDevice_TCRT5000", 5, 50, 0, pcbnew.F_Cu),
    ("S3", "Sensor:Sensor_Hall_TH", 5, 70, 0, pcbnew.F_Cu),
    ("S4", "Sensor:Sensor_Hall_TH", 5, 75, 0, pcbnew.F_Cu),
    ("U2", "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", 25, 65, 0, pcbnew.F_Cu),
]

# Try to load footprints from libraries
loaded = 0
failed = []
for ref, fp_id, x, y, rot, side in footprints:
    try:
        fp = pcbnew.FootprintLoad(pcbnew.GetKicadFootprintsPath(), fp_id)
        if fp:
            fp.SetReference(ref)
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
            fp.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
            board.Add(fp)
            loaded += 1
        else:
            failed.append(ref)
    except Exception as e:
        failed.append(f"{ref}({str(e)[:40]})")

# Save PCB
board.Save(PCB_FILE)
print(f"PCB file: {PCB_FILE}")
print(f"Footprints loaded: {loaded}/{len(footprints)}")
if failed:
    print(f"Failed: {', '.join(failed[:10])}")
