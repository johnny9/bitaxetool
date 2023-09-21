import argparse
import os
import sys
import tempfile

import esptool

from . import nvs_partition_gen, validation


def parse_args():
    parser = argparse.ArgumentParser(description='Flash firmware and config to a device.')

    parser.add_argument('-p', '--port',
                        type=str,
                        default=None,
                        help='The serial port to connect to.')
    parser.add_argument('-f', '--firmware',
                        type=str,
                        required=False,
                        help='The binary file to flash.')
    parser.add_argument('-c', '--config',
                        type=str,
                        required=False,
                        help='The config file to flash.')
    parser.add_argument('--validate_config',
                        '--validate',
                        action='store_true',
                        required=False,
                        default=False,
                        help='Validate the config file before flashing.')
    

    return parser.parse_args()


def flash_bitaxe(firmware_path, config_path, serial_port):
    esp_arguments = []
    if serial_port is not None:
        esp_arguments += ['--port', serial_port]
    if firmware_path is not None:
        esp_arguments += ['write_flash', '0x0', firmware_path]
        esptool.main(esp_arguments)

    if config_path is not None:
        temp_dir = tempfile.gettempdir()
        temp_config_file = 'bitaxe_config.bin'
        output_config_path = os.path.join(temp_dir, temp_config_file)
        nvs_gen_args = argparse.Namespace(input=config_path,
                                      output=temp_config_file,
                                      outdir=temp_dir,
                                      size='0x6000',
                                      version=2)
        nvs_partition_gen.generate(nvs_gen_args)

        esp_arguments = []
        if serial_port is not None:
            esp_arguments += ['--port', serial_port]
        esp_arguments += ['write_flash', '0x9000', output_config_path]
        esptool.main(esp_arguments)
        os.remove(output_config_path)


def main():
    args = parse_args()
    if args.port is not None:
        print(f"Connecting to port: {args.port}")
    print(f"Flashing firmware: {args.firmware}")
    print(f"Flashing config: {args.config}")
    if args.validate_config:
        error_msg = validation.check_validate_dependencies()
        if error_msg is not None:
            print(error_msg)
            sys.exit(1)
    
        print("Validating config...")
        validation.validate_config(args.config)
        print("Config validated successfully!")


    flash_bitaxe(args.firmware, args.config, args.port)


if __name__ == "__main__":
    main()
