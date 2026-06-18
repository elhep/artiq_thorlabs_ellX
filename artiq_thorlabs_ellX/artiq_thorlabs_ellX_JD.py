from artiq_thorlabs_ellX.artiq_thorlabs_ellX_I import ThorlabsELLXInterface, CURRENT_CURVE_T, DEVINFO_T, MOTORINFO_T
import serial
import numpy as np
from enum import Enum, IntEnum
from typing import Optional, Union
import dataclasses as dc
import struct
import time

class COMMAND_STATUS(IntEnum):
    OK = 0
    ERR_COM_TIME = 1
    ERR_MECH_TIME = 2
    ERR_CMD = 3
    ERR_VAL_RANGE = 4
    ERR_ISO = 5
    ERR_NOT_ISO = 6
    ERR_INIT = 7
    ERR_THERM = 8
    ERR_BUSY = 9
    ERR_SENSOR = 10
    ERR_MOTOR = 11
    ERR_RANGE = 12
    ERR_CURR = 13
    ERR_SERIAL = 14

class ThorlabsELLXJD(ThorlabsELLXInterface):
    def __init__(self, device: str, baudrate: int = 9600,
                 timeout: float = 10, addr: int = 0) -> None:
        self.device = device
        self.baudrate = baudrate
        self.timeout = timeout
        self.dev_addr = addr
        self.serial: Optional[serial.Serial] = None
        self.device_type = None

    def log(self, msg: str) -> None:
        print(f"[{self.__class__.__name__}] {msg}")
    
    def connect(self) -> COMMAND_STATUS:
        """Open serial connection to the controller."""
        try:
            self.serial = serial.Serial(
                port=self.device,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.log(f"Connected to {self.device}")
        except serial.SerialException:
            self.log(f"Failed to connect to {self.device}")
            return COMMAND_STATUS.ERR_SERIAL
        return COMMAND_STATUS.OK
    
    def close(self) -> None:
        """Close serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()
    
    async def req_home(self, dir: int) -> Union[str, int]:
        cmd = f"home {dir}"
        self.log(f"Sending: {cmd}")
        try:
            self.serial.write(cmd.encode("ascii", errors="ignore"))
            self.serial.readline()
            data = self.serial.readline().decode("ascii", errors="ignore")
            self.log(f"Read: {data}")
            if "PO" in data:
                return int(data[3:], 16)
        except Exception:
            self.log("Serial port error!")
            return str(COMMAND_STATUS.ERR_SERIAL)
        return data

    async def req_absolute_move(self, val: int) -> Union[str, int]:
        decoded_val = val / 398
        cmd = f"move_absolute {decoded_val:f}\n"
        self.log(f"Sending: {cmd}")
        try:
            self.serial.write(cmd.encode("ascii", errors="ignore"))
            self.serial.readline()
            data = self.serial.readline().decode("ascii", errors="ignore")
            self.log(f"Read: {data}")
            if "PO" in data:
                return int(data[3:], 16)
        except Exception:
            self.log("Serial port error!")
            return str(COMMAND_STATUS.ERR_SERIAL)
        return data
    
    async def req_relative_move(self, val: int) -> Union[str, int]:
        decoded_val = val / 398
        cmd = f"move_relative {decoded_val:f}\n"
        self.log(f"Sending: {cmd}")
        try:
            self.serial.write(cmd.encode("ascii", errors="ignore"))
            self.serial.readline()
            data = self.serial.readline().decode("ascii", errors="ignore")
            self.log(f"Read: {data}")
            if "PO" in data:
                return int(data[3:], 16)
        except Exception:
            self.log("Serial port error!")
            return str(COMMAND_STATUS.ERR_SERIAL)
        return data

    async def forward(self) -> Union[str, int]:
        cmd = f"move_fwd\n"
        self.log(f"Sending: {cmd}")
        try:
            self.serial.write(cmd.encode("ascii", errors="ignore"))
            self.serial.readline()
            data = self.serial.readline().decode("ascii", errors="ignore")
            self.log(f"Read: {data}")
            if "PO" in data:
                return int(data[3:], 16)
        except Exception:
            self.log("Serial port error!")
            return str(COMMAND_STATUS.ERR_SERIAL)
        return data
    
    async def backward(self) -> Union[str, int]:
        cmd = f"move_bwd\n"
        self.log(f"Sending: {cmd}")
        try:
            self.serial.write(cmd.encode("ascii", errors="ignore"))
            self.serial.readline()
            data = self.serial.readline().decode("ascii", errors="ignore")
            self.log(f"Read: {data}")
            if "PO" in data:
                return int(data[3:], 16)
        except Exception:
            self.log("Serial port error!")
            return str(COMMAND_STATUS.ERR_SERIAL)
        return data
    
    async def set_jog_step(self, val: int) -> str:
        decoded_val = val / 398
        cmd = f"set_jog_step {decoded_val:f}\n"
        self.log(f"Sending: {cmd}")
        try:
            self.serial.write(cmd.encode("ascii", errors="ignore"))
            self.serial.read_all()
        except Exception:
            return str(COMMAND_STATUS.ERR_SERIAL)
        return str(COMMAND_STATUS.OK)
    
    async def set_velocity(self, val: int) -> str:
        cmd = f"set_speed {val:i}\n"
        self.log(f"Sending: {cmd}")
        try:
            self.serial.write(cmd.encode("ascii", errors="ignore"))
            self.serial.read_all()
        except Exception:
            self.log("Serial port error!")
            return str(COMMAND_STATUS.ERR_SERIAL)
        return str(COMMAND_STATUS.OK)
    
    async def get_information(self) -> Union[str, DEVINFO_T]:
        return str(COMMAND_STATUS.OK.value)

    async def get_status(self) -> Union[str, int]:
        return str(COMMAND_STATUS.OK.value)

    async def req_save_user_data(self) -> str:
        return str(COMMAND_STATUS.OK.value)

    async def req_change_address(self, new_addr: int) -> str:
        return str(COMMAND_STATUS.OK.value)

    async def get_motor_info(self, motor: int) -> Union[str, MOTORINFO_T]:
        return str(COMMAND_STATUS.OK.value)

    async def set_fwp(self, motor: int, val: int) -> str:
        return str(COMMAND_STATUS.OK.value)

    async def set_bwp(self, motor: int, val: int) -> str:
        return str(COMMAND_STATUS.OK.value)

    async def req_search_freq(self, motor: int) -> str:
        return str(COMMAND_STATUS.OK.value)

    async def req_scan_current_curve(self, motor: int) -> str:
        return str(COMMAND_STATUS.OK.value)

    async def get_current_curve(self, motor: int) -> Union[str, CURRENT_CURVE_T]:
        return str(COMMAND_STATUS.OK.value)

    async def isolate_device(self, minutes: int) -> str:
        return str(COMMAND_STATUS.OK.value)

    async def set_autohoming(self, enable: int) -> Union[str, int]:
        return str(COMMAND_STATUS.OK.value)

    async def req_home_offset(self) -> Union[str, int]:
        return str(COMMAND_STATUS.OK.value)

    async def set_home_offset(self, val: int) -> str:
        return str(COMMAND_STATUS.OK.value)

    async def req_zero_position(self) -> Union[str, int]:
        return str(COMMAND_STATUS.OK.value)

    async def set_zero_position(self) -> str:
        return str(COMMAND_STATUS.OK.value)

    async def req_jog_step(self) -> Union[str, int]:
        return str(COMMAND_STATUS.OK.value)

    async def req_skip_frequency(self) -> str:
        return str(COMMAND_STATUS.OK.value)
    
    async def motion_stop(self) -> str:
        return str(COMMAND_STATUS.OK.value)
    
    async def get_position(self) -> Union[str, int]:
        return str(COMMAND_STATUS.OK.value)

    async def req_velocity(self) -> Union[str, int]:
        return str(COMMAND_STATUS.OK.value)
    
    async def group_address(self, g_addr: int) -> str:
        return str(COMMAND_STATUS.OK.value)
    
    async def optimize_motors(self) -> str:
        return str(COMMAND_STATUS.OK.value)
    
    async def clean_mechanics(self) -> str:
        return str(COMMAND_STATUS.OK.value)
    
    async def reset_factory_default(self) -> str:
        return str(COMMAND_STATUS.OK.value)
        
