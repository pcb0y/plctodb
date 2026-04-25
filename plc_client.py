import snap7
from snap7.util import *
from config import PLC_CONFIG

class PLCClient:
    def __init__(self, ip=None, rack=None, slot=None):
        self.ip = ip or PLC_CONFIG['host']
        self.rack = rack if rack is not None else PLC_CONFIG['rack']
        self.slot = slot if slot is not None else PLC_CONFIG['slot']
        self.port = PLC_CONFIG['port']
        self.db_number = PLC_CONFIG['db_number']
        self.client = None
    
    def connect(self):
        try:
            self.client = snap7.client.Client()
            self.client.connect(self.ip, self.rack, self.slot, self.port)
            if self.client.get_connected():
                print(f"PLC连接成功: {self.ip}")
                return True
            else:
                print(f"PLC连接失败: {self.ip}")
                return False
        except Exception as e:
            print(f"PLC连接异常: {e}")
            return False
    
    def disconnect(self):
        if self.client and self.client.get_connected():
            self.client.disconnect()
            print(f"PLC连接已断开: {self.ip}")
    
    def read_parameter(self, address, data_type="Int"):
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
    
    def write_parameter(self, address, value, data_type="Int"):
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
                set_int(data, 0, value)
            elif data_type == "Real":
                set_real(data, 0, value)
            else:
                return False
            
            self.client.write_area(snap7.client.S7Area.DB, self.db_number, start_address, data)
            print(f"写入成功 {address} = {value}")
            return True
        except Exception as e:
            print(f"写入参数失败 {address}: {e}")
            return False
    
    def read_multiple_parameters(self, param_list):
        results = {}
        for param_name, address, data_type in param_list:
            value = self.read_parameter(address, data_type)
            results[param_name] = value
        return results
