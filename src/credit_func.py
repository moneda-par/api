import os
import rpc
import simplejson as json

from ops_func import *

from config import *

accounts              = {}
assets                = {}
assets_by_id          = {}

def account_id(name):
  return accounts[name]['account']['id']

def asset_id(name):
  return assets[name.upper()]['id']

def init(other_accounts):
  global accounts
  accounts = { a[0]:a[1] for a in rpc.db_get_full_accounts(list(set([MAIN_ASSET_ADMIN_ACCOUNT_ID, ENDORSEMENT_ADMIN_ACCOUNT_ID]+other_accounts)), False) }
  
  global assets
  global assets_by_id
  assets = { a['symbol']:a for a in rpc.db_get_assets(ALL_TRACKED_ASSETS) }
  assets_by_id = { assets[k]['id']:assets[k] for k in assets }

def ops_for_remove(account_name, amount):
  res = override_transfer( 
    MAIN_ASSET_ADMIN_ACCOUNT_ID,
    account_id(account_name),
    MAIN_ASSET_ADMIN_ACCOUNT_ID,
    assets_by_id[CURRENCY_ASSET_ID],
    amount
  ) + asset_reserve(
    MAIN_ASSET_ADMIN_ACCOUNT_ID, 
    assets_by_id[CURRENCY_ASSET_ID], 
    amount
  ) + override_transfer( 
    MAIN_ASSET_ADMIN_ACCOUNT_ID,
    account_id(account_name),
    MAIN_ASSET_ADMIN_ACCOUNT_ID,
    assets_by_id[OVERDRAFT_ASSET_ID],
    amount
  ) + asset_reserve(
    MAIN_ASSET_ADMIN_ACCOUNT_ID, 
    assets_by_id[OVERDRAFT_ASSET_ID], 
    amount
  )

  return res

def ops_for_whitelist(account_name):
  res = account_whitelist(
    MAIN_ASSET_ADMIN_ACCOUNT_ID,
    account_id(account_name),
    1 #insert into white list
  ) + account_whitelist(
    MAIN_ASSET_ADMIN_ACCOUNT_ID,
    account_id(account_name),
    0 #remove from list (white or black)
  )
  return res

def ops_for_issue(account_name, amount):
  res = asset_issue( 
    MAIN_ASSET_ADMIN_ACCOUNT_ID,
    account_id(account_name),
    assets_by_id[CURRENCY_ASSET_ID],
    amount
  ) + asset_issue( 
    MAIN_ASSET_ADMIN_ACCOUNT_ID,
    account_id(account_name),
    assets_by_id[OVERDRAFT_ASSET_ID],
    amount
  ) 
  return res
#print json.dumps(res, indent=2)

# Multisig proposals
def multisig_set_overdraft(accounts_to_issue):

  init(list(accounts_to_issue))

  ops = []
  for account, new_desc in accounts_to_issue.iteritems():

    balances = rpc.db_get_account_balances(account_id(account), [assets_by_id[CURRENCY_ASSET_ID]['id'], assets_by_id[OVERDRAFT_ASSET_ID]['id']])
    assert(balances[0]['asset_id'] == assets_by_id[CURRENCY_ASSET_ID]['id']), "Invalid 0 balance"
    assert(balances[1]['asset_id'] == assets_by_id[OVERDRAFT_ASSET_ID]['id']), "Invalid 1 balance"
    
    par  = Decimal(amount_value( balances[0]['amount'], assets_by_id[CURRENCY_ASSET_ID] ))
    desc = Decimal(amount_value( balances[1]['amount'], assets_by_id[OVERDRAFT_ASSET_ID] ))

    ops_w = ops_for_whitelist(account)

    if desc > new_desc:
      to_remove = desc - new_desc
      assert( par - to_remove >= 0 ), "account {0} => no hay par({1}) suficiente para sacar ({2})".format(account, par, to_remove)
      ops_w[1:1] = ops_for_remove(account, to_remove)
      ops.extend( ops_w )
    elif desc < new_desc:
      to_add = new_desc - desc
      ops_w[1:1] = ops_for_issue(account, to_add)
      ops.extend( ops_w )

    # Lo limpiamos de la blacklist de propuesta (para q pueda recibir avals)  
    ops += account_whitelist(
      ENDORSEMENT_ADMIN_ACCOUNT_ID,
      account_id(account),
      0 #remove from black list
    )

  assert( len(ops) > 0 ), "No hay operaciones parar realizar"
  #print json.dumps(ops, indent=2)
  #return

  return set_fees_and_broadcast(ops, [ADMIN_PRIVATE_KEY], CORE_ASSET)
  #res = proposal_create(ENDORSEMENT_ADMIN_ACCOUNT_ID, ops, REGISTER_PRIVATE_KEY)

def multisig_delete_proposal(proposal_id):
  init([])
  ops = proposal_delete(MAIN_ASSET_ADMIN_ACCOUNT_ID, proposal_id)
  res = proposal_create(ENDORSEMENT_ADMIN_ACCOUNT_ID, ops, REGISTER_PRIVATE_KEY) #)

def WARNING_multisig_bring_them_all_proposal(account):
  init([])
  
  ops = []
  for u in rpc.db_get_asset_holders(assets_by_id[CURRENCY_ASSET_ID]['id']):
    #if u['name'] == 'gobierno-par': continue
    if u['name'] != account: continue

    if u['amount'] == 0: continue
    ops.extend( 
      override_transfer( 
        MAIN_ASSET_ADMIN_ACCOUNT_ID, 
        u['account_id'], 
        MAIN_ASSET_ADMIN_ACCOUNT_ID,
        assets_by_id[CURRENCY_ASSET_ID], 
        Decimal(amount_value(u['amount'], assets_by_id[CURRENCY_ASSET_ID]))
      )
    )

  for u in rpc.db_get_asset_holders(assets_by_id[OVERDRAFT_ASSET_ID]['id']):
    #if u['name'] == 'gobierno-par': continue
    if u['name'] != account: continue

    if u['amount'] == 0: continue
    ops.extend( 
      account_whitelist(
        MAIN_ASSET_ADMIN_ACCOUNT_ID,
        u['account_id'],
        1 #insert into white list
      ) + override_transfer( 
        MAIN_ASSET_ADMIN_ACCOUNT_ID, 
        u['account_id'], 
        MAIN_ASSET_ADMIN_ACCOUNT_ID,
        assets_by_id[OVERDRAFT_ASSET_ID], 
        Decimal(amount_value(u['amount'], assets_by_id[OVERDRAFT_ASSET_ID]))
      ) + account_whitelist(
        MAIN_ASSET_ADMIN_ACCOUNT_ID,
        u['account_id'],
        1 #insert into white list
      )
    )
  print json.dumps(ops, indent=2)
  #set_fees_and_broadcast(ops, [ADMIN_PRIVATE_KEY], CORE_ASSET)
  #res = proposal_create(ENDORSEMENT_ADMIN_ACCOUNT_ID, ops, REGISTER_PRIVATE_KEY)
  #print json.dumps(ops, indent=2)

def multisig_change_government_active(active):
  init([])
  ops = account_update(MAIN_ASSET_ADMIN_ACCOUNT_ID, None, active)
  res = proposal_create(ENDORSEMENT_ADMIN_ACCOUNT_ID, ops, REGISTER_PRIVATE_KEY)

def multisig_reserve_asset(assets_to_reserve):
  init([])

  balances = rpc.db_get_account_balances(MAIN_ASSET_ADMIN_ACCOUNT_ID, [assets[a]['id'] for a in assets_to_reserve])
  
  ops = []
  for j in xrange(len(assets_to_reserve)):
    assert(balances[j]['asset_id'] == assets[assets_to_reserve[j]]['id']), "Invalid 0 balance"
    if balances[j]['amount'] == 0: continue
    amount = amount_value(balances[j]['amount'], assets[assets_to_reserve[j]])
    ops.extend(
      asset_reserve(MAIN_ASSET_ADMIN_ACCOUNT_ID, assets[assets_to_reserve[j]], amount)
    )
  
  set_fees_and_broadcast(ops, [ADMIN_PRIVATE_KEY], CORE_ASSET)
  #res = proposal_create(ENDORSEMENT_ADMIN_ACCOUNT_ID, ops, REGISTER_PRIVATE_KEY)

def multisig_change_keys(account, owner, active, memo_key):
  init([account])

  active_auth = {
    'weight_threshold' : 1,
    'account_auths'    : [],
    'key_auths'        : [[active,1]], 
    'address_auths'    : []
  }
  
  owner_auth = {
    'weight_threshold' : 1,
    'account_auths'    : [[MAIN_ASSET_ADMIN_ACCOUNT_ID,1]],
    'key_auths'        : [[owner,1]], 
    'address_auths'    : []
  }
  
  ops = account_update(
    account_id(account), 
    owner_auth, 
    active_auth, 
    {'memo_key':memo_key},
    [ADMIN_PRIVATE_KEY],
    assets_by_id[CURRENCY_ASSET_ID]['id']
  )

  #[ADMIN_PRIVATE_KEY]
  #set_fees_and_broadcast(ops, None, CORE_ASSET)
  
def multisig_claim_fees(assets_to_claim):
  init([])
  
  oinfo = rpc.db_get_objects([ 
    ainfo['dynamic_asset_data_id'] for ainfo in rpc.db_get_assets([assets[asset]['id'] for asset in assets_to_claim])
  ])
  
  ops = []
  for j in xrange(len(assets_to_claim)):
    
    asset = assets[assets_to_claim[j]]
    
    assert(oinfo[j]['id'][1:] == asset['id'][1:]), "Invalid claim"
    if oinfo[j]['accumulated_fees'] == 0: continue
      
    amount = amount_value(oinfo[j]['accumulated_fees'], asset)
    ops.extend(
      asset_claim_fees(MAIN_ASSET_ADMIN_ACCOUNT_ID, asset, amount)
    )
  
  set_fees_and_broadcast(ops, [ADMIN_PRIVATE_KEY], CORE_ASSET)
  #res = proposal_create(ENDORSEMENT_ADMIN_ACCOUNT_ID, ops, REGISTER_PRIVATE_KEY)

def WARNING_clean_account(orig, orig_wif):
  
  balances = rpc.db_get_account_balances(account_id(orig))
  print json.dumps(balances, indent=2)

  ops = []

  # print json.dumps(assets_by_id, indent=2)

  for b in balances:
    if b['amount'] == 0 : continue
    #print b['asset_id'], b['asset_id'] != '1.3.0'
    if b['asset_id'] != '1.3.0':

      ops += transfer(
        account_id(orig),
        assets_by_id[b['asset_id']]['issuer'],
        assets_by_id[b['asset_id']],
        amount_value(b['amount'], assets_by_id[b['asset_id']])
      )

  print len(ops)

  if len(ops) == 0:
    print "nada para limpiar en ", orig
    return

  ops = transfer(
    ENDORSEMENT_ADMIN_ACCOUNT_ID,
    account_id(orig),
    assets['BTS'],
    amount_value(130625*len(ops), assets['BTS'])
  ) + account_whitelist(
    MAIN_ASSET_ADMIN_ACCOUNT_ID,
    account_id(orig),
    1 #insert into white list
  ) + account_whitelist(
    ENDORSEMENT_ADMIN_ACCOUNT_ID,
    account_id(orig),
    0 #remove from lists
  ) + ops

  tx = build_tx_and_broadcast(
    ops,
    [orig_wif,REGISTER_PRIVATE_KEY,ADMIN_PRIVATE_KEY]
  )

  print json.dumps(tx, indent=2)  


if __name__ == '__main__':
  pass
