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
            
            if address.startswith("VW"):
                start_address = int(address[2:])
                size = 2
            elif address.startswith("VD"):
                start_address = int(address[2:])
                size = 4
            else:
                return None
            
            data = self.client.read_area(snap7.client.S7Area.DB, self.db_number, start_address, size)
            
            if data_type == "Int":
                return get_int(data, 0)
            elif data_type == "Real":
                return get_real(data, 0)
            return None
        except Exception as e:
            print(f"读取参数失败 {address}: {e}")
            return None
    
    def write_parameter(self, address: str, value: Any, data_type: str = "Int") -> bool:
        try:
            if not self.client or not self.client.get_connected():
                return False
            
            if address.startswith("VW"):
                start_address = int(address[2:])
                size = 2
            elif address.startswith("VD"):
                start_address = int(address[2:])
                size = 4
            else:
                return False
            
            data = bytearray(size)
            
            if data_type == "Int":
                set_int(data, 0, int(value))
            elif data_type == "Real":
                set_real(data, 0, float(value))
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
