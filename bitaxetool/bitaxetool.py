from . import nvs_partition_gen

import esptool

import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Flash firmware and config to a device.')

    parser.add_argument('--port', 
                        type=str, 
                        default=None, 
                        help='The serial port to connect to.')
    parser.add_argument('--firmware', 
                        type=str, 
                        required=True, 
                        help='The binary file to flash.')
    parser.add_argument('--config', 
                        type=str, 
                        required=True, 
                        help='The config file to flash.')

    return parser.parse_args()


def flash_bitaxe(firmware_path, config_path, serial_port):
    nvs_gen_args = argparse.Namespace(input=config_path,
                                      output='config.bin',
                                      outdir='/tmp',
                                      size='0x6000',
                                      version=2)
    nvs_partition_gen.generate(nvs_gen_args)

    esp_arguments = []
    if serial_port is not None:
        esp_arguments += ['--port', serial_port]
    esp_arguments += ['write_flash', '0x9000', '/tmp/config.bin', '0x10000', firmware_path]
    esptool.main(esp_arguments)


def main():
    args = parse_args()
    if args.port is not None:
        print(f"Connecting to port: {args.port}")
    print(f"Flashing firmware: {args.firmware}")
    print(f"Flashing config: {args.config}")
    flash_bitaxe(args.firmware, args.config, args.port)


if __name__ == "__main__":
    main()
