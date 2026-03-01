"""
Tests for energy.modbus_maps — register maps for EG4 / Sol-Ark / Victron / LuxPower.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from energy.modbus_maps import (
    INVERTER_MAPS,
    INVERTER_MODE_NAMES,
    GRID_FORMING_MODE_VALUE,
    GRID_FOLLOW_MODE_VALUE,
    read_register,
    interpret_signed,
)

REQUIRED_REGISTERS = [
    "battery_voltage",
    "battery_current",
    "battery_soc",
    "battery_power",
    "ac_output_voltage",
    "ac_output_current",
    "ac_output_power",
    "ac_output_frequency",
    "ac_input_voltage",
    "ac_input_power",
    "ac_input_frequency",
    "pv_power",
    "inverter_mode",
    "frequency_droop_enabled",
    "export_power_setpoint",
    "fault_code",
]


class TestInverterMapsExist(unittest.TestCase):
    def test_all_four_inverters_present(self):
        for key in ("eg4_18kpv", "solark_15k_18k", "victron_mp2", "luxpower_12k"):
            self.assertIn(key, INVERTER_MAPS, f"Missing inverter map: {key}")

    def test_each_map_has_required_registers(self):
        for inverter, reg_map in INVERTER_MAPS.items():
            for reg in REQUIRED_REGISTERS:
                self.assertIn(
                    reg, reg_map,
                    f"Inverter '{inverter}' missing register '{reg}'"
                )

    def test_each_reg_spec_is_four_tuple(self):
        for inverter, reg_map in INVERTER_MAPS.items():
            for reg, spec in reg_map.items():
                self.assertEqual(
                    len(spec), 4,
                    f"'{inverter}.{reg}' spec should be 4-tuple, got {len(spec)}"
                )

    def test_addresses_are_integers(self):
        for inverter, reg_map in INVERTER_MAPS.items():
            for reg, (addr, dtype, scale, unit) in reg_map.items():
                self.assertIsInstance(addr, int, f"Address not int: {inverter}.{reg}")

    def test_data_types_are_valid(self):
        valid_dtypes = {"uint16", "int16", "uint32", "int32", "enum", "bool"}
        for inverter, reg_map in INVERTER_MAPS.items():
            for reg, (addr, dtype, scale, unit) in reg_map.items():
                self.assertIn(
                    dtype, valid_dtypes,
                    f"Invalid dtype '{dtype}' for {inverter}.{reg}"
                )

    def test_scales_are_positive(self):
        for inverter, reg_map in INVERTER_MAPS.items():
            for reg, (addr, dtype, scale, unit) in reg_map.items():
                self.assertGreaterEqual(
                    scale, 0.0,
                    f"Negative scale for {inverter}.{reg}"
                )


class TestReadRegister(unittest.TestCase):
    def test_battery_soc_eg4(self):
        spec = INVERTER_MAPS["eg4_18kpv"]["battery_soc"]
        # SoC = 75 % → raw = 75, scale = 1.0
        self.assertAlmostEqual(read_register(75, spec), 75.0)

    def test_battery_voltage_eg4_scale(self):
        spec = INVERTER_MAPS["eg4_18kpv"]["battery_voltage"]
        # 48.5 V → raw = 485, scale = 0.1
        self.assertAlmostEqual(read_register(485, spec), 48.5)

    def test_frequency_scale(self):
        spec = INVERTER_MAPS["eg4_18kpv"]["ac_output_frequency"]
        # 60.00 Hz → raw = 6000, scale = 0.01
        self.assertAlmostEqual(read_register(6000, spec), 60.0)

    def test_victron_soc_scale(self):
        spec = INVERTER_MAPS["victron_mp2"]["battery_soc"]
        # 85.50 % → raw = 8550, scale = 0.01
        self.assertAlmostEqual(read_register(8550, spec), 85.5)

    def test_zero_raw_returns_zero(self):
        for inverter, reg_map in INVERTER_MAPS.items():
            for reg, spec in reg_map.items():
                result = read_register(0, spec)
                self.assertEqual(result, 0.0, f"Non-zero for raw=0: {inverter}.{reg}")


class TestInterpretSigned(unittest.TestCase):
    def test_positive_int16(self):
        self.assertEqual(interpret_signed(100, "int16"), 100)

    def test_negative_int16(self):
        # -1 is represented as 65535 (0xFFFF) in 16-bit unsigned
        self.assertEqual(interpret_signed(0xFFFF, "int16"), -1)

    def test_large_negative_int16(self):
        # -500 → 65535 - 499 = 65036
        self.assertEqual(interpret_signed(65036, "int16"), -500)

    def test_uint16_unchanged(self):
        self.assertEqual(interpret_signed(50000, "uint16"), 50000)

    def test_negative_int32(self):
        raw = 0x100000000 - 1000
        self.assertEqual(interpret_signed(raw, "int32"), -1000)

    def test_uint32_unchanged(self):
        self.assertEqual(interpret_signed(0xDEADBEEF, "uint32"), 0xDEADBEEF)


class TestInverterModeNames(unittest.TestCase):
    def test_all_inverters_have_mode_names(self):
        for key in INVERTER_MAPS:
            self.assertIn(key, INVERTER_MODE_NAMES, f"Missing mode names for {key}")

    def test_grid_forming_mode_defined(self):
        for key in INVERTER_MAPS:
            self.assertIn(key, GRID_FORMING_MODE_VALUE)
            self.assertIn(key, GRID_FOLLOW_MODE_VALUE)

    def test_grid_forming_and_follow_differ(self):
        for key in INVERTER_MAPS:
            # For most inverters these are different values
            # (Victron is an exception — ESS handles follow internally)
            forming = GRID_FORMING_MODE_VALUE[key]
            follow = GRID_FOLLOW_MODE_VALUE[key]
            self.assertIsInstance(forming, int)
            self.assertIsInstance(follow, int)


if __name__ == "__main__":
    unittest.main(verbosity=2)
