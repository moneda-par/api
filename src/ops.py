from datetime import datetime
from dateutil.relativedelta import relativedelta

from utils import *

def calc_expiration(now, seconds):
  return now+relativedelta(seconds=seconds)

def format_date(date):
  return date.strftime('%Y%m%dT%H%M%S')

def build_tx(ops, ref_block_num, ref_block_prefix, expiration=120):
  return  {
    'expiration'        : format_date(calc_expiration(datetime.utcnow(), expiration)),
    'ref_block_num'     : ref_block_num,
    'ref_block_prefix'  : ref_block_prefix,
    'operations'        : ops
  }

def asset_claim_fees_op(issuer, amount_to_claim, fee=None):
  tmp = [43, {
    'issuer'          : issuer,
    'amount_to_claim' : amount_to_claim
  }]
  
  if fee : tmp[1]['fee']  = fee
  return tmp  
  
def override_transfer_op(issuer, _from, to, amount, memo=None, fee=None):
  tmp = [38, {
    'issuer' : issuer,
    'from'   : _from,
    'to'     : to,
    'amount' : amount
  }]
  
  if fee : tmp[1]['fee']  = fee
  if memo: tmp[1]['memo'] = memo
  
  return tmp  

def withdraw_permission_create_op(withdraw_from_account, authorized_account, withdrawal_limit, withdrawal_period_sec, periods_until_expiration, period_start_time, fee=None):
  tmp = [25, {
      'withdraw_from_account'    : withdraw_from_account,
      'authorized_account'       : authorized_account,
      'withdrawal_limit'         : withdrawal_limit,
      'withdrawal_period_sec'    : withdrawal_period_sec,
      'periods_until_expiration' : periods_until_expiration,
      'period_start_time'        : period_start_time
  }]

  if fee: tmp[1]['fee'] = fee
  return tmp

def proposal_delete_op(fee_paying_account, proposal, using_owner_authority=False, fee=None):
  tmp = [24, {
      'fee_paying_account'    : fee_paying_account,
      'proposal'              : proposal,
      'using_owner_authority' : using_owner_authority 
  }]

  if fee: tmp[1]['fee'] = fee
  return tmp

def account_whitelist_op(authorizing_account, account_to_list, new_listing, fee=None):
  tmp = [7, {
    'authorizing_account' : authorizing_account,
    'account_to_list'     : account_to_list,
    'new_listing'         : new_listing
  }]
  
  if fee: tmp[1]['fee'] = fee
  return tmp

def asset_update_op(issuer, asset_to_update, new_options, new_issuer=None, fee=None):
  tmp = [11, {
    'issuer'          : issuer,
    'asset_to_update' : asset_to_update,
    'new_options'     : new_options
  }]

  if fee: tmp[1]['fee'] = fee
  if new_issuer: tmp[1]['new_issuer'] = new_issuer    
  return tmp

def asset_reserve_op(payer, amount_to_reserve, fee=None):
  tmp = [15, {
    'payer'             : payer,
    'amount_to_reserve' : amount_to_reserve,
  }]

  if fee: tmp[1]['fee'] = fee
  return tmp

def proposal_create_op(fee_paying_account, proposed_ops, expiration_time, review_period_seconds=0, fee=None):
  tmp = [22, {
    'fee_paying_account'    : fee_paying_account,
    'proposed_ops'          : [{'op':op} for op in proposed_ops],
    'expiration_time'       : expiration_time,
  }]

  if review_period_seconds: tmp[1]['review_period_seconds'] = review_period_seconds 
  if fee: tmp[1]['fee'] = fee

  return tmp
    
def asset_issue_op(issuer, asset_to_issue, to_account, memo=None, fee=None):
  tmp = [14, {
    'issuer'           : issuer, 
    'asset_to_issue'   : asset_to_issue,
    'issue_to_account' : to_account
  }]
  
  if memo: tmp[1]['memo'] = memo
  if fee : tmp[1]['fee']  = fee

  return tmp

def account_update_op(account, owner, active, new_options, fee=None):

  tmp = [6, {
    'account' : account,
  }]
  
  if owner : tmp[1]['owner']  = owner
  if active : tmp[1]['active']  = active
  if new_options : tmp[1]['new_options']  = new_options
  
  if fee : tmp[1]['fee']  = fee

  return tmp

def register_account_op(registrar, referrer, referrer_percent, name, owner, active, memo, voting_account, fee=None):
  tmp = [5, {
    'registrar'         : registrar,
    'referrer'          : referrer,
    'referrer_percent'  : referrer_percent,
    'name'              : name,
    'owner'             : owner,
    'active'            : active,
    'options' : {
      'memo_key'       : memo,
      'voting_account' : voting_account
    }
  }]

  if fee : tmp[1]['fee']  = fee

  return tmp

def transfer_op(_from, _to, amount, memo=None, fee=None):
  tmp = [
    0,
    {
      "from"   : _from,
      "to"     : _to,
      "amount" : amount,
    }
  ]

  if fee : tmp[1]['fee']  = fee
  if memo: tmp[1]['memo'] = memo

  return tmp
