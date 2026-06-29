import abc
from typing import Union

DEVINFO_T = tuple[int, str, int, int, int, int, int]
'''
[0] - Mount model
[1] - Serial number
[2] - Year of manufacturing
[3] - Firmware release
[4] - Type (Imperial/Metric) | Hardware release
[5] - Travel range (mm/deg)
[6] - Pulses per position
'''

MOTORINFO_T = tuple[bool, float, int, int]
'''
[0] - State (ON/OFF)
[1] - Current
[2] - Clockwise frequency
[3] - Counterclockwise frequency
'''

CURRENT_CURVE_T = tuple[list[int], list[int]]
'''
[0] - Period values
[1] - Current values
'''

class ThorlabsELLXInterface(abc.ABC):
    
    # ======================
    # ====== MOVEMENT ======
    # ======================

    @abc.abstractmethod
    async def home(self, dir: int) -> tuple[int, Union[float, int]]:
        '''Move to the home (zero) position clockwise or anticlocwise

        Args:
            dir: direction of rotation (0 - clockwise, 1 - anticlockwise)

        Returns:
            First value is operation status. Second value is, if successful -
            mount position after rotation; if not - status of the device.
        '''

    @abc.abstractmethod
    async def move_absolute(self, val: float) -> tuple[int, Union[float, int]]:
        '''Move to a given position

        Args:
            val: desired position of the mount

        Returns:
            First value is operation status. Second value is, if successful -
            mount position after rotation; if not - status of the device.
        '''

    @abc.abstractmethod
    async def move_relative(self, val: float) -> tuple[int, Union[float, int]]:
        '''Move by a given distance

        Args:
            val: distance, by which the mount should move

        Returns:
            First value is operation status. Second value is, if successful -
            mount position after rotation; if not - status of the device.
        '''

    @abc.abstractmethod
    async def forward(self) -> tuple[int, Union[float, int]]:
        '''Move forward by a distance set in Jog Step Size
        
        If the Jog Step Size is set to 0, the device ELL14 moves
        continuously until a command STOP is sent.

        Returns:
            First value is operation status. Second value is, if successful -
            mount position after rotation; if not - status of the device.
        '''

    @abc.abstractmethod
    async def backward(self) ->tuple[int, Union[float, int]]:
        '''Move backward by a distance set in Jog Step Size

        If the Jog Step Size is set to 0, the device ELL14 moves
        continuously until a command STOP is sent.
        
        Returns:
            First value is operation status. Second value is, if successful -
            mount position after rotation; if not - status of the device.
        '''
    
    @abc.abstractmethod
    async def motion_stop(self) -> tuple[int, int]:
        '''Stop the contiuous motion of the device.

        It will also stop motor optimisation and cleaning cycle.
        
        Returns:
            First value is operation status, second is the device status
        '''
    
    @abc.abstractmethod
    async def clean_mechanics(self) -> str:
        pass

    # =====================
    # ====== SETTERS ======
    # =====================

    @abc.abstractmethod
    async def set_fwp(self, motor: int, val: int) -> tuple[int, int]:
        '''Change the operating frequency for the clockwise motion

        Args:
            motor: id of the motor (1 or 2)
            val: frequency to be set (in kHz)
        
        Returns:
            First value is operation status, second is the device status
        '''

    @abc.abstractmethod
    async def set_bwp(self, motor: int, val: int) -> tuple[int, int]:
        '''Change the operating frequency for the counterclockwise motion

        Args:
            motor: id of the motor (1 or 2)
            val: frequency to be set [kHz]
        
        Returns:
            First value is operation status, second is the device status
        '''

    @abc.abstractmethod
    async def set_autohoming(self, enable: int) -> Union[str, int]:
        pass

    @abc.abstractmethod
    async def set_home_offset(self, val: int) -> str:
        pass

    @abc.abstractmethod
    async def set_zero_position(self) -> tuple[int, int]:
        '''Set the current positin of the mount as the zero position
        
        Returns:
            First value is operation status, second is the device status
        '''

    @abc.abstractmethod
    async def set_jog_step(self, val: float) -> tuple[int, int]:
        '''Set the step of the jog mode movements
        
        Args:
            val: Step size of the jog mode
        
        Returns:
            First value is operation status, second is the device status
        '''

    @abc.abstractmethod
    async def set_velocity(self, val: int) -> tuple[int, int]:
        '''Set the movement velocity
        
        Args:
            val: Movement velocity of the mount to be set [%]
        
        Returns:
            First value is operation status, second is the device status
        '''
    
    @abc.abstractmethod
    async def reset_factory_default(self) -> tuple[int, int]:
        pass

    # =====================
    # ====== GETTERS ======
    # =====================

    @abc.abstractmethod
    async def get_information(self) -> tuple[int, Union[int, DEVINFO_T]]:
        '''Read the device information
        
        Returns:
            First value is operation status. Second value is, if successful -
            device information; if not - status of the device.
        '''

    @abc.abstractmethod
    async def get_status(self) -> Union[str, int]:
        '''Read the device status
        
        Returns:
            First value is operation status, second is the device status
        '''

    @abc.abstractmethod
    async def get_motor_info(self, motor: int) -> tuple[int, Union[int, MOTORINFO_T]]:
        '''Read the motor information
        
        Args:
            motor: id of the motor (1 or 2)

        Returns:
            First value is operation status. Second value is, if successful -
            motor information; if not - status of the device.
        '''

    @abc.abstractmethod
    async def get_current_curve(self, motor: int) -> Union[str, CURRENT_CURVE_T]:
        pass

    @abc.abstractmethod
    async def get_home_offset(self) -> tuple[int, Union[float, int]]:
        pass

    @abc.abstractmethod
    async def get_zero_position(self) -> tuple[int, Union[float, int]]:
        '''Read the offset between default zero position and the currently set one
        
        Returns:
            First value is operation status. Second value is, if successful -
            zero position offset; if not - status of the device.
        '''

    @abc.abstractmethod
    async def get_jog_step(self) -> tuple[int, Union[float, int]]:
        '''Read the step size of the jog mode movement
        
        Returns:
            First value is operation status. Second value is, if successful -
            step size of the jog movement; if not - status of the device.
        '''

    @abc.abstractmethod
    async def get_position(self) -> tuple[int, Union[float, int]]:
        '''Read the current position of the mount
        
        Returns:
            First value is operation status. Second value is, if successful -
            mount position; if not - status of the device.
        '''

    @abc.abstractmethod
    async def get_velocity(self) -> tuple[int, int]:
        '''Read the movement velocity

        Returns:
            First value is operation status. Second value is, if successful -
            movement velocity; if not - status of the device.
        '''

    # ===========================
    # ====== MISCELLANEOUS ======
    # ===========================

    @abc.abstractmethod
    async def req_save_user_data(self) -> str:
        pass

    @abc.abstractmethod
    async def req_change_address(self, new_addr: int) -> str:
        pass

    @abc.abstractmethod
    async def req_search_freq(self, motor: int) -> str:
        pass

    @abc.abstractmethod
    async def req_scan_current_curve(self, motor: int) -> str:
        pass

    @abc.abstractmethod
    async def isolate_device(self, minutes: int) -> tuple[int, int]:
        '''Disable the serial interface for a given amount of time
        
        Args:
            minutes: number of minutes the serial interface will be disabled

        Returns:

        '''

    @abc.abstractmethod
    async def req_skip_frequency(self) -> str:
        pass

    @abc.abstractmethod
    async def group_address(self, g_addr: int) -> str:
        pass
    
    @abc.abstractmethod
    async def optimize_motors(self) -> str:
        pass
    