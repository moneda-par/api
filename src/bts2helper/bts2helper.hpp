#include <string>

std::string bts2helper_sign_compact(const std::string& digest, const std::string& wif);
std::string bts2helper_recover_pubkey(const std::string& signature, const std::string& digest, bool check_canonical );
std::string bts2helper_tx_digest(const std::string& tx_json, const std::string& chain_id);
std::string bts2helper_tx_id(const std::string& tx_json);
uint32_t bts2helper_ref_block_num(const std::string& block_id);
uint32_t bts2helper_ref_block_prefix(const std::string& block_id);
std::string bts2helper_block_id(const std::string& signed_block_header_json);
bool bts2helper_is_cheap_name(const std::string& name);
bool bts2helper_is_valid_name(const std::string& name);
std::string bts2helper_wif_to_pubkey(const std::string& wif);
std::string bts2helper_memo_encode(const std::string& priv, const std::string& pub, const std::string& message);
std::string bts2helper_memo_decode(const std::string& priv, const std::string& pub, const std::string& memo_from, const std::string& memo_to, const std::string& memo_nonce, const std::string& memo_message);
