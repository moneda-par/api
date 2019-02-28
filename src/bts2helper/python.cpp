#include <iostream>
#include <string>
#include <vector>

#include <boost/array.hpp>
#include <boost/python.hpp>
#include <boost/python/def.hpp>
#include <boost/python/exception_translator.hpp>

#include <fc/io/json.hpp>
#include <fc/crypto/hex.hpp>
#include <fc/crypto/ripemd160.hpp>

#include <fc/smart_ref_fwd.hpp>
#include <fc/smart_ref_impl.hpp>
#include <fc/bitutil.hpp>

#include <fc/crypto/elliptic.hpp>
#include <fc/crypto/ripemd160.hpp>
#include <fc/crypto/sha512.hpp>
#include <fc/crypto/sha256.hpp>

#include <graphene/chain/protocol/protocol.hpp>
#include <graphene/chain/protocol/transaction.hpp>
#include <graphene/chain/protocol/account.hpp>
#include <graphene/chain/protocol/memo.hpp>

#include <graphene/utilities/key_conversion.hpp>

using namespace boost;
using namespace boost::python;
using namespace graphene::chain;
using namespace graphene::utilities;

std::string bts2helper_sign_compact(const std::string& digest, const std::string& wif) {

  auto pk     = wif_to_key(wif);
  
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

std::string bts2helper_tx_digest(const std::string& tx_json, const std::string& chain_id) {

  auto tx     = fc::json::from_string(tx_json).as<transaction>();
  auto digest = tx.sig_digest(fc::sha256(chain_id));
  auto data   = fc::raw::pack(digest);

  return fc::to_hex(data);
}

// uint32_t bts2helper_ref_block_num(const std::string& block_id) 
// {
//   auto tmp = fc::ripemd160(block_id);
//   return fc::endian_reverse_u32(tmp._hash[0]);
// }

// uint32_t bts2helper_ref_block_prefix(const std::string& block_id) 
// {
//   return fc::ripemd160(block_id)._hash[1];
// }

std::string derive_private_key( const std::string& prefix_string,
                                         int sequence_number )
{
   std::string sequence_string = std::to_string(sequence_number);
   fc::sha512 h = fc::sha512::hash(prefix_string + " " + sequence_string);
   fc::ecc::private_key derived_key = fc::ecc::private_key::regenerate(fc::sha256::hash(h));
   return derived_key.get_secret().str();
   //return fc::to_hex(derived_key.get_secret());
}

std::string bts2helper_block_id(const std::string& signed_block_header_json) {

  auto block_header = fc::json::from_string(signed_block_header_json).as<signed_block_header>();
  auto id           = block_header.id();
  auto data         = fc::raw::pack(id);

  return fc::to_hex(data);
}

// std::string bts2helper_tx_id(std::string tx_json) {

//   auto tx   = fc::json::from_string(tx_json).as<transaction>();
//   auto id   = tx.id();
//   auto data = fc::raw::pack(id);

//   return fc::to_hex(data);
// }

void translate(fc::exception const& e)
{
  //Use the Python 'C' API to set up an exception object
  PyErr_SetString(PyExc_RuntimeError, e.to_detail_string().c_str());
}

 
BOOST_PYTHON_MODULE(bts2helper)
{
  register_exception_translator<fc::exception>(&translate);
  def("is_valid_name"                , is_valid_name);
  def("is_cheap_name"                , is_cheap_name);
  def("derive_private_key"           , derive_private_key);
  def("bts2helper_tx_digest"         , bts2helper_tx_digest);
  def("bts2helper_sign_compact"      , bts2helper_sign_compact);
  def("bts2helper_recover_pubkey"    , bts2helper_recover_pubkey);
  def("bts2helper_block_id"          , bts2helper_block_id);
  // def("bts2helper_ref_block_num"     , bts2helper_ref_block_num);
  // def("bts2helper_ref_block_prefix"  , bts2helper_ref_block_prefix);
}
