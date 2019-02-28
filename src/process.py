import os

import traceback
import websocket
import thread
import time
from dateutil.parser import parse

import requests
import json
import rpc
import cache

from time import sleep
from utils import *
from config import *
from tasks import *
from models import *
from ops_func import *

from bts2helper import *
from credit_func import multisig_set_overdraft

valid_assets = ONLY_VALID_ENDORSEMENT_TOKENS

def user_authorize_user(t):

  to            = t.memo[8:].decode('hex')
  to_id         = cache.get_account_id(unicode(ACCOUNT_PREFIX + to))
  from_name     = real_name(t.from_name)
  endorse_type  = t.amount_asset

  if endorse_type not in valid_assets:
    raise Exception('invalid_endorsement')

  p = rpc.db_get_account_balances(to_id, [OVERDRAFT_ASSET_ID])
  if p[0]['amount'] > 0:
    raise Exception('already_have_credit')

  if to_id in rpc.db_get_accounts([ENDORSEMENT_ADMIN_ACCOUNT_ID])[0]['blacklisted_accounts']:
    raise Exception('already_endorsed')

  asset = rpc.db_get_assets([endorse_type])[0]
  memo  = {
    'message' : '~eb:{0}'.format(from_name).encode('hex')
  }

  tx = build_tx_and_broadcast(
      transfer(
        ENDORSEMENT_ADMIN_ACCOUNT_ID,
        to_id,
        asset,
        1,
        memo
      ) + account_whitelist(
        ENDORSEMENT_ADMIN_ACCOUNT_ID,
        to_id,
        2 #insert into black list
      )
    , None)

  to_sign = bts2helper_tx_digest(json.dumps(tx), CHAIN_ID)
  signature = bts2helper_sign_compact(to_sign, REGISTER_PRIVATE_KEY)
  tx['signatures'] = [signature]

  print tx
  p = rpc.network_broadcast_transaction(tx)
  return to_sign

def user_applies_authorization(t):

  print "ENTER => user_applies_authorization"

  endorse_type  = t.amount_asset

  if endorse_type not in valid_assets:
    raise Exception('invalid_endorsement')

  p = rpc.db_get_account_balances(t.from_id, [OVERDRAFT_ASSET_ID])
  if p[0]['amount'] > 0:
    raise Exception('already_have_credit')

  amount = 0
  if endorse_type == ENDORSE_ASSET_IDx1000:
    amount = 1000
  elif endorse_type == ENDORSE_ASSET_IDx10000:
    amount = 10000
  elif endorse_type == ENDORSE_ASSET_IDx30000:
    amount = 30000
  else:
    raise Exception('invalid_endorse')  

  accounts_to_issue = {
    t.from_name  : amount,
  }

  # HACK : poner las privadas en orden y los owner de los assets
  multisig_set_overdraft(accounts_to_issue)

def user_transfer_authorizations(t):
  
  to            = t.memo[8:].decode('hex')
  to_id         = cache.get_account_id(unicode(ACCOUNT_PREFIX + to))
  from_name     = real_name(t.from_name)
  endorse_type  = t.amount_asset

  if to_id in rpc.db_get_accounts([ENDORSEMENT_ADMIN_ACCOUNT_ID])[0]['blacklisted_accounts']:
    raise Exception('unable_to_receive')

  asset = rpc.db_get_assets([endorse_type])[0]
  memo = {
    'message' : '~et:{0}'.format(from_name).encode('hex')
  }

  tx = build_tx_and_broadcast(
      transfer(
        ENDORSEMENT_ADMIN_ACCOUNT_ID,
        to_id,
        asset,
        t.amount,
        memo
      )
    , None)

  to_sign = bts2helper_tx_digest(json.dumps(tx), CHAIN_ID)
  signature = bts2helper_sign_compact(to_sign, REGISTER_PRIVATE_KEY)
  tx['signatures'] = [signature]

  print tx
  p = rpc.network_broadcast_transaction(tx)
  return to_sign

def do_process():
  try:
    
    with session_scope() as db:
      q = db.query(Transfer)
      q = q.filter(Transfer.processed == 0)
      q = q.order_by(Transfer.id)
      q = q.limit(100)

      for t in q.all():

        last_err = None

        try:        
          # Operaciones de avales
          if t.amount_asset in ALL_ENDORSE_ASSETS_ID and t.to_id == ENDORSEMENT_ADMIN_ACCOUNT_ID:

            print '------'
            print t.id
            print t.memo

            txid = None
            # usuario1 transfiere a gobierno AVAL(i) con memo '~ie:nombre'
            # accion => autorizar a usuario (a.b.c)
            if t.memo and t.memo[:8] == '~ie:'.encode('hex'):
              txid = user_authorize_user(t)
            
            # usuario2 transfiere a gobierno AVAL(i) con memo '~ae'
            # accion => usuario2 quiere credito
            elif t.memo and t.memo == '~ae'.encode('hex'):
              txid = user_applies_authorization(t)
            
            # usuario3 transfiere a gobierno AVAL(i) con memo '~et:nombre'
            # accion => usuario3 transfiere avales a usuario a.b.c
            elif t.memo and t.memo[:8] == '~et:'.encode('hex'):
              txid = user_transfer_authorizations(t)

            t.processed = 1
  
            if txid:
              last_err, ok = get_or_create(db, LastError, transfer_id=t.id)
              last_err.txid = txid
              last_err.description = 'ok'

            #db.add(last_err)
          
          # Otras transferencias
          else:
            t.processed = 1

        except Exception as ex:
          
          print '******************************* %d' % t.id          
          print traceback.format_exc()

          t.processed = -1
          last_err, ok = get_or_create(db, LastError, transfer_id=t.id)
          last_err.description = str(ex)
          db.add(last_err)

        finally:
          db.commit()

  except Exception as ex:
    print ex
    logging.error(traceback.format_exc())

if __name__ == "__main__":
  while True:
    try:
      do_process()
      sleep(3)
    except Exception as ex:
      logging.error(traceback.format_exc())
