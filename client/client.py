import os
import time, copy, math, collections, random,socket, math
import modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus_tcp as modbus_tcp
from datetime import datetime
import struct

HOST_ADDR      = "10.1.10.9"
PORT           = 502
# SLAVE_INDEX    = 1
# TYPE_DEFINITION = {
#   'int（两个地址表示）': 2,
#   'int': 2,
#   '布尔类型': 1,
#   'int': 2,
#   'bool': 1,
#   'dint': 2,
#   'DINT': 2,
#   'float': 2,
# }
protocol_dir = './kn/'

cfg_address = {
  'analog_sortedAddress' : [0, 100],
  'analog_sortedLength' : [100, 68],
  'troubleAddress' : [1, 101, 201, 301, 601, 701],
  'troubleLength' : [100, 100, 100, 100, 100, 100],
  'analogAddress' : [1, 101, 201, 301, 601, 701],
  'analogLength' : [100, 100, 100, 100, 100, 100],
  'digitalAddress' : [1, 1001, 1401, 2201],
  'digitalLength' : [300, 200, 200, 562],
  'paramsAddress' : [800, 900, 1000, 1100, 5200],
  'paramsLength' : [100, 100, 100, 40, 100],
  'triggerAddress' : [2201, 2301, 2401, 2501, 2601, 2711],
  'triggerLength' : [100, 100, 100, 100, 100, 96, 38],
  'triggerParamsAddress' : [1201, 1301, 1401, 1501, 1601, 1711],
  'triggerParamsLength' : [100, 100, 100, 100, 100, 96, 38],
  'resetAddress' : [4201, 4301, 4401, 4501, 4601, 4701],
  'resetLength' : [100, 100, 100, 100, 100, 100, 100],
  'manualResetAddress' : [1701, 1801, 1901],
  'manualResetLength' : [100, 100, 74],
  'paramsHideAddress' : [501, 601, 701],
  'paramsHideLength' : [100, 100, 74],
  'resetParamsAddress' : [3201, 3301, 3401, 3501, 3601, 3711],
  'resetParamsLength' : [100, 100, 100, 100, 100, 96, 38]
}
# master = modbus_tcp.TcpMaster(host=HOST_ADDR, port=PORT)
# master.set_timeout(10.0)
 
def read_cfg():
  cfg = {}
  for file in os.listdir(protocol_dir):
    # if file == 'analog.csv' or file == 'digital.csv' or file == 'params.csv' or file == 'trigger.csv' or file == 'triggerParams.csv' or file == 'reset.csv' or file == 'resetParams.csv' or file == 'manualReset.csv' or file == 'paramsHide.csv'or file == 'trouble.csv':
    if file == 'analog_sorted.csv':
      name = file.split('.')[0]
      if name not in cfg:
        cfg[name] = []
      with open(protocol_dir + file, 'r', encoding='utf-8') as f:
        content = f.readlines()
        for line in content:
          params = line.replace('\n', '', 2).split(',')
          cfg[name].append({
            'name': params[1],
            'type': params[0],
            'address': int(params[2])-1
          })
      continue
  return cfg

analogAddress = [1, 101, 201, 301, 601, 701]
analogLength = [100, 100, 100, 100, 100, 100]
digitalAddress = [1, 1001, 1401, 2201]
digitalLength = [300, 200, 200, 600]
paramsAddress = [800, 900, 1000, 1100, 5200]
paramsLength = [100, 100, 100, 40, 99]
triggerAddress = [2201, 2301, 2401, 2501, 2601, 2711]
triggerLength = [100, 100, 100, 100, 100, 96, 38]
triggerParamsAddress = [1201, 1301, 1401, 1501, 1601, 1711]
triggerParamsLength = [100, 100, 100, 100, 100, 96, 38]
resetAddress = [4201, 4301, 4401, 4501, 4601, 4711]
resetLength = [100, 100, 100, 100, 100, 100, 100]
resetParamsAddress = [3201, 3301, 3401, 3501, 3601, 3711]
resetParamsLength = [100, 100, 100, 100, 100, 96, 38]

def float2Bits(f):
  s = struct.pack('>f', float(f))
  return struct.unpack('>l', s)[0]

def socket_byte_write(ip, data):
  s = socket.socket()
  s.connect((ip, 502))
  s.settimeout(5)
  unitvar = data[0]
  address = data[1] - 1
  value = data[2]
  address1 = 0
  address2 = 0
  print(address)

  if address >  255:
    address1 = int(address / 256)
    address2 = address - address1 * 256
  else:
    address2 = address
  value1 = 0
  if value == 1:
    value1 = 255
    
  val = bytearray([0,0,0,0,0,6,unitvar, 5, address1, address2, value1, 0])
  s.send(val)
  pass

def socket_double_write(ip, data):
  s = socket.socket()
  s.connect((ip, 502))
  s.settimeout(5)
  unitvar = data[0]
  address = data[1] -1
  resvalue = data[2]
  res2value = data[3]
  number = data[4]
  address1 = 0
  address2 = 0
  if address >  255:
    address1 = int(address / 256)
    address2 = address - address1 * 256
  else:
    address2 = address

  if resvalue < 0 and res2value < 0:
    resvalue =resvalue + 65535
    res2value =res2value + 65536
  elif resvalue < 0 and res2value >= 0 :
    resvalue = resvalue+  65536
  elif resvalue >= 0 and res2value < 0 :
    res2value = resvalue+ 65536

  resvalue1 = 0
  resvalue2 = 0
  if resvalue > 255:
    resvalue1 = int(resvalue / 256)
    resvalue2 = resvalue - resvalue1 * 256
  else:
    resvalue2 = resvalue
  
  res2value1 = 0
  res2value2 = 0
  if res2value > 255:
    res2value1 = res2value / 256
    res2value2 = res2value - res2value1 * 256
  else:
    res2value2 = res2value
    print(number, address1, address2, res2value1, res2value2, resvalue1, resvalue2)
  val = bytearray([
    0,
    number,
    0,
    0,
    0,
    11,
    unitvar, 
    16, 
    address1, 
    address2, 
    0, 
    2,
    4, 
    int(res2value1), 
    int(res2value2), 
    int(resvalue1), 
    int(resvalue2)
    ])
  s.send(val)
  pass

def socket_dint_write(ip, data):
  s = socket.socket()
  s.connect((ip, 502))
  s.settimeout(5)
  unitvar = data[0]
  address = data[1]
  resvalue = data[2]
  res2value = data[3]
  number = data[4]

  if address >  255:
    address1 = math.floor(address / 256)
    address2 = address - address1 * 256
  else:
    address2 = address
    
  resvalue1 = 0
  resvalue2 = 0
  if resvalue > 255:
    resvalue1 = resvalue / 256
    resvalue2 = resvalue - resvalue1 * 256
  else:
    resvalue2 = resvalue
  
  res2value1 = 0
  res2value2 = 0
  if res2value > 255:
    res2value1 = res2value / 256
    res2value2 = res2value - res2value1 * 256
  else:
    res2value2 = res2value

  val = bytearray([0,number,0,0,0,11,unitvar, 16, address1, address2, 0, 2,4,res2value1, res2value2, resvalue1, resvalue2])
  s.send(val)
  pass

def byte_ctrl(data, ip):
  # modbus_data = master.execute(slave=1, function_code = cst.READ_COILS, starting_address=start, quantity_of_x=digitalLength[index])
  if len(data) == 2:
    for item in data:
      socket_byte_write(ip, item)
      time.sleep(1)
  if len(data) == 1:
    socket_byte_write(ip, data[0])
  return ''
  
def write_ctrl(data, ip, category, mode):
  if category == 'double':
    var = float2Bits(data)
    var1 = int(var / 65536)
    var2 = int(var % 65536)
    number = random.random()*100
    if len(mode) == 1:
      socket_double_write(ip, [mode[0][0], mode[0][1], var1, var2, round(number)])
      pass
    if len(mode) == 2:
      socket_double_write(ip, [mode[0][0], mode[0][1], var1, var2, round(number)])
      socket_byte_write(ip, [mode[1][0], mode[1][1], 1])
      pass
    pass
  if category == 'dint':
    var1 = int(var / 65536)
    var2 = int(var % 65536)
    number = random.random()*100
    socket_double_write(ip, [mode[0][0], mode[0][1], var1, var2, round(number)])
    socket_byte_write(ip, [mode[1][0], mode[1][1], 1])
    pass
  return ''

def parsefloat(modbus_data, first, end):
  first = hex(first).replace('0x', '')
  end = hex(end).replace('0x', '')
  while len(first) < 4:
    first = '0' + first
  while len(end) < 4:
    end = '0' + end
  value = struct.unpack('>f', bytes.fromhex(end+first))[0]
  return value

def parseDint(first, end):
  first = hex(first).replace('0x', '')
  end = hex(end).replace('0x', '')
  while len(first) < 4:
    first = '0' + first
  while len(end) < 4:
    end = '0' + end
  value = struct.unpack('>L', bytes.fromhex(end+first))[0]
  return value

def read_type_data(cfg, cfg_type, master):
  data = []
  cfg_data = cfg[cfg_type]
  reg_data = {}
  for index in range(len(cfg_address[cfg_type+'Address'])):
    start = cfg_address[cfg_type+'Address'][index] - 1
    if cfg_data[0]['type'] == 'boolean':
      modbus_data = master.execute(slave=1, function_code = cst.READ_COILS, starting_address=start, quantity_of_x=cfg_address[cfg_type+'Length'][index]+1)
    else:
      modbus_data = master.execute(slave=1, function_code = cst.READ_HOLDING_REGISTERS, starting_address=start, quantity_of_x=cfg_address[cfg_type+'Length'][index]+1)
    for offset in range(len(modbus_data)):
      reg_data[start+offset] = modbus_data[offset]
  for item in cfg_data:
    if item['type'] == 'boolean':
      data.append({
        'name': item['name'],
        'type': item['type'],
        'address': item['address'],
        'value': reg_data[item['address']],
      })
    if item['type'] == 'float':
      first = reg_data[item['address']]
      end = reg_data[item['address']+1]
      value = parsefloat(modbus_data, first, end)
      data.append({
        'name': item['name'],
        'type': item['type'],
        'address': item['address'],
        'value': value,
      })

    if item['type'] == 'int' or item['type'] == 'int' or item['type'] == 'dint' or item['type'] == 'DINT':
      first = reg_data[item['address']]
      end = reg_data[item['address']+1]
      value = parseDint(first, end)
      data.append({
        'name': item['name'],
        'type': item['type'],
        'address': item['address'],
        'value': value
      })
  return data

def params_write(value, v_type, address, master):
  address = int(address)
  val = None
  # val = struct.pack('>f',value).hex()
  if v_type == 'boolean' :
    master.execute(slave=1, function_code = cst.WRITE_SINGLE_COIL, starting_address=address, quantity_of_x=1, output_value=[int(value)])
    return
  if v_type == 'float' :
    bint = float2Bits(value)
    val = hex(bint).replace('0x', '')
  if v_type == 'dint' or v_type == 'DINT' or v_type == 'int' or v_type == 'int' :
    val = hex(int(value)).replace('0x', '')
  while len(val) < 8:
    val = '0'+val
  master.execute(slave=1, function_code = cst.WRITE_MULTIPLE_REGISTERS, starting_address=address, quantity_of_x=2, output_value=[int(str(val[4:]), 16), int(str(val[:4]),16)])

# params_write(1789.0, 'float', 800, master)