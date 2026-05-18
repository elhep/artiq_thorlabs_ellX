#!/usr/bin/env python3

import argparse
import asyncio
import sys

from sipyco import common_args
from sipyco.pc_rpc import simple_server_loop

from artiq_thorlabs_ellX.artiq_thorlabs_ellX import ThorlabsELLX
from artiq_thorlabs_ellX.artiq_thorlabs_ellX_sim import ThorlabsELLXSim


def get_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", default=None, help="Device path")
    parser.add_argument("-b", "--baudrate", default=9600, help="Baudrate of the device")
    parser.add_argument("-t", "--timeout", default=10, help="Timeout of the serial port")
    parser.add_argument(
        "--simulation",
        action="store_true",
        help="Put the driver in simulation mode",
    )
    common_args.simple_network_args(parser, 3280)
    common_args.verbosity_args(parser)
    return parser


def main():
    args = get_argparser().parse_args()
    common_args.init_logger_from_args(args)

    if not args.simulation and args.device is None:
        print(
            "You need to specify either --simulation or -d "
            "argument. Use --help for more information."
        )
        sys.exit(1)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        if args.simulation:
            dev = ThorlabsELLXSim()
        else:
            dev = ThorlabsELLX(args.device, args.baudrate, args.timeout)
        try:
            simple_server_loop(
                {"artiq_filter_driver": dev},
                common_args.bind_address_from_args(args),
                args.port,
                loop=loop,
            )
        finally:
            dev.close()
    finally:
        loop.close()


if __name__ == "__main__":
    main()