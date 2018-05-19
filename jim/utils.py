import json

# Кодировка
ENCODING = 'utf-8'

# 1. словарь в json
def encode(msg):
    #print(type(msg))
    msg_json = json.dumps(msg)
    #print(type(msg_json))
    msg_b = msg_json.encode(ENCODING)
    #print(type(msg_b))
    return msg_b

# 2. наоборот
# байты в строку
def decode(bmsg):
    jmsg = bmsg.decode(ENCODING)
    # строку в словарь
    msg = json.loads(jmsg)
    #print(msg)
    return msg