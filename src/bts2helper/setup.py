#!/usr/bin/python3

import os
os.environ["CC"] = "gcc"
os.environ["CXX"] = "g++"
os.environ["LDFLAGS"] = "-Wl,--no-as-needed -Wl,-z,defs"
 
from distutils.core import setup
from distutils.extension import Extension
  
# iroot  = os.environ.get('GPH_ROOT_INCLUDE', '/home/ubuntu/bitshares_2_0_180612/libraries')
# lroot  = os.environ.get('GPH_ROOT_LIB', '/home/ubuntu/bitshares_2_0_180612/libraries')
iroot  = os.environ.get('GPH_ROOT_INCLUDE', '/home/ubuntu/bitshares/libraries')
lroot  = os.environ.get('GPH_ROOT_LIB', '/home/ubuntu/bitshares/libraries')
mt     = os.environ.get('GPH_BOOST_POSTFIX', '')
debug  = os.environ.get('GPH_DEBUG','_debug')

setup(name="BTS2Helper",
  ext_modules=[
    Extension("bts2helper", ["bts2helper.cpp", "bts2helper_python.cpp"],
      extra_compile_args = ['-std=c++11'], #, '-D_GLIBCXX_USE_CXX11_ABI=0'],
      #libraries = ['leveldb', 'graphene_chain' , 'graphene_db', 'fc%s'%debug , 'ssl' , 'boost_iostreams%s'%mt , 'boost_filesystem%s'%mt , 'boost_thread%s'%mt , 'easylzma_static%s' % debug , 'boost_system%s'%mt , 'boost_chrono%s'%mt , 'crypto' , 'boost_coroutine%s'%mt , 'boost_context%s'%mt, 'boost_python%s'%mt, 'boost_date_time%s'%mt],
      libraries = ['secp256k1', 'graphene_utilities', 'graphene_chain', 'fc%s'%debug , 'graphene_db', 'graphene_chain' , 'ssl' , 'boost_iostreams%s'%mt , 'boost_filesystem%s'%mt , 'boost_thread%s'%mt , 'boost_system%s'%mt , 'boost_chrono%s'%mt , 'crypto' , 'boost_coroutine%s'%mt , 'boost_context%s'%mt, 'boost_python%s'%mt, 'boost_date_time%s'%mt, 'python2.7'],
      include_dirs = ['/home/ubuntu/opt/boost_1_57_0/include', '/usr/local/include', '%s/utilities/include' % iroot , '%s/chain/include' % iroot , '%s/db/include' % iroot ,'%s/fc/include' % iroot],
      #library_dirs = ['/usr/local/lib' , '%s/leveldb' % lroot, '%s/chain' % lroot , '%s/db' % lroot , '%s/fc' % lroot , '%s/fc/vendor/easylzma/src' % lroot]
      library_dirs = ['/home/ubuntu/opt/boost_1_57_0/lib', '/usr/local/lib' , '%s/utilities' % lroot, '%s/chain' % lroot , '%s/db' % lroot , '%s/fc' % lroot, '%s/fc/vendor/secp256k1-zkp/src/project_secp256k1-build/.libs' % lroot ]
    )
  ]
)
      # libraries = ['secp256k1', 'graphene_utilities', 'graphene_chain', 'fc%s'%debug , 'graphene_db', 'graphene_chain' , 'ssl' , 'boost_iostreams%s'%mt , 'boost_filesystem%s'%mt , 'boost_thread%s'%mt , 'boost_system%s'%mt , 'boost_chrono%s'%mt , 'crypto' , 'boost_coroutine%s'%mt , 'boost_context%s'%mt, 'boost_python%s'%mt, 'boost_date_time%s'%mt, 'python2.7'],
      # include_dirs = ['/usr/local/include', '%s/utilities/include' % iroot , '%s/chain/include' % iroot , '%s/db/include' % iroot ,'%s/fc/include' % iroot],
      # library_dirs = ['/usr/local/lib' , '%s/utilities' % lroot, '%s/chain' % lroot , '%s/db' % lroot , '%s/fc' % lroot, '%s/fc/vendor/secp256k1-zkp/src/project_secp256k1-build/.libs' % lroot ]
