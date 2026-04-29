import snap7
from snap7.util import *
from config import PLC_CONFIG
from typing import Optional, Dict, Any

class PLCClient:
    def __init__(self, ip: str, rack: int = 0, slot: int = 1):
        self.ip = ip
        self.rack = rack
        self.slot = slot
        self.port = PLC_CONFIG['port']
        self.db_number = PLC_CONFIG['db_number']
        self.client: Optional[snap7.client.Client] = None
    
    def __enter__(self):
        if self.connect():
            return self
        raise ConnectionError(f"无法连接到 PLC {self.ip}")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False
    
    def connect(self) -> bool:
        try:
            self.client = snap7.client.Client()
            self.client.connect(self.ip, self.rack, self.slot, self.port)
            return self.client.get_connected()
        except Exception as e:
            print(f"PLC连接异常: {e}")
            return False
    
    def disconnect(self):
        if self.client:
            try:
                self.client.disconnect()
            except Exception as e:
                print(f"PLC断开连接异常: {e}")
            finally:
                self.client = None
    
    def read_parameter(self, address: str, data_type: str = "Int") -> Optional[Any]:
        try:
            if not self.client or not self.client.get_connected():
                return None
            
            address = address.strip().upper()
            size = 2
            
            if address.startswith("VW"):
                start_address = int(address[2:])
                size = 2
            elif address.startswith("VD"):
                start_address = int(address[2:])
                size = 4
            elif address.startswith("VB"):
                start_address = int(address[2:])
                size = 1
            elif address.startswith("VC"):
                start_address = int(address[2:])
                size = 2
            elif address.startswith("V") and "." in address:
                parts = address[1:].split(".")
                start_address = int(parts[0])
                bit = int(parts[1])
                data = self.client.read_area(snap7.client.S7Area.DB, self.db_number, start_address, 1)
                byte_value = int.from_bytes(data, byteorder='big')
                return (byte_value & (1 << bit)) != 0
            elif address.startswith("C"):
                try:
                    counter_number = int(address[1:])
                    counter_data = self.client.read_area(0x1C, 0, counter_number * 2, 2)
                    return get_int(counter_data, 0)
                except Exception as ce:
                    print(f"读取计数器失败 {address}: {ce}")
                    return None
            elif address.startswith("T"):
                try:
                    timer_number = int(address[1:])
                    timer_data = self.client.read_area(0x1D, 0, timer_number * 2, 2)
                    return get_int(timer_data, 0)
                except Exception as te:
                    print(f"读取定时器失败 {address}: {te}")
                    return None
            else:
                return None
            
            data = self.client.read_area(snap7.client.S7Area.DB, self.db_number, start_address, size)
            
            if data_type == "Bool":
                return get_bool(data, 0, 0)
            elif data_type == "Int" or address.startswith("VW") or address.startswith("VC"):
                return get_int(data, 0)
            elif data_type == "Real" or address.startswith("VD"):
                return get_real(data, 0)
            elif address.startswith("VB"):
                return get_bool(data, 0, 0)
            return None
        except Exception as e:
            print(f"读取参数失败 {address}: {e}")
            return None
    
    def write_parameter(self, address: str, value: Any, data_type: str = "Int") -> bool:
        try:
            if not self.client or not self.client.get_connected():
                return False
            
            address = address.strip().upper()
            size = 2
            
            if address.startswith("VW"):
                start_address = int(address[2:])
                size = 2
            elif address.startswith("VD"):
                start_address = int(address[2:])
                size = 4
            elif address.startswith("VB"):
                start_address = int(address[2:])
                size = 1
            elif address.startswith("VC"):
                start_address = int(address[2:])
                size = 2
            elif address.startswith("V") and "." in address:
                parts = address[1:].split(".")
                start_address = int(parts[0])
                bit = int(parts[1])
                current_data = self.client.read_area(snap7.client.S7Area.DB, self.db_number, start_address, 1)
                byte_value = int.from_bytes(current_data, byteorder='big')
                if value:
                    byte_value |= (1 << bit)
                else:
                    byte_value &= ~(1 << bit)
                self.client.write_area(snap7.client.S7Area.DB, self.db_number, start_address, byte_value.to_bytes(1, byteorder='big'))
                return True
            elif address.startswith("C"):
                counter_number = int(address[1:])
                data = bytearray(2)
                set_int(data, 0, int(value))
                self.client.write_area(0x1C, 0, counter_number * 2, data)
                return True
            elif address.startswith("T"):
                timer_number = int(address[1:])
                data = bytearray(2)
                set_int(data, 0, int(value))
                self.client.write_area(0x1D, 0, timer_number * 2, data)
                return True
            else:
                return False
            
            data = bytearray(size)
            
            if data_type == "Int" or address.startswith("VW") or address.startswith("VC"):
                set_int(data, 0, int(value))
            elif data_type == "Real" or address.startswith("VD"):
                set_real(data, 0, float(value))
            elif data_type == "Bool" or address.startswith("VB"):
                set_bool(data, 0, 0, bool(value))
            else:
                return False
            
            self.client.write_area(snap7.client.S7Area.DB, self.db_number, start_address, data)
            return True
        except Exception as e:
            print(f"写入参数失败 {address}: {e}")
            return False
    
    def read_multiple_parameters(self, param_list: list) -> Dict[str, Any]:
        results = {}
        for param_name, address, data_type in param_list:
            value = self.read_parameter(address, data_type)
            results[param_name] = value
        return results
