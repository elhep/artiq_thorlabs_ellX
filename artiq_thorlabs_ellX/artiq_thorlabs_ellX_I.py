import abc
from typing import Union

DEVINFO_T = tuple[int, int, int, int, int, int, int]
'''
[0] - Mount model
[1] - Serial number
[2] - Year of manufacturing
[3] - Firmware release
[4] - Type (Imperial/Metric) | Hardware release
[5] - Travel range (mm/deg)
[6] - Pulses per position
'''

MOTORINFO_T = tuple[int, int, int, int]
'''
[0] - State (ON/OFF)
[1] - Current
[2] - Forward period
[3] - Backward period
'''

CURRENT_CURVE_T = tuple[list[int], list[int]]
'''
[0] - Period values
[1] - Current values
'''

class ThorlabsELLXInterface(abc.ABC):
    
    @abc.abstractmethod
    async def get_information(self) -> Union[str, DEVINFO_T]:
        pass

    @abc.abstractmethod
    async def get_status(self) -> Union[str, int]:
        pass

    @abc.abstractmethod
    async def req_save_user_data(self) -> str:
        pass

    @abc.abstractmethod
    async def req_change_address(self, new_addr: int) -> str:
        pass

    @abc.abstractmethod
    async def get_motor_info(self, motor: int) -> Union[str, MOTORINFO_T]:
        pass

    @abc.abstractmethod
    async def set_fwp(self, motor: int, val: int) -> str:
        pass

    @abc.abstractmethod
    async def set_bwp(self, motor: int, val: int) -> str:
        pass

    @abc.abstractmethod
    async def req_search_freq(self, motor: int) -> str:
        pass

    @abc.abstractmethod
    async def req_scan_current_curve(self, motor: int) -> str:
        pass

    @abc.abstractmethod
    async def get_current_curve(self, motor: int) -> Union[str, CURRENT_CURVE_T]:
        pass

    @abc.abstractmethod
    async def isolate_device(self, minutes: int) -> str:
        pass

    @abc.abstractmethod
    async def req_home(self, dir: int) -> Union[str, int]:
        pass

    @abc.abstractmethod
    async def set_autohoming(self, enable: int) -> Union[str, int]:
        pass

    @abc.abstractmethod
    async def req_absolute_move(self, val: int) -> Union[str, int]:
        pass

    @abc.abstractmethod
    async def req_relative_move(self, val: int) -> Union[str, int]:
        pass

    @abc.abstractmethod
    async def req_home_offset(self) -> Union[str, int]:
        pass

    @abc.abstractmethod
    async def set_home_offset(self, val: int) -> str:
        pass

    @abc.abstractmethod
    async def req_zero_position(self) -> Union[str, int]:
        pass

    @abc.abstractmethod
    async def set_zero_position(self) -> str:
        pass

    @abc.abstractmethod
    async def req_jog_step(self) -> Union[str, int]:
        pass

    @abc.abstractmethod
    async def set_jog_step(self, val: int) -> str:
        pass

    @abc.abstractmethod
    async def forward(self) -> Union[str, int]:
        '''Move forward by a distance set in Jog Step Size
        
        If the Jog Step Size is set to 0, the device ELL14 moves
        continuously until a command STOP is sent.

        Returns:
            Position after finished move or a command status
        '''

    @abc.abstractmethod
    async def backward(self) -> Union[str, int]:
        '''Move backward by a distance set in Jog Step Size

        If the Jog Step Size is set to 0, the device ELL14 moves
        continuously until a command STOP is sent.
        
        Returns:
            Position after finished move or a command status
        '''

    @abc.abstractmethod
    async def req_skip_frequency(self) -> str:
        '''Bypass the frequency search performed at startup
        
        Returns:
            Command status
        '''
    
    @abc.abstractmethod
    async def motion_stop(self) -> str:
        '''Stop the contiuous motion of the device.

        It will also stop motor optimisation and cleaning cycle.
        
        Returns:
            Command status
        '''
    
    @abc.abstractmethod
    async def get_position(self) -> Union[str, int]:
        '''Read the current position of the mount
        
        Returns:
            Position of the mount or a command status
        '''

    @abc.abstractmethod
    async def req_velocity(self) -> Union[str, int]:
        '''Read the movement velocity

        Returns:
            Movement velocity of the mount or a status command
        '''
    
    @abc.abstractmethod
    async def set_velocity(self, val: int) -> str:
        '''Set the movement velocity
        
        Args:
            val: New movement velocity of the mount to be set
        
        Returns:
            Command status
        '''
    
    @abc.abstractmethod
    async def group_address(self, g_addr: int) -> str:
        '''Make the mount to listen to another address for one command
        
        Args:
            g_addr: Group addres the mount will listen to next
        
        Returns:
            Command status
        '''
    
    @abc.abstractmethod
    async def optimize_motors(self) -> str:
        '''Fine tune the operating frequency after performing a frequency search

        This operation may take a couple of minutes.
        
        Returns:
            Command status
        '''
    
    @abc.abstractmethod
    async def clean_mechanics(self) -> str:
        '''Force a cleaning cycle - a movement over the whole available range
        
        Returns:
            Command status
        '''
    
    @abc.abstractmethod
    async def reset_factory_default(self) -> str:
        '''Restore all parameters to factory defaults. Available for ELL22.
        
        Returns:
            Command status
        '''

    