from flask import Flask, abort, request, jsonify, render_template
import modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus_tcp as modbus_tcp
from datetime import datetime
import client
HOST_ADDR      = "10.211.55.4"
PORT           = 502
SLAVE_INDEX    = 1
master = None

CTRL_MODE = {
  0: [(1, 1625, 1), (1, 1625, 0)], # 启动
  1: [(1, 1626, 1), (1, 1626, 0)], # 停止
  2: [(1, 1627, 1), (1, 1627, 0)], # 复位 
  3: [(1, 1627, 1), (1, 1625, 0), (1, 1627, 0), (1, 1625, 0)], # 重启 -> 复位+启动
  5: [(1, 1628, 1), (1, 1628, 0)], # setPlcYawLeft
  6: [(1, 1629, 1), (1, 1629, 0)], # setPlcYawRight
  7: [(1, 1630, 1), (1, 1630, 0)], # setPlcYawCloseAuto
  8: [(1, 1631, 1), (1, 1631, 0)], # setPlcYawStop
  9: [(1, 1661, 1)], # enableActivePowerLimit
  10: [(1, 1661, 0)], # disableActivePowerLimit
  11: [(1, 1616, 1), (1, 1616, 0)], # setPlcAbmqEnable
  12: [(1, 1617, 1), (1, 1617, 0)], # setPlcBbmqEnable
  13: [(1, 1662, 1)], # enableReactivePowerLimit
  14: [(1, 1662, 0)], # disableReactivePowerLimit
  15: [(1, 1607, 1), (1, 1607, 0)], # setPlcSetTimeEnableFlag
  16: [(1, 1151), (1, 1661, 1)],
  17: [(1, 1149), (1, 1662, 1)],
  18: [(1, 1153)],
}
cfg = client.read_cfg()

app = Flask(__name__)
analog_data = None
digital_data = None
params_data = None

@app.route("/")
def index():
  return render_template("index.html")

@app.route('/set', methods=['POST'])
def read_set():
  global master, HOST_ADDR
  if not request.form or 'ip' not in request.form:
    return jsonify({'code': 100})
  ip = request.form['ip']
  if len(ip.split('.')) != 4:
    return jsonify({'code': 101})
  if master != None and HOST_ADDR == ip:
    return jsonify({'code': 0})
  try:
    HOST_ADDR = ip
    master = modbus_tcp.TcpMaster(host=HOST_ADDR, port=PORT)
    master.set_timeout(3.0)
  except:
    return jsonify({'code': 102})
  
  return jsonify({'code': 0})

@app.route('/params', methods=['GET'])
def read_params():
  global cfg, params_data, master
  params_data = client.read_params(cfg, master)
  return jsonify({'code': 0, 'params': params_data})

@app.route('/type', methods=['GET'])
def read_type_data():
  global cfg, params_data, master
  v_type = request.args.get('type')
  print(v_type)
  params_data = client.read_type_data(cfg, v_type, master)
  return jsonify({'code': 0, str(v_type): params_data})

# @app.route('/save', methods=['GET'])
# def save():
#   global analog_data, digital_data
#   txt = []
#   for item in analog_data:
#     txt.append(item['name'] + ':' + str(item['value']))
#   print('\n'.join(txt))
#   with open("./static/record.txt","w") as f:
#     f.write('\n'.join(txt))
#   f.close()
#   return jsonify({'code': 0, 'url': './static/record.txt'})

@app.route('/ctrl', methods=['POST'])
def ctrl():
  if not request.form or 'ip' not in request.form or 'ctrl' not in request.form:
    return jsonify({'code': 100})
  print(CTRL_MODE[int(request.form['ctrl'])])
  res = client.byte_ctrl(CTRL_MODE[int(request.form['ctrl'])], request.form['ip'])
  return jsonify({'code': 0,})

@app.route('/write', methods=['POST'])
def write():
  if not request.form or 'ip' not in request.form or 'ctrl' not in request.form or 'value' not in request.form or 'category' not in request.form:
    return jsonify({'code': 100})
  res = client.write_ctrl(request.form['value'], request.form['ip'], request.form['category'], CTRL_MODE[int(request.form['ctrl'])])
  return jsonify({'code': 0,})

@app.route('/params_write', methods=['POST'])
def params_write():
  global master
  if not request.form or 'ip' not in request.form or 'value' not in request.form or 'type' not in request.form or 'address' not in request.form :
    return jsonify({'code': 100})
  client.params_write(request.form['value'], request.form['type'], request.form['address'], master)
  return jsonify({'code': 0,})

if __name__ == '__main__':
  app.run(host="0.0.0.0", port=8383, debug=True)