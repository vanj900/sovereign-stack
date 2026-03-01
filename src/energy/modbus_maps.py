"""
modbus_maps.py — Modbus register maps for AC-coupled inverters.
================================================================
Supports:
  - EG4 18kPV
  - Sol-Ark 15K / 18K
  - Victron MultiPlus-II 5 kVA (via MK3-USB / VE.Bus-to-Modbus adapter)

Each map is a dict of logical name → (register_address, data_type, scale, unit).
data_type: "uint16" | "int16" | "uint32"
scale    : multiply raw register value by this factor to get engineering units

Usage::

    from energy.modbus_maps import INVERTER_MAPS, read_register

    regs = INVERTER_MAPS["eg4_18kpv"]
    addr, dtype, scale, unit = regs["soc"]
    # Read raw value from Modbus, then:  value = raw * scale
"""

from __future__ import annotations

from typing import Dict, Tuple

# (register_address, data_type, scale, unit)
_RegSpec = Tuple[int, str, float, str]

# ---------------------------------------------------------------------------
# EG4 18kPV  — Modbus RTU / TCP, unit ID 1 (configurable)
# Reference: EG4 18kPV Modbus Communication Protocol v1.3
# ---------------------------------------------------------------------------
EG4_18KPV: Dict[str, _RegSpec] = {
    # Battery
    "battery_voltage":         (0x0101, "uint16", 0.1,   "V"),
    "battery_current":         (0x0102, "int16",  0.1,   "A"),   # + = charging
    "battery_soc":             (0x0103, "uint16", 1.0,   "%"),
    "battery_power":           (0x0104, "int16",  1.0,   "W"),   # + = charging
    "battery_temp":            (0x0105, "int16",  0.1,   "°C"),
    # AC output
    "ac_output_voltage":       (0x0201, "uint16", 0.1,   "V"),
    "ac_output_current":       (0x0202, "uint16", 0.1,   "A"),
    "ac_output_power":         (0x0203, "uint16", 1.0,   "W"),
    "ac_output_frequency":     (0x0204, "uint16", 0.01,  "Hz"),
    # AC input (grid / bus)
    "ac_input_voltage":        (0x0205, "uint16", 0.1,   "V"),
    "ac_input_current":        (0x0206, "uint16", 0.1,   "A"),
    "ac_input_power":          (0x0207, "int16",  1.0,   "W"),   # + = importing
    "ac_input_frequency":      (0x0208, "uint16", 0.01,  "Hz"),
    # Solar / PV
    "pv_power":                (0x0300, "uint16", 1.0,   "W"),
    "pv_voltage":              (0x0301, "uint16", 0.1,   "V"),
    "pv_current":              (0x0302, "uint16", 0.1,   "A"),
    # Inverter mode / control
    "inverter_mode":           (0x0400, "uint16", 1.0,   "enum"),
    # 0=standby 1=grid-tie 2=off-grid(grid-forming) 3=grid-follow(export) 4=charge-only
    "frequency_droop_enabled": (0x0401, "uint16", 1.0,   "bool"),
    "export_power_setpoint":   (0x0402, "int16",  1.0,   "W"),   # negative = import
    "charge_current_limit":    (0x0403, "uint16", 0.1,   "A"),
    # Fault / status
    "fault_code":              (0x0500, "uint16", 1.0,   "enum"),
    "warning_code":            (0x0501, "uint16", 1.0,   "enum"),
    "runtime_hours":           (0x0502, "uint32", 1.0,   "h"),
}

# ---------------------------------------------------------------------------
# Sol-Ark 15K / 18K  — Modbus RTU / TCP, unit ID 1
# Reference: Sol-Ark 15K/18K Modbus Register List v2.0
# ---------------------------------------------------------------------------
SOLARK_15K_18K: Dict[str, _RegSpec] = {
    # Battery
    "battery_voltage":         (0x00B3, "uint16", 0.1,   "V"),
    "battery_current":         (0x00B4, "int16",  0.1,   "A"),
    "battery_soc":             (0x00B8, "uint16", 1.0,   "%"),
    "battery_power":           (0x00BE, "int16",  1.0,   "W"),
    "battery_temp":            (0x00B5, "int16",  0.1,   "°C"),
    # AC output (Load)
    "ac_output_voltage":       (0x006D, "uint16", 0.1,   "V"),
    "ac_output_current":       (0x006E, "uint16", 0.1,   "A"),
    "ac_output_power":         (0x006F, "uint16", 1.0,   "W"),
    "ac_output_frequency":     (0x007C, "uint16", 0.01,  "Hz"),
    # AC input (Grid / Utility)
    "ac_input_voltage":        (0x0096, "uint16", 0.1,   "V"),
    "ac_input_current":        (0x0097, "uint16", 0.1,   "A"),
    "ac_input_power":          (0x0098, "int16",  1.0,   "W"),
    "ac_input_frequency":      (0x0099, "uint16", 0.01,  "Hz"),
    # Solar / PV
    "pv_power":                (0x00DC, "uint16", 1.0,   "W"),
    "pv1_voltage":             (0x006A, "uint16", 0.1,   "V"),
    "pv1_current":             (0x006B, "uint16", 0.1,   "A"),
    "pv2_voltage":             (0x00D5, "uint16", 0.1,   "V"),
    "pv2_current":             (0x00D6, "uint16", 0.1,   "A"),
    # Inverter mode / control
    "inverter_mode":           (0x00F3, "uint16", 1.0,   "enum"),
    # 0=standby 1=grid-tie(grid-follow) 2=off-grid(grid-forming) 3=backup
    "frequency_droop_enabled": (0x00F4, "uint16", 1.0,   "bool"),
    "export_power_setpoint":   (0x00F5, "int16",  1.0,   "W"),
    "charge_current_limit":    (0x00F6, "uint16", 0.1,   "A"),
    # Fault / status
    "fault_code":              (0x0010, "uint16", 1.0,   "enum"),
    "warning_code":            (0x0011, "uint16", 1.0,   "enum"),
    "runtime_hours":           (0x01A0, "uint32", 1.0,   "h"),
}

# ---------------------------------------------------------------------------
# Victron MultiPlus-II 5 kVA  — VE.Bus Modbus-TCP (via CCGX / Venus OS)
# Reference: Victron Modbus-TCP register list (Venus OS ≥ 2.80)
# ---------------------------------------------------------------------------
VICTRON_MULTIPLUS2: Dict[str, _RegSpec] = {
    # Battery  (service com.victronenergy.battery, unit 288)
    "battery_voltage":         (259,  "uint16", 0.01,  "V"),
    "battery_current":         (261,  "int16",  0.1,   "A"),
    "battery_soc":             (266,  "uint16", 0.01,  "%"),   # 0–10000 → 0.00–100.00
    "battery_power":           (258,  "int16",  1.0,   "W"),
    "battery_temp":            (262,  "int16",  0.01,  "°C"),
    # AC output  (service com.victronenergy.vebus, unit 228)
    "ac_output_voltage":       (15,   "uint16", 0.1,   "V"),
    "ac_output_current":       (9,    "int16",  0.1,   "A"),
    "ac_output_power":         (100,  "int16",  1.0,   "W"),
    "ac_output_frequency":     (21,   "uint16", 0.01,  "Hz"),
    # AC input
    "ac_input_voltage":        (3,    "uint16", 0.1,   "V"),
    "ac_input_current":        (6,    "int16",  0.1,   "A"),
    "ac_input_power":          (12,   "int16",  1.0,   "W"),
    "ac_input_frequency":      (18,   "uint16", 0.01,  "Hz"),
    # Solar (service com.victronenergy.solarcharger, unit 100)
    "pv_power":                (789,  "uint16", 1.0,   "W"),
    "pv_voltage":              (776,  "uint16", 0.01,  "V"),
    "pv_current":              (778,  "int16",  0.1,   "A"),
    # Inverter mode / control (VE.Bus)
    "inverter_mode":           (33,   "uint16", 1.0,   "enum"),
    # 1=charger-only 2=inverter-only 3=on(grid-forming) 4=off 5=eco
    "frequency_droop_enabled": (37,   "uint16", 1.0,   "bool"),
    "export_power_setpoint":   (37,   "int16",  1.0,   "W"),   # reg 2703 on ESS assistant
    "charge_current_limit":    (22,   "uint16", 1.0,   "A"),
    # Fault / status
    "fault_code":              (32,   "uint16", 1.0,   "enum"),
    "warning_code":            (31,   "uint16", 1.0,   "enum"),
    "runtime_hours":           (0,    "uint32", 0.0,   "h"),   # not in std map; firmware-specific
}

# ---------------------------------------------------------------------------
# LuxPower 12K  — Modbus RTU, unit ID 1
# Reference: LuxPower LXP-12K Modbus Register Map v1.1
# ---------------------------------------------------------------------------
LUXPOWER_12K: Dict[str, _RegSpec] = {
    "battery_voltage":         (0x00A0, "uint16", 0.1,  "V"),
    "battery_current":         (0x00A1, "int16",  0.1,  "A"),
    "battery_soc":             (0x00A2, "uint16", 1.0,  "%"),
    "battery_power":           (0x00A3, "int16",  1.0,  "W"),
    "battery_temp":            (0x00A4, "int16",  0.1,  "°C"),
    "ac_output_voltage":       (0x0060, "uint16", 0.1,  "V"),
    "ac_output_current":       (0x0061, "uint16", 0.1,  "A"),
    "ac_output_power":         (0x0062, "uint16", 1.0,  "W"),
    "ac_output_frequency":     (0x0063, "uint16", 0.01, "Hz"),
    "ac_input_voltage":        (0x0070, "uint16", 0.1,  "V"),
    "ac_input_current":        (0x0071, "uint16", 0.1,  "A"),
    "ac_input_power":          (0x0072, "int16",  1.0,  "W"),
    "ac_input_frequency":      (0x0073, "uint16", 0.01, "Hz"),
    "pv_power":                (0x0080, "uint16", 1.0,  "W"),
    "pv_voltage":              (0x0081, "uint16", 0.1,  "V"),
    "pv_current":              (0x0082, "uint16", 0.1,  "A"),
    "inverter_mode":           (0x00F0, "uint16", 1.0,  "enum"),
    "frequency_droop_enabled": (0x00F1, "uint16", 1.0,  "bool"),
    "export_power_setpoint":   (0x00F2, "int16",  1.0,  "W"),
    "charge_current_limit":    (0x00F3, "uint16", 0.1,  "A"),
    "fault_code":              (0x0020, "uint16", 1.0,  "enum"),
    "warning_code":            (0x0021, "uint16", 1.0,  "enum"),
    "runtime_hours":           (0x01B0, "uint32", 1.0,  "h"),
}

# ---------------------------------------------------------------------------
# Public registry
# ---------------------------------------------------------------------------

INVERTER_MAPS: Dict[str, Dict[str, _RegSpec]] = {
    "eg4_18kpv":       EG4_18KPV,
    "solark_15k_18k":  SOLARK_15K_18K,
    "victron_mp2":     VICTRON_MULTIPLUS2,
    "luxpower_12k":    LUXPOWER_12K,
}

# Logical inverter modes mapped to a common name
INVERTER_MODE_NAMES: Dict[str, Dict[int, str]] = {
    "eg4_18kpv": {
        0: "standby",
        1: "grid_tie",
        2: "grid_forming",
        3: "grid_follow",
        4: "charge_only",
    },
    "solark_15k_18k": {
        0: "standby",
        1: "grid_follow",
        2: "grid_forming",
        3: "backup",
    },
    "victron_mp2": {
        1: "charge_only",
        2: "inverter_only",
        3: "grid_forming",
        4: "off",
        5: "eco",
    },
    "luxpower_12k": {
        0: "standby",
        1: "grid_follow",
        2: "grid_forming",
        3: "backup",
    },
}

# Modbus command values to set grid-forming vs grid-follow mode
GRID_FORMING_MODE_VALUE: Dict[str, int] = {
    "eg4_18kpv":      2,
    "solark_15k_18k": 2,
    "victron_mp2":    3,
    "luxpower_12k":   2,
}

GRID_FOLLOW_MODE_VALUE: Dict[str, int] = {
    "eg4_18kpv":      3,
    "solark_15k_18k": 1,
    "victron_mp2":    3,   # VE.Bus ESS mode handles follow internally
    "luxpower_12k":   1,
}


def read_register(
    raw_value: int,
    reg_spec: _RegSpec,
) -> float:
    """
    Convert a raw Modbus register value to an engineering-units float.

    Parameters
    ----------
    raw_value : int
        The 16-bit (or 32-bit) value read from the Modbus register.
    reg_spec  : _RegSpec
        (address, data_type, scale, unit) tuple from one of the maps above.

    Returns
    -------
    float
        raw_value * scale  (caller interprets sign for int16 before passing in)
    """
    _, _, scale, _ = reg_spec
    return raw_value * scale


def interpret_signed(raw_value: int, data_type: str) -> int:
    """
    Interpret a raw unsigned Modbus value as signed if data_type is int16/int32.

    Parameters
    ----------
    raw_value : int  — unsigned value from Modbus response (0–65535 for 16-bit)
    data_type : str  — "int16", "uint16", "int32", or "uint32"
    """
    if data_type == "int16" and raw_value >= 0x8000:
        return raw_value - 0x10000
    if data_type == "int32" and raw_value >= 0x80000000:
        return raw_value - 0x100000000
    return raw_value
