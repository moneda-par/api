#include <iostream>
#include <string>
#include <vector>

#include <boost/array.hpp>

#include <fc/io/json.hpp>
#include <fc/variant_object.hpp>
#include <fc/crypto/hex.hpp>
#include <fc/crypto/ripemd160.hpp>

#include <fc/smart_ref_fwd.hpp>
#include <fc/smart_ref_impl.hpp>
#include <fc/bitutil.hpp>

#include <fc/crypto/elliptic.hpp>
#include <fc/crypto/ripemd160.hpp>
#include <fc/crypto/sha512.hpp>
#include <fc/crypto/sha256.hpp>

// #include <graphene/chain/protocol/protocol.hpp>
#include <graphene/chain/protocol/transaction.hpp>
#include <graphene/chain/protocol/account.hpp>
#include <graphene/chain/protocol/memo.hpp>

#include <graphene/utilities/key_conversion.hpp>

using namespace boost;
using namespace graphene::chain;
using namespace graphene::utilities;

#define MAX_JSON_DEPTH 1000

std::string bts2helper_memo_encode(const std::string& priv, const std::string& pub, const std::string& message) {

  auto priv_key = fc::ecc::private_key::regenerate( fc::sha256(priv) );
  auto pub_key  = public_key_type( pub );

  memo_data data;
  data.set_message(priv_key, pub_key, message, 0);

  return fc::json::to_string(data);
}

std::string bts2helper_memo_decode(const std::string& priv, const std::string& pub, const std::string& memo_from, const std::string& memo_to,
                 const std::string& memo_nonce, const std::string& memo_message) {

  auto priv_key = fc::ecc::private_key::regenerate( fc::sha256(priv) );
  auto pub_key  = public_key_type( pub );

  memo_data data;
  
  data.from    = public_key_type(memo_from);
  data.to      = public_key_type(memo_to);
  data.nonce   = fc::to_uint64(memo_nonce);
  
  auto byte_size = memo_message.length()/2;

  data.message.resize(byte_size);
  fc::from_hex(memo_message, &data.message[0], byte_size);
  
  return data.get_message(priv_key, pub_key);
}

std::string bts2helper_wif_to_pubkey(const std::string& wif) {
  auto pk = wif_to_key(wif);
  public_key_type pub = pk->get_public_key();
  return std::string(pub);
}

std::string bts2helper_sign_compact(const std::string& digest, const std::string& wif) {

  auto pk = wif_to_key(wif);
  
  auto tmp = fc::sha256(digest);

  auto sig = pk->sign_compact(tmp);

  return fc::to_hex(fc::raw::pack(sig));

  // return sig.str();
}

std::string bts2helper_recover_pubkey(const std::string& signature, const std::string& digest, bool check_canonical ) {

  auto _digest = fc::sha256(digest);  
  
  fc::ecc::compact_signature cs;

  fc::from_hex(signature, (char*)&cs, sizeof(cs));

  auto _pub_key = fc::ecc::public_key( cs, _digest, check_canonical);

  return fc::to_hex(fc::raw::pack(_pub_key.serialize()));
}

std::string bts2helper_tx_id(const std::string& tx_json) {

  auto tx     = fc::json::from_string(tx_json).as<transaction>(MAX_JSON_DEPTH);
  auto txid   = tx.id();
  auto data   = fc::raw::pack(txid);

  return fc::to_hex(data);
}

std::string bts2helper_tx_digest(const std::string& tx_json, const std::string& chain_id) {

  auto tx     = fc::json::from_string(tx_json).as<transaction>(MAX_JSON_DEPTH);
  auto digest = tx.sig_digest(fc::sha256(chain_id));
  auto data   = fc::raw::pack(digest);

  return fc::to_hex(data);
}

uint32_t bts2helper_ref_block_num(const std::string& block_id) 
{
  auto tmp = fc::ripemd160(block_id);
  return fc::endian_reverse_u32(tmp._hash[0]);
}

uint32_t bts2helper_ref_block_prefix(const std::string& block_id) 
{
  return fc::ripemd160(block_id)._hash[1];
}

std::string bts2helper_block_id(const std::string& signed_block_header_json) {

  auto block_header = fc::json::from_string(signed_block_header_json).as<signed_block_header>(MAX_JSON_DEPTH);
  auto id           = block_header.id();
  auto data         = fc::raw::pack(id);

  return fc::to_hex(data);
}

std::string bts2helper_tx_id(std::string tx_json) {

  auto tx   = fc::json::from_string(tx_json).as<transaction>(MAX_JSON_DEPTH);
  auto id   = tx.id();
  auto data = fc::raw::pack(id);

  return fc::to_hex(data);
}

bool bts2helper_is_cheap_name(const std::string& name) {
  return is_cheap_name(name);
}

bool bts2helper_is_valid_name(const std::string& name) {
  return is_valid_name(name);
}
