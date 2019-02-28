# MONEDA PAR API
Simple, lightweight and scalable API written in Python that facilitates Mutual Credit System accounting, which is deployed on BitShares.

## About MONEDA PAR

Moneda PAR (Pair Coin) is an implementation of a [LETS](https://en.wikipedia.org/wiki/Local_exchange_trading_system) or [Mutual Credit System](https://en.wikipedia.org/wiki/Mutual_credit).
It is a credit system, where creditors and debtors are the same people who lend to each other. It should be noted that they do not lend money like a bank does, but they keep an exchange accounting or credit compensation system. The novelty is that this accounting is carried forward on blockchain technology.

[Ver de tomar y traducir de este link](https://github.com/waba-network/par).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

#### 1.- Build Bitshares
Follow this link https://github.com/bitshares/bitshares-core up to build BitShares. 

Tip#1: add this line 
```
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
```
at the begining of [CMakeList.txt](https://github.com/bitshares/bitshares-core/blob/master/CMakeLists.txt) file before running `make` command.

Tip#2: To improve compilation time you can run `make` command  with -sj paramenter.
```
name@device:~$ make -sj7
```
I use 7 because i'ts the result of my laptop's cores count minus 1.

#### 2.- Configure Private Bitshares Testnet on your local machine
Follow this link to configure https://github.com/cryptonomex/graphene/wiki/private-testnet until [Creating committee members](https://github.com/cryptonomex/graphene/wiki/private-testnet#creating-committee-members).
Up to here, `nathan` is an upgraded account with tons of BTS on its balance.

#### 3.- Configure API permissions
Before continue, we will configure node's APIs permissions, as described [here](https://github.com/bitshares/bitshares-core#accessing-restricted-apis).
You can use `/config/my-api-access.json` configuration file  provided in this repo.

#### 4.- Run Testnet
Use `/full-path-to-bitshares-directory/programs/witness_node/witness_node --data-dir data/my-blockprod --genesis-json relative-path-to-genesis-conf-file/my-genesis.json --enable-stale-production --seed-nodes "[]"
` to run local node.

You can use `/config/my-genesis.json` configuration file provided in this repo, which include updated fees.

#### 5.- Creating a wallet and running CLI Wallet
Folowing [this steps](https://github.com/cryptonomex/graphene/wiki/private-testnet#creating-a-wallet) you end upwith a CLI Wallet running.
You can now create requiered accounts and assets.

##### 5.1.- Accounts creation
We will create the main asset admin account (the Architect) and the endorsement admin account (the Keymaker).

##### main-asset-admin-account
* Get a wif private key using the `suggest_brain_key` command. 
```
unlocked >>> suggest_brain_key
{
  "brain_priv_key": "LICHAM SLOE ENOMOTY UMIRI DOWDILY MOORN DAVOCH AZYME PITEOUS UNTIDAL UNTALL STEVEN MUIST SAFE NEWISH MUYUSA",
  "wif_priv_key": "5KjuGau695Y98Xr5YgnDHJ8SJgKsnKdpbwRzMSjVSY9rRivQs9b",
  "pub_key": "BTS87Btwuz5H2hFoThXqPDTmw2tRpGWWkURu9Xd5bHW7HTaPAizMR"
}
```

  * Register account running the `register_account` command.
```
unlocked >>> register_account name owner_pubkey active_pubkey registrar_account referrer_account referrer_percent broadcast
``` 

In our example:
```
unlocked >>> register_account main-asset-admin-account BTS87Btwuz5H2hFoThXqPDTmw2tRpGWWkURu9Xd5bHW7HTaPAizMR BTS87Btwuz5H2hFoThXqPDTmw2tRpGWWkURu9Xd5bHW7HTaPAizMR nathan nathan 0 true
```   

##### asset-endorsement-admin-account
* Get a wif private key using the `suggest_brain_key` command.
```
unlocked >>> suggest_brain_key
{
  "brain_priv_key": "TINNERY COILING BRAISE ABRASE OPPOSER OUTWENT TAXATOR CHERRY KISWA MATEY LINO EUGE AXUNGE STIPE RICKEY SAMOVAR",
  "wif_priv_key": "5JQGCnJCDyraociQmhDRDxzNFCd8WdcJ4BAj8q1YDZtVpk5NDw9",
  "pub_key": "BTS6bM4zBP7PKcSmXV7voEdauT6khCDGUqXyAsq5NCHcyYaNSMYBk"
}
```
* Register account running the `register_account` command.
```
unlocked >>> register_account asset-endorsement-admin-account BTS6bM4zBP7PKcSmXV7voEdauT6khCDGUqXyAsq5NCHcyYaNSMYBk BTS6bM4zBP7PKcSmXV7voEdauT6khCDGUqXyAsq5NCHcyYaNSMYBk nathan nathan 0 true
```   

##### 5.2.- Fund accounts' balances and upgrade accounts

```
unlocked >>> import_key main-asset-admin-account "5KjuGau695Y98Xr5YgnDHJ8SJgKsnKdpbwRzMSjVSY9rRivQs9b"
unlocked >>> transfer nathan main-asset-admin-account 100000 CORE "here is the cash" true
unlocked >>> upgrade main-asset-admin-account true
```

```
unlocked >>> import_key asset-endorsement-admin-account "5JQGCnJCDyraociQmhDRDxzNFCd8WdcJ4BAj8q1YDZtVpk5NDw9"
unlocked >>> transfer nathan asset-endorsement-admin-account 100000 CORE "here is the cash" true
unlocked >>> upgrade asset-endorsement-admin-account true
```

By running `get_account <name_or_id>` command you get account's information.
```
unlocked >>> get_account main-asset-admin-account
get_account main-asset-admin-account
{
  "id": "1.2.9",
  "membership_expiration_date": "1969-12-31T23:59:59",
  "registrar": "1.2.XXX",
  "referrer": "1.2.XXX",
  "lifetime_referrer": "1.2.XXX",
  "network_fee_percentage": 2000,
  "lifetime_referrer_fee_percentage": 8000,
  "referrer_rewards_percentage": 0,
  "name": "main-asset-admin-account",
  "owner": {
    "weight_threshold": 1,
    "account_auths": [],
    "key_auths": [[
	"BTS87Btwuz5H2hFoThXqPDTmw2tRpGWWkURu9Xd5bHW7HTaPAizMR",
        1
      ]
    ],
    "address_auths": []
  },
  "active": {
    "weight_threshold": 1,
    "account_auths": [],
    "key_auths": [[
	"BTS87Btwuz5H2hFoThXqPDTmw2tRpGWWkURu9Xd5bHW7HTaPAizMR",
        1
      ]
    ],
    "address_auths": []
  },
  "options": {
    "memo_key": "BTS87Btwuz5H2hFoThXqPDTmw2tRpGWWkURu9Xd5bHW7HTaPAizMR",
    "voting_account": "1.2.XXX",
    "num_witness": 0,
    "num_committee": 0,
    "votes": [],
    "extensions": []
  },
```

```
unlocked >>> get_account asset-endorsement-admin-account
get_account asset-endorsement-admin-account
{
  "id": "1.2.10",
  "membership_expiration_date": "1969-12-31T23:59:59",
  "registrar": "1.2.XXX",
  "referrer": "1.2.XXX",
  "lifetime_referrer": "1.2.XXX",
  "network_fee_percentage": 2000,
  "lifetime_referrer_fee_percentage": 8000,
  "referrer_rewards_percentage": 0,
  "name": "main-asset-admin-account",
  "owner": {
    "weight_threshold": 1,
    "account_auths": [],
    "key_auths": [[
	"BTS6bM4zBP7PKcSmXV7voEdauT6khCDGUqXyAsq5NCHcyYaNSMYBk",
        1
      ]
    ],
    "address_auths": []
  },
  "active": {
    "weight_threshold": 1,
    "account_auths": [],
    "key_auths": [[
	"BTS6bM4zBP7PKcSmXV7voEdauT6khCDGUqXyAsq5NCHcyYaNSMYBk",
        1
      ]
    ],
    "address_auths": []
  },
  "options": {
    "memo_key": "BTS6bM4zBP7PKcSmXV7voEdauT6khCDGUqXyAsq5NCHcyYaNSMYBk",
    "voting_account": "1.2.XXX",
    "num_witness": 0,
    "num_committee": 0,
    "votes": [],
    "extensions": []
  },
```

| Account Name| Account Id           | 
| ------------- |:-------------:| 
| main-asset-admin-account | 1.2.9 |
| asset-endorsement-admin-account | 1.2.10 | 

##### 5.3.-  Assets creation

We will create 3 tokens using the `create_asset` command.
```
unlocked >>> create_asset <issuer> <symbol> <precision> <options> {} true
```
For deeper information about creating an asset checkout [this link about creating UIA](http://docs.bitshares.org/bitshares/tutorials/uia-create-manual.html)

*main-asset-admin-account* will create the main asset and the overdraft asset.
*asset-endorsement-admin-account* will create the endorsement asset that let the community create the social graph of permissions/credits. 

```
Note that this implementation requires one endorsement asset for every different overdraft's amount. In such scenario, the account that holds one unit of ENDORSEMENTASSET1 can apply for an overdraft of a predefined amount related to the asset. There is an upgrade at Discoin (discoin.com.ar) where we use only one asset that represents the amount of the overdraft to be credited. This updates will be provided as soon as we merge both branches. 
```

###### Notation Convention

* 1.3.0 is the main Bitshares asset id, BTS.
* 1.3.1 is the creating asset id.

###### Create Currency Asset

```
unlocked >>> create_asset main-asset-admin-account CURRENCYASSET 2 {"max_supply": "100000000000","market_fee_percent": 0,"max_market_fee": "0","issuer_permissions": 79,"flags": 4,"core_exchange_rate": { "base": { "amount": 100000, "asset_id": "1.3.0" }, "quote": { "amount": 1, "asset_id": "1.3.1" } }, "whitelist_authorities": [], "blacklist_authorities": [], "whitelist_markets"    : [], "blacklist_markets": [], "description": "My Community Currency", "extensions": [] } null true
```

###### Create Overdraft Asset

```
unlocked >>> create_asset main-asset-admin-account OVERDRAFTASSET 2 {"max_supply": "100000000000","market_fee_percent": 0,"max_market_fee": "0","issuer_permissions": 79,"flags": 4,"core_exchange_rate": { "base": { "amount": 100000, "asset_id": "1.3.0" }, "quote": { "amount": 1, "asset_id": "1.3.1" } }, "whitelist_authorities": ['1.2.9'], "blacklist_authorities": [], "whitelist_markets"    : [], "blacklist_markets": [], "description": "My Community Currency", "extensions": [] } null true
```
Checkout that the whitelist authorized account is issuers' account id (main-asset-admin-account id). It means that any account that holds this asset has been previously authorized by the issuer.

###### Create Endorsement Asset #1

```
unlocked >>> create_asset asset-endorsement-admin-account ENDORSEMENTASSET1 2 {"max_supply": "100000000000","market_fee_percent": 0,"max_market_fee": "0","issuer_permissions": 79,"flags": 78,"core_exchange_rate": { "base": { "amount": 100000, "asset_id": "1.3.0" }, "quote": { "amount": 1, "asset_id": "1.3.1" } }, "whitelist_authorities": [], "blacklist_authorities": ['1.2.9'], "whitelist_markets"    : [], "blacklist_markets": [], "description": "Endorsement asset 1", "extensions": [] } null true
```

Checkout that the blacklist authorized account is issuers' account id (main-asset-admin-account id). It means that any account that holds this asset has been previously authorized by the issuer.

###### Get assets' IDs
By running `get_asset <asset_name>` you get asset's configuration, such as ID.
```
unlocked >>> get_asset ENDORSEMENTASSET1
get_asset ENDORSEMENTASSET1
{
  "id": "1.3.3",
  "symbol": "ENDORSEMENTASSET1",
  "precision": 2,
  "issuer": "1.2.10",
  "options": {
    "max_supply": "100000000000",
    "market_fee_percent": 0,
    "max_market_fee": 0,
    "issuer_permissions": 79,
    "flags": 78,
    "core_exchange_rate": {
      "base": {
        "amount": 1000000,
        "asset_id": "1.3.0"
      },
      "quote": {
        "amount": 10,
        "asset_id": "1.3.1"
      }
    },
    "whitelist_authorities": [],
    "blacklist_authorities": [
	      "1.2.10"
	    ],
    "whitelist_markets": [
      "1.3.1004"
    ],
    "blacklist_markets": [],
    "description": "Endorsement asset 1",
    "extensions": []
  },
  "dynamic_asset_data_id": "2.3.1"
}

```

#### 6.- Create database

#### 7.- Configure and run API

`>>>>missing info<<<<<`

##### 7.1.- Create OneSignal App

`>>>>missing info<<<<<`

##### 7.2.- Configure API's parameters

`>>>>missing info<<<<<`

##### 7.3.- Build Bitshares Helper (a Shared Object)

`>>>>missing info<<<<<`

##### 7.4.- Run API

`>>>>missing info<<<<<`

#### 8.- Build Mobile App

##### 8.1.- Setup development environment
`>>>>missing info<<<<<`

##### 8.2.- Configure App's  parameters
`>>>>missing info<<<<<`

##### 8.3.- Build
`>>>>missing info<<<<<`

##### 8.4.- Run app
`>>>>missing info<<<<<`

#### 9.- Launch

##### 9.1.- Issue first endorsement

`>>>>something<<<<<`

##### 9.2.- Give first credit/overdraft

`>>>>something<<<<<`

## Deployment

`>>>>something<<<<<`

## Built With

* [Bitshares](https://github.com/bitshares/bitshares-core) - The accountability platform used (blockchain). [Link to Bitshares' institutional website](https://bitshares.org/).
* [Bitshares UI](https://github.com/bitshares/bitshares-ui) - Bitshares administration tool.
* [Python](https://www.python.org/) - API
* [Flask](http://flask.pocoo.org/) - Web framework
* [ReactNative](https://facebook.github.io/react-native/) - Mobile app framework

## Contributing

`>>>>something<<<<<`

## Versioning

`>>>>something<<<<<`

## Authors

* **Matias Romeo** - [elmato](https://github.com/elmato)
* **Pablo Tutino** - [dargonar](https://github.com/dargonar)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE Version 3 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

* [Nicolas Echaniz](https://github.com/nicoechaniz)
* [Rogelio Segovia](https://www.linkedin.com/in/rogeliosegovia/)


