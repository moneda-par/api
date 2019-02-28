import os
from decimal import Decimal

DB_URL                        = os.environ.get('DB_URL', 'mysql+pymysql://root:__PASSWORD__@__IP__/par')
BITSHARES_WS_NODE             = os.environ.get('BITSHARES_WS_NODE', 'ws://localhost:8090/')
BITSHARES_RPC_NODE            = os.environ.get('BITSHARES_RPC_NODE', 'http://localhost:8090/rpc')

# ACCOUNT_PREFIX used to register new MutualCredit accounts.
ACCOUNT_PREFIX                = 'myproject-prefix.'

# ASSETS' issuers and administrators
# REGISTER_PRIVATE_KEY is ENDORSEMENT_ADMIN_ACCOUNT_ID active key (aka propuesta-par)
REGISTER_PRIVATE_KEY          = os.environ.get('REGISTER_PRIVATE_KEY', '') 
# ADMIN_PRIVATE_KEY is MAIN_ASSET_ADMIN_ACCOUNT_ID active key
ADMIN_PRIVATE_KEY             = os.environ.get('ADMIN_PRIVATE_KEY', '') 
# MAIN_ASSET_ADMIN_ACCOUNT_ID issues currency asset and endorsement asset.
MAIN_ASSET_ADMIN_ACCOUNT_ID   = '1.2.150830'
MAIN_ASSET_ADMIN_ACCOUNT_NAME = 'main-asset-admin-account' #'myproject-architect'
# ENDORSEMENT_ADMIN_ACCOUNT_ID issues amounts endorsements assets (ENDORSE_ASSET_IDxXXX).
ENDORSEMENT_ADMIN_ACCOUNT_ID  = '1.2.151476'
ENDORSEMENT_ADMIN_ACCOUNT_NAME= 'asset-endorsement-admin-account'

CORE_ASSET                    = '1.3.0'
ASSET_PRECISION               = 100
ASSET_ID                      = '1.3.1236'
CURRENCY_ASSET_ID             = ASSET_ID
OVERDRAFT_ASSET_ID            = '1.3.1237'

ENDORSE_ASSET_IDx1000         = '1.3.1319'
ENDORSE_ASSET_IDx10000        = '1.3.1322'
ENDORSE_ASSET_IDx30000        = '1.3.1320'
ENDORSE_ASSET_IDx100000       = '1.3.1321'
ALL_ENDORSE_ASSETS_ID         = [ENDORSE_ASSET_IDx1000, ENDORSE_ASSET_IDx10000, ENDORSE_ASSET_IDx30000, ENDORSE_ASSET_IDx100000]

ONLY_VALID_ENDORSEMENT_TOKENS       = [ENDORSE_ASSET_IDx1000, ENDORSE_ASSET_IDx10000, ENDORSE_ASSET_IDx30000]
ALL_TRACKED_ASSETS                  = ALL_ENDORSE_ASSETS_ID + [CURRENCY_ASSET_ID, OVERDRAFT_ASSET_ID]
ALL_VALID_ASSETS                    = ALL_ENDORSE_ASSETS_ID + [CURRENCY_ASSET_ID]
ALL_TRACKED_ASSETS_PLUS_CORE_ASSET  = ALL_TRACKED_ASSETS + [CORE_ASSET]

CHAIN_ID                      = '4018d7844c78f6a6c41c6a552b898022310fc5dec06da467ee7905a8dad512c8'

MEMCACHE_IP_and_PORT          = '127.0.0.1:11211'

REGISTER_SECRET_PHRASE        = 'averysecretphrase'

ONE_SIGNAL_APP_ID             = '__ONE_SIGNAL_APP_ID__'
