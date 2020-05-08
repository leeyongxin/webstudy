import modbus_tk
import modbus_tk.modbus_tcp as modbus_tcp
import modbus_tk.defines as cst
import client
import pymysql
import threading
import time, random, json
import pika

# master = modbus_tcp.TcpMaster(host='192.168.5.47',port=7777)
# s = master.execute(slave=1, function_code = cst.READ_INPUT_REGISTERS, starting_address=0, quantity_of_x=10, output_value=5)

MSG_DATA  = 1
MSG_EVENT = 2
MSG_ERR   = 3
MSG_REG   = 4
statusDict = [1, 2, 3, 4, 5, 6,7]
data_dict = {}
event_dict = {}

KN_TYPE = {
  # 'manualReset' : 1,
  # 'digital' : 2,
  # 'trouble' : 2,
  # 'reset' : 1,
  # 'resetParams' : 1,
  # 'trigger' : 1,
  # 'params' : 1,
  'analog' : 1,
  # 'paramsHide' : 1,
  # 'triggerParams' : 1
}

db = pymysql.connect("localhost","root","admin123","scada")

cursor = db.cursor()
sql = "select abbr,type from device_property where device_type_id = 2 and category = 1"
cursor.execute(sql)
props = cursor.fetchall()
sql = "select id from device where is_root = true"
cursor.execute(sql)
devices = cursor.fetchall()
cursor.close()
print(devices)

def get_point():
  global data_dict, event_dict
  file = open('./DeviceProperty.txt', encoding = "utf-8")
  content = file.readlines()
  for line in content:
    rows = line.split(',')
    device_type = int(rows[1])
    type = int(rows[6])
    device_abbr = str(rows[2])
    if type == 1:
      if device_type not in data_dict:
          data_dict[device_type] = {}
      data_dict[device_type][device_abbr] = 0

    if type == 2:
      if device_type not in event_dict:
        event_dict[device_type] = {}
      event_dict[device_type][device_abbr] = 0

def rabbitmq():
  credentials = pika.PlainCredentials('admin', 'admin')
  connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',5672,'/',credentials))
  channel = connection.channel()
  channel.basic_qos(prefetch_count=1)
  rabbit_producer = channel
  rabbit_connect = connection
  return rabbit_producer

def device_register(device_sn, rabbit_producer):
  reg_data = []
  for key,abbr in data.items():
    if device_sn != key:
      reg_data.append({
        "sn": key,
        "type": key.split('.')[-1]
      })
    pass

  rabbit_producer.basic_publish(exchange='scada', routing_key='device.'+device_sn+'.'+str(MSG_REG), body=json.dumps(reg_data), properties=pika.BasicProperties(
        delivery_mode=2,
      ))
  pass

def mock_device_data(device_sn, n):
  global data_dict, event_dict
  rabbit_producer = rabbitmq()
  get_point()
  point_dict = data_dict
  device_data = {}
  device_event = {}
  send_index = 1
  device_props = {}
  start_time = time.time()
  while True:
    tim = int(time.time()*1000)
    # if len(device_data) == 0:
    #   for key,abbr in point_dict.items():
    #     device_props = { 'tim': int(time.time()*1000) }
    #     for k,v in abbr.items():
    #       if k =='turbineStaus':
    #         device_props[k] = statusDict[abs(int(7*random.random()))]
    #         print(device_props[k])
    #       elif k =='dayEnergy':
    #         device_props[k] = int(round(20*random.random(), 2))+30
    #       elif k =='monthEnergy':
    #         device_props[k] = int(round(200*random.random(), 2))+100
    #       elif k =='yearEnergy':
    #         device_props[k] = int(round(1000*random.random(), 2))+3000
    #       elif k =='windSpd3s':
    #         device_props[k] = int(round(5*random.random(), 2))
    #       elif k =='activePowerFromInverter':
    #         device_props[k] = int(round(100*random.random(), 2))+50
    #       elif k =='reActivePowerFromInverter':
    #         device_props[k] = -int(round(10*random.random(), 2))+10
    #       else:
    #         device_props[k] = int(round(50*random.random(), 2))
    #     if key == 2:
    #       device_data[device_sn] = device_props
    #     else:
    #       device_data[device_sn+'-'+str(key)] = device_props
    # else:
    #   status = device_data[device_sn]['turbineStaus']
    #   print(status)
    #   for key,value in device_data.items():
    #     value['tim'] = tim
    #     if status in [3,5,6,7]:
    #       device_data = device_data
    #       break
    #     else:
    #       for k,v in value.items():
    #         if k == 'dayEnergy' or k == 'monthEnergy' or k == 'yearEnergy':
    #           device_data[key][k] = v+1
    #         elif k =='windSpd3s':
    #           device_data[key][k] = int(round(5*random.random(), 2))
    #         elif k == 'turbineStaus':
    #           device_data[key][k] = status
    #         elif k != 'type':
    #           device_data[key][k] = int(round((v + random.uniform(-2, 2)), 2))
    #   device_data = device_data
    # if len(device_event) == 0:
    #   for key,abbr in event_dict.items():
    #     device_props = { 'tim': int(time.time()*1000) }
    #     for k,v in abbr.items():
    #       device_props[k] = 0
    #     if key == 2:
    #       device_event[device_sn] = device_props
    #     else:
    #       device_event[device_sn+'-'+str(key)] = device_props
    # else:
    #   for key,abbr in event_dict.items():
    #     device_props = { 'tim': int(time.time()*1000) }
    #     for k,v in abbr.items():
    #       device_props[k] = 0
    #       if send_index % 20 < 10:
    #         device_props[k] = 1
    #     if key == 2:
    #       device_event[device_sn] = device_props
    #     else:
    #       device_event[device_sn+'-'+str(key)] = device_props
    
    if send_index == 1:
      device_register(device_data, device_sn, rabbit_producer)
      time.sleep(2)

    send_index += 1
    # rabbit_producer.basic_publish(exchange='scada', routing_key='device.'+device_sn+'.'+str(MSG_DATA), body=json.dumps(device_data), properties=pika.BasicProperties(delivery_mode=2,))
    print('send ----- ' + device_sn )
    # rabbit_producer.basic_publish(exchange='scada', routing_key='device.'+device_sn+'.'+str(MSG_EVENT), body=json.dumps(device_event), properties=pika.BasicProperties(
    #   delivery_mode=2,
    # ))
    time.sleep(1)
  
def getProperty():
  props_dict = {}
  with open('./DeviceProperty_1.txt', 'r', encoding='utf-8') as f:
    content = f.readlines()
    for index in range(len(content)):
      line = content[index]
      params = line.replace('\n', '', 2).split(',')
      props_dict[params[3]] = params[2]
  return props_dict

def get_device_data(cfg, props, master):
  device_data = {
    '2': {
      'tim': int(time.time()*1000)
    }
  }
  for k,v in cfg.items():
    if k in KN_TYPE.keys():
      data = client.read_type_data(cfg, k, master)
      for item in data:
        key = item['name']
        value = item['value']
        # if item['type'] != "REAL" :
        #   device_data['2'][props[key]] = float('%.3f'%value)
        # else:
        device_data['2'][props[key]] = float('%.3f'%value)
  return device_data

def mock_data(device_sn, rabbit_producer):
  props_data = {
    device_sn: {
      'tim': int(time.time()*1000)
    }
  }
  print(time.time())
  for prop in props:
    if prop[1] == 'float':
      props_data[device_sn][prop[0]] = round(50*random.random(), 2)
    if prop[1] == 'int':
      props_data[device_sn][prop[0]] = int(round(50*random.random(), 2))
  rabbit_producer.basic_publish(exchange='scada', routing_key='device.'+device_sn+'.'+str(MSG_DATA), body=json.dumps(props_data), properties=pika.BasicProperties(delivery_mode=2,))
  
if __name__ == '__main__':
  rq = rabbitmq()
  # while True:
  #   mock_data('#9', rq)
  #   time.sleep(1)
  task = []
  # ip = '10.1.10.9'
  # master = modbus_tcp.TcpMaster(host=ip)
  # master.set_timeout(10.0)
  # cfg = client.read_cfg()
  # mq_producer = rabbitmq()
  # props = getProperty()
  # while True:
  #   device_data = get_device_data(cfg, props, master)
  #   print('----- send ----- ' )
  #   mq_producer.basic_publish(exchange='scada', routing_key='device.A9.'+str(MSG_DATA), body=json.dumps(device_data), properties=pika.BasicProperties(delivery_mode=2,))
  #   time.sleep(1)
  for item in devices:
    t = threading.Thread( target = mock_device_data, args=(item[0], 1), daemon=True)
    time.sleep(0.5)
    t.start()
    task.append(t)
  for t in task:  #等待所有子线程都退出
    t.join()  