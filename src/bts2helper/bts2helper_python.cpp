#include "bts2helper.hpp"
#include <boost/python.hpp>
#include <boost/python/def.hpp>
#include <boost/python/exception_translator.hpp>

using namespace boost::python;

#include <fc/exception/exception.hpp>
void translate(fc::exception const& e)
{
  //Use the Python 'C' API to set up an exception object
  PyErr_SetString(PyExc_RuntimeError, e.to_detail_string().c_str());
}

 
BOOST_PYTHON_MODULE(bts2helper)
{
  register_exception_translator<fc::exception>(&translate);
  def("bts2helper_is_valid_name"     , bts2helper_is_valid_name);
  def("bts2helper_is_cheap_name"     , bts2helper_is_cheap_name);
  def("bts2helper_tx_id"             , bts2helper_tx_id);
  def("bts2helper_tx_digest"         , bts2helper_tx_digest);
  def("bts2helper_sign_compact"      , bts2helper_sign_compact);
  def("bts2helper_recover_pubkey"    , bts2helper_recover_pubkey);
  def("bts2helper_block_id"          , bts2helper_block_id);
  def("bts2helper_ref_block_num"     , bts2helper_ref_block_num);
  def("bts2helper_ref_block_prefix"  , bts2helper_ref_block_prefix);
  def("bts2helper_wif_to_pubkey"     , bts2helper_wif_to_pubkey);
  def("bts2helper_memo_decode"       , bts2helper_memo_decode);
  def("bts2helper_memo_encode"       , bts2helper_memo_encode);
}
