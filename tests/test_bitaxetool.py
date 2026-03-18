import importlib
import os
import sys
import types
import unittest
from unittest import mock


def import_module_under_test():
    sys.modules.pop("bitaxetool.bitaxetool", None)
    sys.modules.pop("bitaxetool.nvs_partition_gen", None)
    sys.modules.pop("bitaxetool.validation", None)
    fake_esptool = mock.Mock()
    fake_nvs_partition_gen = types.ModuleType("bitaxetool.nvs_partition_gen")
    fake_nvs_partition_gen.generate = mock.Mock()
    fake_validation = types.ModuleType("bitaxetool.validation")
    fake_validation.check_validate_dependencies = mock.Mock(return_value=None)
    fake_validation.validate_config = mock.Mock()
    with mock.patch.dict(
        sys.modules,
        {
            "esptool": fake_esptool,
            "bitaxetool.nvs_partition_gen": fake_nvs_partition_gen,
            "bitaxetool.validation": fake_validation,
        },
    ):
        module = importlib.import_module("bitaxetool.bitaxetool")
    return module, fake_esptool


class FlashBitaxeTests(unittest.TestCase):
    def test_flashes_firmware_with_esptool_v5_command_name(self):
        module, fake_esptool = import_module_under_test()

        module.flash_bitaxe("firmware.bin", None, "/dev/ttyUSB0")

        fake_esptool.main.assert_called_once_with(
            ["--port", "/dev/ttyUSB0", "write-flash", "0x0", "firmware.bin"]
        )

    def test_generates_temp_config_and_cleans_it_up(self):
        module, fake_esptool = import_module_under_test()

        def fake_generate(args):
            output_path = os.path.join(args.outdir, args.output)
            with open(output_path, "wb") as output_file:
                output_file.write(b"config")

        with mock.patch.object(
            module.nvs_partition_gen, "generate", side_effect=fake_generate
        ) as generate_mock:
            module.flash_bitaxe(None, "config.csv", None)

        generate_mock.assert_called_once()
        flashed_args = fake_esptool.main.call_args.args[0]
        self.assertEqual(flashed_args[:2], ["write-flash", "0x9000"])
        self.assertEqual(os.path.basename(flashed_args[2]), "bitaxe_config.bin")
        self.assertFalse(os.path.exists(flashed_args[2]))


if __name__ == "__main__":
    unittest.main()
