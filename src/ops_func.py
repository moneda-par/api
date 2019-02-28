import os

from ops import *
from utils import *
from decimal import Decimal
import simplejson as json
from bts2helper import *

import rpc

# Helpers
def amount_of(asset, amount):
  int_amount = int(Decimal(amount)*Decimal(10**asset['precision']))
  return {'asset_id' : asset['id'], 'amount': int_amount}

def set_fees(ops, pay_in):
  fees = rpc.db_get_required_fees(ops, pay_in)
  for i in xrange(len(ops)):
    ops[i][1]['fee'] = fees[i]
  return ops

def build_tx_and_broadcast(ops, wif, signatures=[]):
  
  print "entro con signaturas => ", signatures
  tx = build_tx(
    ops,
    *ref_block(rpc.db_get_dynamic_global_properties()['head_block_id'])
  )
  
  if not wif:
    #print json.dumps(tx, indent=2)
    return tx

  if type(wif) != list:
    wif = [wif]
    
  to_sign = bts2helper_tx_digest(json.dumps(tx), CHAIN_ID)
  
  tx['signatures'] = signatures
  for w in wif:
    tx['signatures'].append( bts2helper_sign_compact(to_sign, w) )
  
  print 'Broadcasting...'
  print json.dumps(tx, indent=2)
  rpc.network_broadcast_transaction(tx)
  return to_sign

def set_fees_and_broadcast(ops, wif, pay_in):
  ops = set_fees(ops, pay_in)
  if not wif: return ops
  return build_tx_and_broadcast(ops, wif, [])

# OPS Func
def proposal_create(from_id, proposed_ops, wif=None):
  expiration_time = format_date(calc_expiration(datetime.utcnow(), 7200)) #1209600))
  pcop = proposal_create_op(from_id, proposed_ops, expiration_time)
  ops = [pcop]
  
  fees = rpc.db_get_required_fees(ops, CORE_ASSET)
  pcop[1]['fee'] = fees[0][0]
  
  build_tx_and_broadcast(ops, wif)

def transfer(from_id, to_id, asset, amount, memo=None, wif=None, pay_in=CORE_ASSET):
  t_op  = transfer_op( from_id, to_id, amount_of(asset, amount), memo )
  return set_fees_and_broadcast([t_op], wif, pay_in)

def asset_issue(issuer_id, to_account_id, asset, amount, wif=None, pay_in=CORE_ASSET):
  ai_op  = asset_issue_op( issuer_id, amount_of(asset, amount), to_account_id )
  return set_fees_and_broadcast([ai_op], wif, pay_in)

def proposal_delete(account_id, proposal_id, wif=None, pay_in=CORE_ASSET):
  pd_op = proposal_delete_op(account_id, proposal_id)
  return set_fees_and_broadcast([pd_op], wif, pay_in)
  
def asset_reserve(payer_id, asset, amount, wif=None, pay_in=CORE_ASSET):
  ar_op = asset_reserve_op(payer_id, amount_of(asset, amount))
  return set_fees_and_broadcast([ar_op], wif, pay_in)
  
def asset_update(issuer_id, asset_id, new_options, wif=None, pay_in=CORE_ASSET):
  au_op = asset_update_op(issuer_id, asset_id, new_options)
  return set_fees_and_broadcast([au_op], wif, pay_in)

def override_transfer(issuer_id, _from_id, to_id, asset, amount, wif=None, pay_in=CORE_ASSET):
  ot_op = override_transfer_op(issuer_id, _from_id, to_id, amount_of(asset, amount))
  return set_fees_and_broadcast([ot_op], wif, pay_in)

def account_update(account, owner=None, active=None, new_options=None, wif=None, pay_in=CORE_ASSET):
  au_op = account_update_op(account, owner, active, new_options)
  return set_fees_and_broadcast([au_op], wif, pay_in)

def asset_claim_fees(issuer, asset, amount, wif=None, pay_in=CORE_ASSET):
  acf_op = asset_claim_fees_op(issuer, amount_of(asset, amount))
  return set_fees_and_broadcast([acf_op], wif, pay_in)

def account_whitelist(authorizing_account_id, account_id_to_list, new_listing, wif=None, pay_in=CORE_ASSET):
  aw_op = account_whitelist_op(authorizing_account_id, account_id_to_list, new_listing)
  return set_fees_and_broadcast([aw_op], wif, pay_in)

def withdraw_permission_create(withdraw_from_account_id, authorized_account_id, withdrawal_limit, withdrawal_period_sec, periods_until_expiration, period_start_time, wif=None, pay_in=CORE_ASSET):
  wpc_op = withdraw_permission_create_op(withdraw_from_account_id, authorized_account_id, withdrawal_limit, withdrawal_period_sec, periods_until_expiration, period_start_time)
  return set_fees_and_broadcast([wpc_op], wif, pay_in)
