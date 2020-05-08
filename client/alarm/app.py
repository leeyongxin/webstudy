import os, time
from urllib import parse,request
import pygame
import tkinter
import tkinter.messagebox

REQUEST_URL = 'http://61.182.134.97/wmc/dataPMC'

root = tkinter.Tk()
root.withdraw()

def audio_init():
  pygame.mixer.init()
  track = pygame.mixer.music.load("alarm.wav")

def get_data():
  try:
    data = {
      'tags[]': 'HBJT:HX:HX_TT|CALC_AGC2'
    }
    # response = requests.post(REQUEST_URL, data = {
    #   'tags[]': 'HBJT:HX:HX_TT|CALC_AGC2'
    # })
    req = request.Request(url = REQUEST_URL, data = parse.urlencode(data).encode(encoding='utf-8'))
    res = request.urlopen(req)
    res_data = eval(res.read().decode(encoding='utf-8'))
    if res_data and len(res_data) > 0:
      return float(res_data[0])
    else:
      return False
  except Exception as e:
    print(e)
    return False
    
  
if __name__ == "__main__":
  print('初始化...')
  audio_init()
  last_agc = None
  is_lost = False
  while True:
    print('开始获取...')
    res = get_data()
    if res == False and is_lost == False:
      is_lost = True
      pygame.mixer.music.play()
      tkinter.messagebox.showerror('错误','与服务器失去连接！')
    else:
      is_lost = False
      if last_agc == None:
        last_agc = res
      else:
        diff = abs(last_agc - res)
        print('上一次AGC %s , 当前AGC %s , 差值%s' %(str(last_agc), str(res), str(diff)))
        last_agc = res
        if diff >= 1:
          pygame.mixer.music.play()
          tkinter.messagebox.showwarning('','前后5秒AGC下发值差距超过1MW！')
    time.sleep(5)