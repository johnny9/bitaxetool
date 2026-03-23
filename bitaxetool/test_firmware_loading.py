import unittest
import csv
import os
from bitaxetool import bitaxetool  # Import the module

class TestFirmwareLoading(unittest.TestCase):
    def test_load_firmware(self):
        # Load config from CSV
        config = self.load_config('config.csv')
        
        # Use local firmware file path
        firmware_path = '/Users/usernameisjim/Desktop/bitaxetool/esp-miner.bin'
        
        # Determine serial port (hardcoded for this example)
        serial_port = '/dev/tty.usbmodem101'
        
        # Flash firmware
        result = bitaxetool.flash_bitaxe(firmware_path, config, serial_port)
        
        self.assertTrue(result, "Firmware flashing failed")

    def load_config(self, csv_path):
        config = {}
        with open(csv_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                config[row['key']] = row['value']
        return config

    # Removed download_firmware method

if __name__ == '__main__':
    unittest.main()