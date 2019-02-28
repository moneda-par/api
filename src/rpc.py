from config import *
import os
import sys
import decimal
import requests
import simplejson as json
import traceback
import logging

# import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1

# # You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True


#BITSHARES_RPC_NODE = os.environ.get('BITSHARES_RPC_NODE', 'http://localhost:8090/rpc')
# print 'using RPC @ ', BITSHARES_RPC_NODE

class RpcError(Exception):
  def __init__(self, message, code):
    # Call the base class constructor with the parameters it needs
    super(RpcError, self).__init__(message)
    self.code = code

API_ID = {
  'db'      : "database",
  'network' : "network_broadcast",
  'history' : "history",
  "asset"   : "asset",
  "block"   : "block" 
}

def call_rpc_impl(api, method, *params):
  url     = BITSHARES_RPC_NODE
  headers = {
    'content-type'  : 'application/json',
    #'Authorization' : 'Basic Ynl0ZW1hc3RlcjpzdXBlcnNlY3JldA=='
  }
  
  auth    = ('kkuser', 'supersecret')

  payload2 =  {
      "method": "call",
      "params": [API_ID[api], method] + [p for p in params],
      "jsonrpc": "2.0",
      "id": 10
  }

  r = requests.post(url, data=json.dumps(payload2), headers=headers, auth=auth, timeout=5)

  res = json.loads(r.text, parse_float=decimal.Decimal)
  if 'result' in res:
    return res['result']
  if 'code' in res['error']:
    print res['error']
    raise RpcError(res['error']['message'], res['error']['code'])
  else:
    raise RpcError(res['error']['message'], 6969696969)

def call_rpc(api, method, *params):
  try:
    return call_rpc_impl(api, method, params)
  except Exception as e:
    print traceback.format_exc()
    exc_info = sys.exc_info()
    raise exc_info[0], exc_info[1], exc_info[2]
  
#--- new 2.x 
def db_get_objects(objects):
  return call_rpc('db', 'get_objects', objects)

def db_get_asset_holders(asset_id):
  return call_rpc('asset', 'get_asset_holders', asset_id)

def db_get_key_references(key):
  return call_rpc('db', 'get_key_references', key)

def db_get_assets(assets):
  return call_rpc('db', 'get_assets', assets)

def db_get_full_accounts(accounts, subscribe):
  return call_rpc('db', 'get_full_accounts', accounts, subscribe)

def db_get_block_header(block_num):
  return call_rpc('db', 'get_block_header', block_num)

def db_get_block(block_num):
  return call_rpc('db', 'get_block', block_num)

def db_get_blocks(block_num_from, block_num_to):
  return call_rpc('block', 'get_blocks', block_num_from, block_num_to)

def db_get_accounts(account_ids):
  return call_rpc('db', 'get_accounts', account_ids)

def db_get_account_by_name(name):
  return call_rpc('db', 'get_account_by_name', name)

def db_get_account_balances(account, assets=[]):
  return call_rpc('db', 'get_account_balances', account, assets)

def history_get_relative_account_history(account, stop=0, limit=100, start=0):
  return call_rpc('history', 'get_relative_account_history', account, stop, limit, start)

def history_get_account_history(account, stop='', limit=100, start=''):
  return call_rpc('history', 'get_account_history', account, stop, limit, start)

def db_get_transaction(block_num, trx_in_block):
  return call_rpc('db', 'get_transaction', block_num, trx_in_block)

def db_get_required_fees(ops, asset_id):
  if type(ops) != list: ops = [ops]
  return call_rpc('db', 'get_required_fees', ops, asset_id)

def db_get_global_properties():
  return call_rpc('db', 'get_global_properties')

def db_get_dynamic_global_properties():
  return call_rpc('db', 'get_dynamic_global_properties')
  
def db_get_chain_properties():
  return call_rpc('db', 'get_chain_properties')

def db_lookup_accounts(lower_bound_name, limit):
  return call_rpc('db', 'lookup_accounts', lower_bound_name, limit)  

def db_lookup_account_names(names):
  return call_rpc('db', 'lookup_account_names', names)  

def network_broadcast_transaction(tx):
  return call_rpc('network', 'broadcast_transaction', tx)

def network_broadcast_transaction_sync(tx):
  return call_rpc('network', 'broadcast_transaction_synchronous', tx)

def participation_rate():
  return calc_participation_rate(int(db_get_dynamic_global_properties()['recent_slots_filled']))

def calc_participation_rate(recent_slots_filled):
  return bin(recent_slots_filled).count('1')*100.0/128.0
