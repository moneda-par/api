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
from tasks import *
from models import *
Base.metadata.create_all(get_engine())

from bts2helper import *

def get_my_last_block(db):
  q = db.query(Block)
  q = q.order_by(Block.block_num.desc())
  return q.first()

def undo_block(db, block):
  # Remove block from main chain
  db.query(Block).filter(Block.id == block.id).delete()
  db.flush()
 
  # Get previous
  return get_my_last_block(db)

def get_message(op):
  if 'memo' not in op: return None
  if 'message' not in op['memo']: return None
  return op['memo']['message']

def transfer_from_op(op, ts, new_block_id, block_num, trx_in_block, op_in_trx):

  print op
  
  to_id   = op[1]['to']
  from_id = op[1]['from']
  amount  = op[1]['amount']
  fee     = op[1]['fee']
  memo    = get_message(op[1])
  
  amount_asset = cache.get_asset(amount['asset_id'])
  fee_asset    = cache.get_asset(fee['asset_id'])

  transfer = Transfer(
    block_id     = new_block_id,
    from_id      = from_id,
    from_name    = cache.get_account(from_id)['name'],
    to_id        = to_id,
    to_name      = cache.get_account(to_id)['name'],
    amount       = amount['amount'],
    amount_asset = amount['asset_id'],
    fee          = fee['amount'],
    fee_asset    = fee['asset_id'],
    block_num    = block_num,
    trx_in_block = trx_in_block,
    op_in_trx    = op_in_trx,
    timestamp    = parse(ts),
    memo         = memo[:256] if memo else None,
    processed    = 0
  )
  
  return transfer

def do_import():
  try:
    with session_scope() as db:
      # My last block imported in DB
      my_block = get_my_last_block(db)

      # Network last block (head of master chain)
      dgp = rpc.db_get_dynamic_global_properties()
      #print dgp
      
      # Check participation rate
      pr = rpc.calc_participation_rate(int(dgp['recent_slots_filled']))
      if int(pr) < 80:
        print 'Participation rate too low'
        return
      
      last_block_num = dgp['head_block_number']
      
      while last_block_num > my_block.block_num:
        
        from_block = int(my_block.block_num+1)
        print from_block
        
        next_block = rpc.db_get_block_header(from_block)
        
        if next_block['previous'] != my_block.block_id:
          my_block = undo_block(db, my_block)
        else:
          
          to_block = min(from_block+100, last_block_num)
          
          blocks = rpc.db_get_blocks(from_block, to_block)
                    
          new_block = Block(
            block_num  = to_block,
            block_id   = bts2helper_block_id(json.dumps(blocks[-1]))
          )

          db.add(new_block)
          db.flush()
          total_c=0
	  errors_c=0
          for blk_inx, next_block in enumerate(blocks):
	    for trx_in_block, tx in enumerate(next_block['transactions']):
              
              ppp = tx
              try:
                to_sign = bts2helper_tx_digest(json.dumps(tx), CHAIN_ID)
		total_c+=1
		#print ' -- OK en to_sign'
              except Exception as ex:
		errors_c+=1
                #to_sign=None
		continue
		#print ' -- ERROR en to_sign'
		#print json.dumps(tx)
                #print str(ex)
	        #raise ex
              for le in db.query(LastError).filter(LastError.txid == to_sign).all():
                le.block_num = new_block.block_num
                le.trx_in_block = trx_in_block

              for op_in_trx, op in enumerate(tx['operations']):
                if not ( op[0] == 0 and op[1]['amount']['asset_id'] in ALL_TRACKED_ASSETS ):
                  continue
                t = transfer_from_op(op, next_block['timestamp'], new_block.id, from_block+blk_inx, trx_in_block, op_in_trx)
                db.add(t)
	  print '----'
          print 'Total = ', str(total_c)
	  print 'Errors = ', str(errors_c)
	  errors_c=0
	  total_c=0
          db.commit()
          my_block = new_block
      
  except Exception as ex:
    print ex
    logging.error(traceback.format_exc())

  
if __name__ == "__main__":

  while True:
    try:
      do_import()
      sleep(3)
    except Exception as ex:
      logging.error(traceback.format_exc())


  # with session_scope() as db:
  #   for t in db.query(Transfer).all():
  #     tx = rpc.db_get_transaction(t.block_num, t.trx_in_block)
  #     if 'memo' in tx['operations'][t.op_in_trx][1]:
  #       t.memo = tx['operations'][t.op_in_trx][1]['memo']['message'][:32]

  #   db.commit()
