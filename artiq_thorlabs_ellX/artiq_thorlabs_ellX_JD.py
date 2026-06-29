from artiq_thorlabs_ellX.artiq_thorlabs_ellX_I import ThorlabsELLXInterface, CURRENT_CURVE_T, DEVINFO_T, MOTORINFO_T
import serial
from enum import IntEnum
from typing import Optional, Union
import dataclasses as dc

class DEVICE_STATUS(IntEnum):
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

class COM_STATUS(IntEnum):
    COM_OK = 0
    ADDR_ERROR = 1
    RESP_SIZE_ERROR = 2
    NO_RESP_ERROR = 3
    MOVE_RESP_ERROR = 4
    UNKNOWN_RESP_ERROR = 5
    ABNORMAL_STATUS_VAL = 6
    SERIAL_ERROR = 7
    NOT_IMPLEMENTED = 8

@dc.dataclass
class COM_RESULT_T:
    com_s: COM_STATUS
    cmd_s: DEVICE_STATUS
    data: str

class ThorlabsELLXJD(ThorlabsELLXInterface):
    def __init__(self, device: str, baudrate: int = 9600,
                 timeout: float = 10, addr: int = 0) -> None:
        self.device = device
        self.baudrate = baudrate
        self.timeout = timeout
        self.dev_addr = addr
        self.serial: Optional[serial.Serial] = None
        self.device_type = None
        self.connect()

    def log(self, msg: str) -> None:
        print(f"[{self.__class__.__name__}] {msg}")
    
    def connect(self) -> COM_STATUS:
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
            return COM_STATUS.SERIAL_ERROR
        return COM_STATUS.COM_OK
    
    def close(self) -> None:
        """Close serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()
    
    def _parse_resp_status(self, resp: str) -> COM_STATUS:
        if "ADDR_ERROR" in resp:
            return COM_STATUS.ADDR_ERROR
        elif "RESP_SIZE_ERROR" in resp:
            return COM_STATUS.RESP_SIZE_ERROR
        elif "NO_RESP_ERROR" in resp:
            return COM_STATUS.NO_RESP_ERROR
        elif "MOVE_RESP_ERROR" in resp:
            return COM_STATUS.MOVE_RESP_ERROR
        elif "UNKNOWN_RESP_ERROR" in resp:
            return COM_STATUS.UNKNOWN_RESP_ERROR
        elif "STATUS " in resp:
            return COM_STATUS.ABNORMAL_STATUS_VAL
        elif len(resp) == 0:
            return COM_STATUS.SERIAL_ERROR
        return COM_STATUS.COM_OK
    
    def _parse_resp_cmd_status(self, resp: str) -> DEVICE_STATUS:
        if "STATUS " not in resp:
            return DEVICE_STATUS.OK
        status_val = int(resp.strip().split(" ")[1])
        if status_val < 0 or status_val > 13:
            return DEVICE_STATUS.OK
        return DEVICE_STATUS(status_val)

    def _send_cmd(self, cmd: str) -> COM_RESULT_T:
        self.log(f"Sending: {cmd}")
        try:
            self.serial.write(cmd.encode("ascii", errors="ignore"))
            self.serial.readline()
            data = self.serial.readline().decode("ascii", errors="ignore").strip()
            self.log(f"Read: {data}")
            com_status = self._parse_resp_status(data)
            if com_status == COM_STATUS.ABNORMAL_STATUS_VAL:
                cmd_status = self._parse_resp_cmd_status(data)
                return COM_RESULT_T(com_status, cmd_status, "")
            if com_status != COM_STATUS.COM_OK:
                return COM_RESULT_T(com_status, DEVICE_STATUS.OK, "")
        except Exception as e:
            self.log(f"Serial port error: {e}")
            return COM_RESULT_T(COM_STATUS.SERIAL_ERROR, DEVICE_STATUS.OK, "")
        return COM_RESULT_T(COM_STATUS.COM_OK, DEVICE_STATUS.OK, data)
    
    # ======================
    # ====== MOVEMENT ======
    # ======================

    async def home(self, dir: int) -> tuple[int, Union[float, int]]:
        cmd = f"home {dir}"
        resp = self._send_cmd(cmd)
        if resp.com_s == COM_STATUS.COM_OK:
            value = float(resp.data)
            return (resp.com_s.value, value)
        else:
            return (resp.com_s.value, resp.cmd_s.value)

    async def move_absolute(self, val: int) -> tuple[int, Union[float, int]]:
        cmd = f"move_absolute {val:f}\n"
        resp = self._send_cmd(cmd)
        if resp.com_s == COM_STATUS.COM_OK:
            value = float(resp.data)
            return (resp.com_s.value, value)
        else:
            return (resp.com_s.value, resp.cmd_s.value)
    
    async def move_relative(self, val: float) -> tuple[int, Union[float, int]]:
        cmd = f"move_relative {val:f}\n"
        resp = self._send_cmd(cmd)
        if resp.com_s == COM_STATUS.COM_OK:
            value = float(resp.data)
            return (resp.com_s.value, value)
        else:
            return (resp.com_s.value, resp.cmd_s.value)

    async def forward(self) -> tuple[int, Union[float, int]]:
        cmd = f"forward\n"
        resp = self._send_cmd(cmd)
        if resp.com_s == COM_STATUS.COM_OK:
            value = float(resp.data)
            return (resp.com_s.value, value)
        else:
            return (resp.com_s.value, resp.cmd_s.value)
    
    async def backward(self) -> tuple[int, Union[float, int]]:
        cmd = f"backward\n"
        resp = self._send_cmd(cmd)
        if resp.com_s == COM_STATUS.COM_OK:
            value = float(resp.data)
            return (resp.com_s.value, value)
        else:
            return (resp.com_s.value, resp.cmd_s.value)
    
    async def motion_stop(self) -> tuple[int, int]:
        cmd = f"motion_stop\n"
        resp = self._send_cmd(cmd)
        return (resp.com_s.value, resp.cmd_s.value)
    
    # =====================
    # ====== SETTERS ======
    # =====================

    async def set_jog_step(self, val: float) -> tuple[int, int]:
        cmd = f"set_jog_step {val:f}\n"
        resp = self._send_cmd(cmd)
        return (resp.com_s.value, resp.cmd_s.value)
    
    async def set_velocity(self, val: int) -> tuple[int, int]:
        cmd = f"set_velocity {val:i}\n"
        resp = self._send_cmd(cmd)
        return (resp.com_s.value, resp.cmd_s.value)
    
    async def set_fwp(self, motor: int, val: int) -> tuple[int, int]:
        cmd = f"set_motor_fwp {motor:i} {val:i}\n"
        resp = self._send_cmd(cmd)
        return (resp.com_s.value, resp.cmd_s.value)

    async def set_bwp(self, motor: int, val: int) -> tuple[int, int]:
        cmd = f"set_motor_bwp {motor:i} {val:i}\n"
        resp = self._send_cmd(cmd)
        return (resp.com_s.value, resp.cmd_s.value)
    
    async def set_zero_position(self) -> tuple[int, int]:
        cmd = f"set_zero_position\n"
        resp = self._send_cmd(cmd)
        return (resp.com_s.value, resp.cmd_s.value)
    
    # =====================
    # ====== GETTERS ======
    # =====================
    
    async def get_information(self) -> tuple[int, Union[int, DEVINFO_T]]:
        cmd = f"get_info\n"
        resp = self._send_cmd(cmd)
        if resp.com_s == COM_STATUS.COM_OK:
            tokens = resp.data.split(',')
            if len(tokens) != 7:
                return (COM_STATUS.RESP_SIZE_ERROR, DEVICE_STATUS.OK)
            model = int(tokens[0])
            serial = tokens[1]
            year = int(tokens[2])
            firmware = int(tokens[3])
            hardware = int(tokens[4])
            travel = int(tokens[5])
            pulses = int(tokens[6])
            ret_data = (model, serial, year, firmware, hardware, travel, pulses)
            return (resp.com_s.value, ret_data)
        else:
            return (resp.com_s.value, resp.cmd_s.value)

    async def get_status(self) -> tuple[int, int]:
        cmd = f"get_status\n"
        resp = self._send_cmd(cmd)
        return (resp.com_s.value, resp.cmd_s.value)

    async def get_motor_info(self, motor: int) -> tuple[int, Union[int, MOTORINFO_T]]:
        cmd = f"get_motor_info {motor:i}\n"
        resp = self._send_cmd(cmd)
        if resp.com_s == COM_STATUS.COM_OK:
            tokens = resp.data.split(',')
            if len(tokens) != 4:
                return (COM_STATUS.RESP_SIZE_ERROR, DEVICE_STATUS.OK)
            is_on = bool(tokens[0])
            current = float(tokens[1])
            fwp = int(tokens[2])
            bwp = int(tokens[3])
            ret_data = (is_on, current, fwp, bwp)
            return (resp.com_s.value, ret_data)
        else:
            return (resp.com_s.value, resp.cmd_s.value)

    async def get_zero_position(self) -> tuple[int, Union[float, int]]:
        cmd = f"get_zero_position\n"
        resp = self._send_cmd(cmd)
        if resp.com_s == COM_STATUS.COM_OK:
            value = float(resp.data)
            return (resp.com_s.value, value)
        else:
            return (resp.com_s.value, resp.cmd_s.value)

    async def get_jog_step(self) -> tuple[int, Union[float, int]]:
        cmd = f"get_jog_step\n"
        resp = self._send_cmd(cmd)
        if resp.com_s == COM_STATUS.COM_OK:
            value = float(resp.data)
            return (resp.com_s.value, value)
        else:
            return (resp.com_s.value, resp.cmd_s.value)
    
    async def get_position(self) -> tuple[int, Union[float, int]]:
        cmd = f"get_position\n"
        resp = self._send_cmd(cmd)
        if resp.com_s == COM_STATUS.COM_OK:
            value = float(resp.data)
            return (resp.com_s.value, value)
        else:
            return (resp.com_s.value, resp.cmd_s.value)

    async def get_velocity(self) -> tuple[int, int]:
        cmd = f"get_velocity\n"
        resp = self._send_cmd(cmd)
        if resp.com_s == COM_STATUS.COM_OK:
            value = int(resp.data)
            return (resp.com_s.value, value)
        else:
            return (resp.com_s.value, resp.cmd_s.value)
    
    # ===========================
    # ====== MISCELLANEOUS ======
    # ===========================

    async def isolate_device(self, minutes: int) -> tuple[int, int]:
        cmd = f"isolate_dev {minutes:i}\n"
        resp = self._send_cmd(cmd)
        return (resp.com_s.value, resp.cmd_s.value)

    # =============================
    # ====== NOT IMPLEMENTED ======
    # =============================

    async def req_save_user_data(self) -> str:
        return COM_STATUS.NOT_IMPLEMENTED.value

    async def req_change_address(self, new_addr: int) -> str:
        return COM_STATUS.NOT_IMPLEMENTED.value
    
    async def req_search_freq(self, motor: int) -> int:
        return COM_STATUS.NOT_IMPLEMENTED.value

    async def req_scan_current_curve(self, motor: int) -> str:
        return COM_STATUS.NOT_IMPLEMENTED.value

    async def get_current_curve(self, motor: int) -> Union[str, CURRENT_CURVE_T]:
        return COM_STATUS.NOT_IMPLEMENTED.value
    
    async def set_autohoming(self, enable: int) -> Union[str, int]:
        return COM_STATUS.NOT_IMPLEMENTED.value

    async def req_home_offset(self) -> Union[str, int]:
        return COM_STATUS.NOT_IMPLEMENTED.value

    async def set_home_offset(self, val: int) -> int:
        return COM_STATUS.NOT_IMPLEMENTED.value
    
    async def req_skip_frequency(self) -> int:
        return COM_STATUS.NOT_IMPLEMENTED.value
    
    async def group_address(self, g_addr: int) -> int:
        return COM_STATUS.NOT_IMPLEMENTED.value
    
    async def optimize_motors(self) -> int:
        return COM_STATUS.NOT_IMPLEMENTED.value
    
    async def clean_mechanics(self) -> int:
        return COM_STATUS.NOT_IMPLEMENTED.value
    
    async def reset_factory_default(self) -> int:
        return COM_STATUS.NOT_IMPLEMENTED.value
        
