import os
import websocket
import thread
import time
import traceback
import logging

import requests
import json
import rpc
import cache

from time import sleep
from utils import *
from config import *
from models import *

print 'using BITSHARES_WS_NODE =>', BITSHARES_WS_NODE
 
def send_notification(account_name, message):

  player_id = None
  with session_scope() as db:
    pi = db.query(PushInfo).filter(PushInfo.name == account_name).first()
    player_id = pi.push_id if pi else None
      
  if not player_id:
    print 'No encontre el player_id de =>', account_name
    return
  
  print "FOUND =>", account_name, "=", player_id 
  
  header = {"Content-Type": "application/json; charset=utf-8",
            "Authorization": "Basic 123456789"}

  payload = {
    "app_id"             : ONE_SIGNAL_APP_ID,
    "small_icon"         : "ic_iconoclasa.png",
    "include_player_ids" : [player_id],
    "android_sound"     : "coins_received",
    #"filters"           : [
    #    {"field": "tag", "key": "account", "relation": "=", "value": account_name}, 
    #],
    "contents"          : {
      "en" : message
    }
  }
   
  print json.dumps(payload)
    
  req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
  print(req.status_code, req.reason)

#send_notification("matu", "Va mas platilli")

def run_again():
  ws = websocket.WebSocketApp(BITSHARES_WS_NODE,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
  ws.on_open = on_open
  ws.run_forever()  

def on_message(ws, message):
  #print message
  m = json.loads(message)
  #print m

  if 'method' in m and m['method'] == 'notice' and m['params'][0] == 1:
    for block_id in m['params'][1]:

      try :
        block = rpc.db_get_block( int(block_id[0:8], 16) )
        if not block: continue

        to_ids   = []
        from_ids = []
        amounts  = []
        
        for tx in block['transactions']:
          for op in tx['operations']:
            if op[0] == 0 and op[1]['amount']['asset_id'] == ASSET_ID:
              to_ids.append(op[1]['to'])
              from_ids.append(op[1]['from'])
              amounts.append(op[1]['amount']['amount'])

        if len(to_ids) > 0:
          froms = rpc.db_get_accounts(from_ids)
          tos   = rpc.db_get_accounts(to_ids)
          
          asset = cache.get_asset(ASSET_ID)
          
          for i in xrange(len(froms)):
            f = real_name(froms[i]['name'])
            t = real_name(tos[i]['name'])
            a = amount_value(amounts[i],asset)
            
            msg = '{0} has sent you {1} PAR'.format(f, a)
            print t, msg
            send_notification(t, msg)
      
      except Exception as ex:
        print ex
        logging.error(traceback.format_exc())

  #     #print 'pidiendo bloque => ', int(block_id[0:8], 16)
  #     ws.send(
  #       json.dumps( {"id":1000, "method":"call", "params":[0, "get_block", []]} )
  #     )
  
  # elif 'id' in m and m['id'] == 1000 and 'result' in m:
  #   print len(m['result']['transactions'])
  #   for tx in m['result']['transactions']:
  #     for op in tx['operations']:
  #       if op[0] == 0:
  #         print op[1]['to']

def on_error(ws, error):
  print error

def on_close(ws):
  print "### closed ###"
  sleep(5)
  run_again()

def on_open(ws):
  ws.send(
    json.dumps( {"id":1, "method":"call", "params":[0, "set_block_applied_callback", [1]]} )
  )
  # def run(*args):
  #     for i in range(3):
  #         time.sleep(1)
  #         ws.send("Hello %d" % i)
  #     time.sleep(1)
  #     ws.close()
  #     print "thread terminating..."
  # thread.start_new_thread(run, ())

if __name__ == "__main__":
  #websocket.enableTrace(True)
  run_again()
