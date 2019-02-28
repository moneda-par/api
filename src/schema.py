import graphene

import rpc
import cache

from decimal import Decimal
from utils import *
import simplejson as json

# class AuthorizationMiddleware(object):
#   def resolve(self, next, root, args, context, info):

#     if info.field_name == 'user':
#         return None
#     return next(root, args, context, info)

class Blockchain(graphene.ObjectType):
  
  fees             = graphene.String()
  ref_block_num    = graphene.String()
  ref_block_prefix = graphene.String()

  def resolve_fees(self, args, context, info):
    current_fees = rpc.db_get_global_properties()['parameters']['current_fees']

    #HACK BEGIN - static_Variant en android != servidor
    y=[]
    for p in current_fees['parameters']:
      if p[0]<44: y.append(p)
    current_fees['parameters'] = y
    #HACK END

    print(current_fees)
    return json.dumps(current_fees)

  def resolve_ref_block_num(self, args, context, info):
    ref_block_num, ref_block_prefix = ref_block(cache.get_dynamic_global_properties()['head_block_id'])
    return ref_block_num

  def resolve_ref_block_prefix(self, args, context, info):
    ref_block_num, ref_block_prefix = ref_block(cache.get_dynamic_global_properties()['head_block_id'])
    return ref_block_prefix
  
class Amount(graphene.ObjectType):
  quantity = graphene.String()
  asset    = graphene.Field(lambda:Asset)

class Asset(graphene.ObjectType):
  id     = graphene.String()
  symbol = graphene.String()
  issuer = graphene.Field(lambda:Account)

  def __init__(self, asset):
    self.asset = asset

  def resolve_id(self, args, context, info):
    return self.asset['id']

  def resolve_symbol(self, args, context, info):
    return self.asset['symbol']

  #@graphene.with_context
  def resolve_issuer(self, args, context, info):
    return Account( cache.get_account(self.asset['issuer']) )

class Memo(graphene.ObjectType):
  from_   = graphene.String(name='from')
  to      = graphene.String()
  nonce   = graphene.String()
  message = graphene.String()

class Block(graphene.ObjectType):
  previous                = graphene.String()
  timestamp               = graphene.String()
  witness                 = graphene.String()
  transaction_merkle_root = graphene.String()
  extensions              = graphene.String()
  witness_signature       = graphene.String()
  block_id                = graphene.String()
  signing_key             = graphene.String()
  number                  = graphene.Int()

class Operation(graphene.Interface):
  id        = graphene.String()
  fee       = graphene.Field(Amount)
  block     = graphene.Field(Block)

  def resolve_id(self, args, context, info):
    return self.oph['id']

  def resolve_block(self, args, context, info):
    block = cache.get_block_header(self.oph['block_num'])
    return Block(
      previous                = block['previous'],
      timestamp               = block['timestamp'],
      witness                 = block['witness'],
      transaction_merkle_root = block['transaction_merkle_root'],
      extensions              = block['extensions'],
      number                  = self.oph['block_num']
      #witness_signature       = block['witness_signature'],
      #block_id                = block['block_id'],
      #signing_key             = block['signing_key'],
    )

  def resolve_fee(self, args, context, info):
    asset = cache.get_asset(self.op['fee']['asset_id'])
    return Amount(
      quantity = amount_value( str(self.op['fee']['amount']), asset),
      asset    = Asset(asset)
    )


class NoDetailOp(graphene.ObjectType):
  name = graphene.String()

  def __init__(self, oph):
    self.oph = oph
    self.op  = oph['op'][1]

  class Meta:
    interfaces = (Operation, )

class CreditRequest(graphene.ObjectType):

  amount = graphene.Field(lambda:Amount)
  type   = graphene.String()
  
  def __init__(self, ops):
    self.ops   = ops
    print 'CREDIT REQUEST *************************** largo %d' % len(ops)
    print ops

    main_op = ops[-1 if len(ops)==3 else -2].oph['op']
    
    # This is the main OP (ops[1])
    #
    # [ Whitelist, 
    #   Transfer,  
    #   Transfer,    <==== this
    #   Whitelist ] 
    
    # Determine asset
    self.asset = main_op[1]['amount']
    
    # Determine type
    # self.otype = 'down' if main_op[0] == 38 else 'up'
    
    # Determine id (important for history)
    self.oph = ops[0].oph
    self.op  = ops[0].oph['op'][1]
    
  class Meta:
    interfaces = (Operation, )

  def resolve_amount(self, args, context, info):
    asset = cache.get_asset(self.asset['asset_id'])
    return Amount(
      quantity = amount_value( str(self.asset['amount']), asset),
      asset    = Asset(asset)
    )
  
  def resolve_ops(self, args, context, info):
    return self.ops


class OverdraftChange(graphene.ObjectType):

  amount = graphene.Field(lambda:Amount)
  type   = graphene.String()
  
  def __init__(self, ops):
    self.ops   = ops

    print "OverdraftChange => ", ops

    main_op = ops[1].oph['op']
    
    # This is the main OP (ops[1])
    #
    # [ Whitelist, 
    #   AssetIssue,  <==== this
    #   AssetIssue, 
    #   Whitelist ]
    # or 
    # [ Whitelist, 
    #   OverrideTransfer, <==== this
    #   AssetReserve, 
    #   OverrideTransfer, 
    #   AssetReserve, 
    #   Whitelist ]
    # or 
    # [ Whitelist, 
    #   AssetIssue,  <==== this
    #   AssetIssue, 
    #   Whitelist
    #   Whitelist (propuesta-par) ]
    
    # Determine asset
    self.asset = main_op[1]['asset_to_issue'] if 'asset_to_issue' in main_op[1] else main_op[1]['amount']
    
    # Determine type
    self.otype = 'down' if main_op[0] == 38 else 'up'
    
    # Determine id (important for history)
    self.oph = ops[0].oph
    self.op  = ops[0].oph['op'][1]
    
  class Meta:
    interfaces = (Operation, )

  def resolve_amount(self, args, context, info):
    asset = cache.get_asset(self.asset['asset_id'])
    return Amount(
      quantity = amount_value( str(self.asset['amount']), asset),
      asset    = Asset(asset)
    )
  
  def resolve_type(self, args, context, info):
    return self.otype

  def resolve_ops(self, args, context, info):
    return self.ops
    
class AssetIssue(graphene.ObjectType):

  issuer           = graphene.Field(lambda:Account)
  asset_to_issue   = graphene.Field(lambda:Asset)
  issue_to_account = graphene.Field(lambda:Account)

  def __init__(self, oph):
    self.oph = oph
    self.op  = oph['op'][1]

  class Meta:
    interfaces = (Operation, )

  def resolve_issuer(self, args, context, info):
    return Account( cache.get_account(self.op['issuer']) )

  def resolve_asset_to_issue(self, args, context, info):
    return Asset( cache.get_asset(self.op['asset_to_issue']) )

  def resolve_issue_to_account(self, args, context, info):
    return Account( cache.get_asset(self.op['issue_to_account']) )

  
class OverrideTransfer(graphene.ObjectType):

  from_       = graphene.Field(lambda:Account, name='from')
  to          = graphene.Field(lambda:Account)
  amount      = graphene.Field(Amount)
  memo        = graphene.Field(Memo)

  def __init__(self, oph):
    self.oph = oph
    self.op  = oph['op'][1]

  class Meta:
    interfaces = (Operation, )

  def resolve_from_(self, args, context, info):
    return Account( cache.get_account(self.op['from']) )

  def resolve_to(self, args, context, info):
    return Account( cache.get_account(self.op['to']) )

  def resolve_amount(self, args, context, info):
    asset = cache.get_asset(self.op['amount']['asset_id'])
    return Amount(
      quantity = amount_value( str(self.op['amount']['amount']), asset),
      asset    = Asset(asset)
    )

  def resolve_memo(self, args, context, info):
    if not 'memo' in self.op: return None
    return Memo(
      from_   = self.op['memo']['from'],
      to      = self.op['memo']['to'],
      nonce   = self.op['memo']['nonce'],
      message = self.op['memo']['message']
    )

class AccountWhitelist(graphene.ObjectType):

  authorizing_account = graphene.Field(lambda:Account)
  account_to_list     = graphene.Field(lambda:Account)
  new_listing         = graphene.String()

  def __init__(self, oph):
    self.oph = oph
    self.op  = oph['op'][1]

  class Meta:
    interfaces = (Operation, )

  def resolve_authorizing_account(self, args, context, info):
    return Account( cache.get_account(self.op['authorizing_account']) )

  def resolve_account_to_list(self, args, context, info):
    return Account( cache.get_account(self.op['account_to_list']) )

  def resolve_new_listing(self, args, context, info):
    return self.op['new_listing']
  
class Transfer(graphene.ObjectType):
  from_       = graphene.Field(lambda:Account, name='from')
  to          = graphene.Field(lambda:Account)
  amount      = graphene.Field(Amount)
  memo        = graphene.Field(Memo)
  type_       = graphene.String(name='type')

  def __init__(self, oph):
    self.oph = oph
    self.op  = oph['op'][1]

  class Meta:
    interfaces = (Operation, )

  def resolve_from_(self, args, context, info):
    return Account( cache.get_account(self.op['from']) )

  def resolve_to(self, args, context, info):
    return Account( cache.get_account(self.op['to']) )

  def resolve_amount(self, args, context, info):
    asset = cache.get_asset(self.op['amount']['asset_id'])
    return Amount(
      quantity = amount_value( str(self.op['amount']['amount']), asset),
      asset    = Asset(asset)
    )

  def resolve_memo(self, args, context, info):
    if not 'memo' in self.op: return None
    return Memo(
      from_   = self.op['memo']['from'],
      to      = self.op['memo']['to'],
      nonce   = self.op['memo']['nonce'],
      message = self.op['memo']['message']
    )

  #@graphene.with_context
  def resolve_type_(self, args, context, info):
    f = cache.get_account(self.op['from'])['name']

    # print 'comerla ...'
    # print args
    # print '******************'
    # print context
    # print '******************'
    # print info
    # print '******************'

    #HACK:
    x = info.operation.selection_set.selections[0].arguments[0].value.value
    if x == f: return 'sent'
    return 'received'


templates = [
  [ CreditRequest, 
    (7 , []),
    (0 , []),
    (0 , []),
    (7 , []),
  ],
  [ CreditRequest,
    (7 , []),
    (0 , []),
    (0 , []),
  ],
  [ OverdraftChange,
    (7  , []),
    (38 , []),
    (15 , []),
    (38 , []),
    (15 , []),
    (7  , []),
  ],
  [ OverdraftChange,
    (7  , []),
    (14 , []),
    (14 , []),
    (7  , []),
    (7  , []),
  ],
  [ OverdraftChange,
    (7  , []),
    (14 , []),
    (14 , []),
    (7  , []),
  ]
]

#@Schema.register
class Account(graphene.ObjectType):

  id      = graphene.String() 
  name    = graphene.String()
  history = graphene.List(Operation,
   _type = graphene.String(name='type'),
   stop  = graphene.String(),
   limit = graphene.Int(),
   start = graphene.String(),
  )
  
  balance = graphene.List(Amount)
  blacklisted_by = graphene.Boolean(
    account = graphene.String()
  )

  def __init__(self, account):
    self.account = account

  def resolve_id(self, args, context, info):
    return self.account['id']
  
  def resolve_blacklisted_by(self, args, context, info):
    return self.account['id'] in rpc.db_get_account_by_name(args.get('account'))['blacklisted_accounts']

  def resolve_name(self, args, context, info):
    name = self.account['name']
    return real_name(name)
  
  def resolve_balance(self, args, context, info):
    bals = rpc.db_get_account_balances(self.account['id'])
    print '**** bals ****'
    print bals
    print '**************'

    res = []
    for b in bals:
      asset = cache.get_asset(b['asset_id'])
      res.append(Amount(
        quantity = amount_value( str(b['amount']), asset),
        asset    = Asset(asset)
      ))
    return res

  #@graphene.with_context
  def resolve_history(self, args, context, info):

    if args.get('type') == 'relative':
      stop    = int(args.get('stop', 0))
      limit   = int(args.get('limit', 100))
      #start   = int(args.get('start', 0))
      start = 0
      print '[START] rpc.history_get_relative_account_history (%s %s %s)' % (stop, limit, start)
      raw_ops = rpc.history_get_relative_account_history(self.account['id'], stop, limit, start)
      print '[END] rpc.history_get_relative_account_history '

    else:
      stop    = args.get('stop', '1.11.0')
      limit   = int(args.get('limit', 100))
      start   = args.get('start', '1.11.0')
      start   = '1.11.0' if start == '0' else start

      print '[START] rpc.history_get_account_history (%s %s %s %s)' % (self.account['id'], stop, limit, start)
      raw_ops = rpc.history_get_account_history(self.account['id'], stop, limit, start)
      print '[END] rpc.history_get_account_history x'

    txs = []

    # Group ops by tx
    ops_in_tx = []
    for o in raw_ops:
      ops_in_tx.append(o)
      if o['op_in_trx'] == 0:
        txs.append(ops_in_tx[::-1])
        ops_in_tx = []

    def instanceFromOp(oph):
  
      #oph = ops[i]
      op  = oph['op']
      
      if op[0] == 0: 
        return Transfer(oph)
      
      elif op[0] == 7: # Whitelist add
        return AccountWhitelist(oph)

      elif op[0] == 14:
        return AssetIssue(oph)

      elif op[0] == 15:
        return AssetReserve(oph)
        
      elif op[0] == 38:
        return OverrideTransfer(oph)
      
      else:
        return NoDetailOp(oph)

    history = []

    j = 0
    while j < len(txs):

      ops = txs[j]
      print '=======>WORKING NEW TX'

      i = 0

      # Verificar templates
      u = 0
      while u < len(templates):

        ts = templates[u][1:]

        if len(ops)-i >= len(ts):

          pack1 = [ ops[i+x]['op'][0] for x in range(len(ts))  ]
          pack2 = [ t[0] for t in ts ]

          print "OPS_ORIG: ", pack1
          print "TEMPLATE: ", pack2, u, i

          if pack1 == pack2:
            
            sub_ops = [ instanceFromOp(ops[i+x]) for x in range(len(ts)) ]
            history.append( templates[u][0](sub_ops) )

            i += len(ts)
            u = 0

          else:
            u = u + 1

        else:
          u = u + 1

      while i < len(ops):
        print "meto normal ", ops[i]['op'][0]
        
        # HACK HACK CUSTOM_OPERATION
        if ops[i]['op'][0] != 35:
          history.append ( instanceFromOp(ops[i]) )
        
        i = i + 1

      j = j + 1
       
    print 'voy a retornar history'
    return history

class Query(graphene.ObjectType):

  blockchain = graphene.Field(Blockchain)
  
  asset = graphene.String(
    id = graphene.String()
  )
  
  account = graphene.Field(Account, 
    name = graphene.String()
  )

  def resolve_blockchain(self, args, context, info):
    return Blockchain()
  
  def resolve_asset(self, args, context, info):
    return json.dumps(cache.get_asset(args.get('id')))
  
  def resolve_account(self, args, context, info):
    account_name = args.get('name')
    if not account_name: raise

    print 'ACA ESTYO cache.get_account_id'  
    account_id = cache.get_account_id(ACCOUNT_PREFIX + account_name)
    print 'OSHE MIRA ', account_id  
    return Account(cache.get_account(account_id))


theSchema = graphene.Schema(
  query=Query, 
  types=[
    NoDetailOp, 
    Transfer, 
    CreditRequest,
    OverdraftChange,
    AccountWhitelist, 
    OverrideTransfer,
    AssetIssue
  ]
)
#print theSchema
