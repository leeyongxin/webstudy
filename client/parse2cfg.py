import os
import urllib.parse
import http.client
import random
import hashlib
import json
import pymysql
# 中译英
appKey = '0de6af61fc8aa166'
secretKey = 'HjspypqdVlTRwU42omrpPEZBfVY0dw25'
appId = '20191116000357662'
appSK = 'Omb6LsWksLLfiuzh5tEc'
# def saveProperty():
#     with open('./DeviceProperty_1.txt', 'r', encoding='utf-8') as f:
#         content = f.readlines()
#         for index in range(len(content)):
#             line = content[index]
#             params = line.replace('\n', '', 2).split(',')
#             sql = """INSERT INTO device_property(id, device_type_id, abbr, name, category, type) VALUES (%d, %d, '%s', '%s', %d, '%s');"""%(
#                         int(params[0]),
#                         2,
#                         params[2],
#                         params[3],
#                         1,
#                         params[9],
#                     )
#             print(sql)
#             cursor.execute(sql)
#     db.close()

del_word = ['of', 'is', 'the', 'button', 'for', 'does', 'to', 'too', 'a']
def Ch2En(item):
    httpClient = None
    myurl = '/api'
    fromLang = 'zh-CHS'  # 译文主体
    toLang = 'EN'  # 译文客体
    salt = random.randint(1, 65536)
    sign = appKey + item + str(salt) + secretKey
    m1 = hashlib.new('md5')
    m1.update(sign.encode("utf-8"))
    sign = m1.hexdigest()
    # 拼接完整译文对象
    myurl = myurl + '?appKey=' + appKey + '&q=' + urllib.parse.quote(
        item) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign
    result = ""
    try:
        httpClient = http.client.HTTPConnection('openapi.youdao.com')
        httpClient.request('GET', myurl)
        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result = json.loads(response.read().decode("utf-8"))['translation'][0].split(' ')
    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()
    return result

if __name__ == '__main__':
    # saveProperty()
    en_arr = []
    with open('./DeviceProperty.csv', 'r', encoding='utf-8') as f:
        w = open('./DeviceProperty1.csv', 'r+', encoding='utf-8')
        content = f.readlines()
        l = len(content)
        for index in range(l):
            print(index, l)
            line = content[index].replace('\n', '', 2)
            params = line.split(',')
            name = params[1]
            typeStr = params[4]
            if len(params) >7:
                full = params[6]
                abbr = params[7]
                en_arr.append(typeStr+params[7])
            else:
                c2e = Ch2En(name)
                en = ''
                en_l = ''
                for ch in c2e:
                    if ch not in del_word:
                        en_l = en_l + ch.capitalize()
                        if ch.isalpha():
                            en = en + ch[0].lower()
                        else:
                            en = en + ch
                if (typeStr+en) in en_arr:
                    params.append(en_l)
                    params.append('re-' + en)
                else:
                    params.append(en_l)
                    params.append(en)
                print(en)
                en_arr.append(typeStr+en)
            w.write(','.join(params)+'\n')
    w.close()
