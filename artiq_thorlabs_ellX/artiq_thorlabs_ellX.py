from artiq_thorlabs_ellX.artiq_thorlabs_ellX_I import ThorlabsELLXInterface, CURRENT_CURVE_T, DEVINFO_T, MOTORINFO_T
import serial
import numpy as np
from enum import Enum, IntEnum
from typing import Optional, Union
import dataclasses as dc
import struct

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

@dc.dataclass
class DEV_DESC:
    name: str
    dev_id: int
    motor_count: int

class COMMAND_WORDS(Enum):
    REQ_INFO = "in"
    GET_INFO = "IN"

    REQ_STATUS = "gs"
    GET_STATUS = "GS"

    REQ_SAVE_USER_DATA = "us"

    REQ_CHANGE_ADDRESS = "ca"

    REQ_M1_INFO = "i1"
    GET_M1_INFO = "I1"
    SET_FWP_M1 = "f1"
    SET_BWP_M1 = "b1"
    REQ_SEARCH_FREQ_M1 = "s1"
    REQ_SCAN_CURRENT_M1 = "c1"
    GET_CURRENT_M1 = "C1"

    REQ_M2_INFO = "i2"
    GET_M2_INFO = "I2"
    SET_FWP_M2 = "f2"
    SET_BWP_M2 = "b2"
    REQ_SEARCH_FREQ_M2 = "s2"
    REQ_SCAN_CURRENT_M2 = "c2"
    GET_CURRENT_M2 = "C2"

    ISOLATE_MINUTES = "is"

    REQ_HOME = "ho"
    
    SET_AUTO_HOMING = "ah"
    
    REQ_MOVE_ABS = "ma"
    REQ_MOVE_REL = "mr"
    
    REQ_HOME_OFFSET = "go"
    GET_HOME_OFFSET = "HO"
    SET_HOME_OFFSET = "so"

    REQ_ZERO_POS = "gz"
    GET_ZERO_POS = "ZO"
    SET_ZERO_POS = "sz"

    REQ_JOG_STEP_SIZE = "gj"
    GET_JOG_STEP_SIZE = "GJ"
    SET_JOB_STEP_SIZE = "sj"

    FORWARD = "fw"
    BACKWARD = "bw"

    REQ_SKIP_FREQ = "sk"
    REQ_MOTION_STOP = "st"

    REQ_POSITION = "gp"
    GET_POSITION = "PO"

    REQ_VELOCITY = "gv"
    GET_VELOCITY = "GV"
    SET_VELOCITY = "sv"

    GET_BUTTON_STATUS = "BS"
    GET_BUTTON_POSITION = "BO"

    GROUP_ADDRESS = "ga"
    OPTIMIZE_MOTORS = "om"
    CLEAN_MECHANICS = "cm"
    FACTORY_DEFAULT = "rd"

resp_lenghts = {
    COMMAND_WORDS.GET_INFO: 30,
    COMMAND_WORDS.GET_STATUS: 2,
    COMMAND_WORDS.GET_M1_INFO: 22,
    COMMAND_WORDS.GET_CURRENT_M1: 522,
    COMMAND_WORDS.GET_M2_INFO: 22,
    COMMAND_WORDS.GET_CURRENT_M2: 522,
    COMMAND_WORDS.GET_HOME_OFFSET: 8,
    COMMAND_WORDS.GET_ZERO_POS: 8,
    COMMAND_WORDS.GET_JOG_STEP_SIZE: 8,
    COMMAND_WORDS.GET_POSITION: 8,
    COMMAND_WORDS.GET_VELOCITY: 2,
    COMMAND_WORDS.GET_BUTTON_STATUS: 2,
    COMMAND_WORDS.GET_BUTTON_POSITION: 8,
}

cmd_responses = {
    COMMAND_WORDS.REQ_INFO: COMMAND_WORDS.GET_INFO,
    COMMAND_WORDS.REQ_STATUS: COMMAND_WORDS.GET_STATUS,
    COMMAND_WORDS.REQ_SAVE_USER_DATA: COMMAND_WORDS.GET_STATUS,
    COMMAND_WORDS.REQ_CHANGE_ADDRESS: COMMAND_WORDS.GET_STATUS,
    COMMAND_WORDS.REQ_M1_INFO: COMMAND_WORDS.GET_M1_INFO,
    COMMAND_WORDS.SET_FWP_M1: COMMAND_WORDS.GET_STATUS,
    COMMAND_WORDS.SET_BWP_M1: COMMAND_WORDS.GET_STATUS,
    COMMAND_WORDS.REQ_SEARCH_FREQ_M1: COMMAND_WORDS.GET_STATUS,
    COMMAND_WORDS.REQ_SCAN_CURRENT_M1: COMMAND_WORDS.GET_STATUS,
    COMMAND_WORDS.REQ_M2_INFO: COMMAND_WORDS.GET_M2_INFO,
    COMMAND_WORDS.SET_FWP_M2: COMMAND_WORDS.GET_STATUS,
    COMMAND_WORDS.SET_BWP_M2: COMMAND_WORDS.GET_STATUS,
    COMMAND_WORDS.REQ_SEARCH_FREQ_M2: COMMAND_WORDS.GET_STATUS,
    COMMAND_WORDS.REQ_SCAN_CURRENT_M2: COMMAND_WORDS.GET_STATUS,
    COMMAND_WORDS.REQ_HOME: [COMMAND_WORDS.GET_STATUS, COMMAND_WORDS.GET_POSITION],
    COMMAND_WORDS.SET_AUTO_HOMING: [COMMAND_WORDS.GET_STATUS, COMMAND_WORDS.GET_POSITION],
    COMMAND_WORDS.REQ_MOVE_ABS: [COMMAND_WORDS.GET_STATUS, COMMAND_WORDS.GET_POSITION],
    COMMAND_WORDS.REQ_MOVE_REL: [COMMAND_WORDS.GET_STATUS, COMMAND_WORDS.GET_POSITION],
    COMMAND_WORDS.REQ_HOME_OFFSET: COMMAND_WORDS.GET_HOME_OFFSET,
    COMMAND_WORDS.REQ_ZERO_POS: COMMAND_WORDS.GET_ZERO_POS,
    COMMAND_WORDS.REQ_JOG_STEP_SIZE: COMMAND_WORDS.GET_JOG_STEP_SIZE,
    COMMAND_WORDS.FORWARD: [COMMAND_WORDS.GET_STATUS, COMMAND_WORDS.GET_POSITION],
    COMMAND_WORDS.BACKWARD: [COMMAND_WORDS.GET_STATUS, COMMAND_WORDS.GET_POSITION],
    COMMAND_WORDS.REQ_SKIP_FREQ: COMMAND_WORDS.GET_STATUS,
    COMMAND_WORDS.REQ_MOTION_STOP: COMMAND_WORDS.GET_STATUS,
    COMMAND_WORDS.REQ_POSITION: COMMAND_WORDS.GET_POSITION,
    COMMAND_WORDS.REQ_VELOCITY: COMMAND_WORDS.GET_VELOCITY,
    COMMAND_WORDS.GROUP_ADDRESS: COMMAND_WORDS.GET_STATUS,
    COMMAND_WORDS.OPTIMIZE_MOTORS: COMMAND_WORDS.GET_STATUS,
    COMMAND_WORDS.CLEAN_MECHANICS: COMMAND_WORDS.GET_STATUS,
}


class ThorlabsELLX(ThorlabsELLXInterface):
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
    
    def _send_cmd(self, cmd: COMMAND_WORDS, data: str = "") -> COMMAND_STATUS:
        if self.serial is None:
            if self.connect() == COMMAND_STATUS.ERR_SERIAL:
                return COMMAND_STATUS.ERR_SERIAL
        full_cmd = f"{self.dev_addr}{cmd.value}{data}"
        self.log(f"Write command: {full_cmd}")
        try:
            self.serial.read_all()
            self.serial.write(full_cmd.encode("ascii", errors="ignore"))
        except:
            self.log("Serial device caused an exception!")
            return COMMAND_STATUS.ERR_SERIAL
        
        return COMMAND_STATUS.OK
    
    def _read_resp(self, cmd: Union[COMMAND_WORDS, list[COMMAND_WORDS]]) -> Union[str, COMMAND_STATUS]:
        if self.serial is None:
            if self.connect() == COMMAND_STATUS.ERR_SERIAL:
                return COMMAND_STATUS.ERR_SERIAL
        if type(cmd) == COMMAND_WORDS:
            cmd = [cmd]
        try:
            header = self.serial.read(3)
            self.log(f"Received header: {header.decode()}")
            if int(header.decode()[0]) != self.dev_addr:
                return COMMAND_STATUS.ERR_SERIAL
            for c in cmd:
                if c.value.encode("ascii") == header[1:3] and c in resp_lenghts.keys():
                    data = self.serial.read(resp_lenghts[c]+2).decode("ascii", errors="ignore").strip()
                    return data
        except serial.SerialException:
            self.log(f"Failed to connect to {self.device}")
            return COMMAND_STATUS.ERR_SERIAL
        return COMMAND_STATUS.ERR_CMD
    
    def _parse_int(self, data: str) -> int:
        return struct.unpack(">i", bytes.fromhex(data))[0]
    
    async def get_information(self) -> Union[str, DEVINFO_T]:
        status = self._send_cmd(COMMAND_WORDS.REQ_INFO)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.REQ_INFO])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        parsed = struct.unpack(">BIHBBHI", bytes.fromhex(data))
        return DEVINFO_T(parsed)

    async def get_status(self) -> Union[str, int]:
        status = self._send_cmd(COMMAND_WORDS.REQ_STATUS)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.REQ_STATUS])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        return int(data, 16)

    async def req_save_user_data(self) -> str:
        status = self._send_cmd(COMMAND_WORDS.REQ_SAVE_USER_DATA)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.REQ_SAVE_USER_DATA])
        if type(data) == COMMAND_STATUS:
            return str(data.value)

    async def req_change_address(self, new_addr: int) -> str:
        data = f"{new_addr:X}"
        status = self._send_cmd(COMMAND_WORDS.REQ_CHANGE_ADDRESS, data[0])
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        self.dev_addr = new_addr
        data = self._read_resp(cmd_responses[COMMAND_WORDS.REQ_CHANGE_ADDRESS])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        return data
        # data = self._read_resp(cmd_responses[COMMAND_WORDS.REQ_CHANGE_ADDRESS])

    async def get_motor_info(self, motor: int) -> Union[str, MOTORINFO_T]:
        cmd = COMMAND_WORDS.REQ_M1_INFO if motor == 1 else COMMAND_WORDS.REQ_M2_INFO
        status = self._send_cmd(cmd)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[cmd])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        parsed = struct.unpack(">BHHHHH", bytes.fromhex(data))
        return (parsed[0] & 0xF, parsed[1], parsed[4], parsed[5])

    async def set_fwp(self, motor: int, val: int) -> str:
        cmd = COMMAND_WORDS.SET_FWP_M1 if motor == 1 else COMMAND_WORDS.SET_FWP_M2
        data = struct.pack(">H", val).hex().upper()
        status = self._send_cmd(cmd, data)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[cmd])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        return data

    async def set_bwp(self, motor: int, val: int) -> str:
        cmd = COMMAND_WORDS.SET_BWP_M1 if motor == 1 else COMMAND_WORDS.SET_BWP_M2
        data = struct.pack(">H", val).hex().upper()
        status = self._send_cmd(cmd, data)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[cmd])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        return data

    async def req_search_freq(self, motor: int) -> str:
        cmd = COMMAND_WORDS.REQ_SEARCH_FREQ_M1 if motor == 1 else COMMAND_WORDS.REQ_SEARCH_FREQ_M2
        status = self._send_cmd(cmd)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[cmd])
        if type(data) == COMMAND_STATUS:
            return str(data.value)

    async def req_scan_current_curve(self, motor: int) -> str:
        cmd = COMMAND_WORDS.REQ_SCAN_CURRENT_M1 if motor == 1 else COMMAND_WORDS.REQ_SCAN_CURRENT_M2
        status = self._send_cmd(cmd)

    async def get_current_curve(self, motor: int) -> Union[str, CURRENT_CURVE_T]:
        pass # TODO Figure out how it works

    async def isolate_device(self, minutes: int) -> str:
        data = struct.pack(">B", minutes).hex().upper()
        status = self._send_cmd(COMMAND_WORDS.ISOLATE_MINUTES, data)
        return str(status.value)


    async def req_home(self, dir: int) -> Union[str, int]:
        data = str(dir)
        status = self._send_cmd(COMMAND_WORDS.REQ_HOME, data)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.REQ_HOME])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        if len(data) == 2:
            return data
        return int(data, 16)

    async def set_autohoming(self, enable: int) -> Union[str, int]:
        data = str(enable)
        status = self._send_cmd(COMMAND_WORDS.SET_AUTO_HOMING, data)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.SET_AUTO_HOMING])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        if len(data) == 2:
            return data
        return int(data, 16)

    async def req_absolute_move(self, val: int) -> Union[str, int]:
        data = struct.pack(">i", val).hex().upper()
        status = self._send_cmd(COMMAND_WORDS.REQ_MOVE_ABS, data)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.REQ_MOVE_ABS])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        if len(data) == 2:
            return data
        return int(data, 16)

    async def req_relative_move(self, val: int) -> Union[str, int]:
        data = struct.pack(">i", val).hex().upper()
        status = self._send_cmd(COMMAND_WORDS.REQ_MOVE_REL, data)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.REQ_MOVE_REL])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        if len(data) == 2:
            return data
        return int(data, 16)

    async def req_home_offset(self) -> Union[str, int]:
        status = self._send_cmd(COMMAND_WORDS.REQ_HOME_OFFSET)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.REQ_HOME_OFFSET])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        return self._parse_int(data)

    async def set_home_offset(self, val: int) -> str:
        data = struct.pack(">I", val).hex().upper()
        status = self._send_cmd(COMMAND_WORDS.SET_HOME_OFFSET, data)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        return status

    async def req_zero_position(self) -> Union[str, int]:
        status = self._send_cmd(COMMAND_WORDS.REQ_ZERO_POS)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.REQ_ZERO_POS])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        return self._parse_int(data)

    async def set_zero_position(self) -> str:
        status = self._send_cmd(COMMAND_WORDS.SET_ZERO_POS)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        return status

    async def req_jog_step(self) -> Union[str, int]:
        status = self._send_cmd(COMMAND_WORDS.REQ_JOG_STEP_SIZE)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.REQ_JOG_STEP_SIZE])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        return self._parse_int(data)

    async def set_jog_step(self, val: int) -> str:
        data = struct.pack(">I", val).hex().upper()
        status = self._send_cmd(COMMAND_WORDS.SET_JOB_STEP_SIZE, data)
        return str(status.value)

    async def forward(self) -> Union[str, int]:
        status = self._send_cmd(COMMAND_WORDS.FORWARD)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.FORWARD])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        if len(data) == 2:
            return data
        return self._parse_int(data)

    async def backward(self) -> Union[str, int]:
        status = self._send_cmd(COMMAND_WORDS.BACKWARD)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.BACKWARD])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        if len(data) == 2:
            return data
        return self._parse_int(data)

    async def req_skip_frequency(self) -> str:
        status = self._send_cmd(COMMAND_WORDS.REQ_SKIP_FREQ)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.REQ_SKIP_FREQ])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        return data
    
    async def motion_stop(self) -> str:
        status = self._send_cmd(COMMAND_WORDS.REQ_MOTION_STOP)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.REQ_MOTION_STOP])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        return data
    
    async def get_position(self) -> Union[str, int]:
        status = self._send_cmd(COMMAND_WORDS.REQ_POSITION)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.REQ_POSITION])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        val = struct.unpack(">i", bytes.fromhex(data))[0]
        return val

    async def req_velocity(self) -> Union[str, int]:
        status = self._send_cmd(COMMAND_WORDS.REQ_VELOCITY)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.REQ_VELOCITY])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        return int(data, 16)
        

    async def set_velocity(self, val: int) -> str:
        data = struct.pack(">B", val).hex().upper()
        status = self._send_cmd(COMMAND_WORDS.SET_VELOCITY, data)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        return status

    async def group_address(self, g_addr: int) -> str:
        pass # TODO Add servicing of group address

    async def optimize_motors(self) -> str:
        status = self._send_cmd(COMMAND_WORDS.OPTIMIZE_MOTORS)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.OPTIMIZE_MOTORS])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        return data

    async def clean_mechanics(self) -> str:
        status = self._send_cmd(COMMAND_WORDS.CLEAN_MECHANICS)
        if status != COMMAND_STATUS.OK:
            return str(status.value)
        data = self._read_resp(cmd_responses[COMMAND_WORDS.CLEAN_MECHANICS])
        if type(data) == COMMAND_STATUS:
            return str(data.value)
        return data
    
    async def reset_factory_default(self) -> str:
        status = self._send_cmd(COMMAND_WORDS.FACTORY_DEFAULT)
        return str(status.value)
