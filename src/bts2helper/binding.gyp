{
    "targets": [
        {
            "target_name": "bts2helper",
            "sources": [ "bts2helper.cpp", "bts2helper_node.cpp"],
	    'cflags!': [ '-fno-exceptions', '-fno-rtti' ],
            'cflags_cc!': [ '-fno-exceptions', '-fno-rtti' ],
            "include_dirs": [
                "<!(node -e \"require('nan')\")",
'/home/ubuntu/opt/boost_1_57_0/include', '/usr/local/include', '/home/ubuntu/dev/graphene/libraries/utilities/include', '/home/ubuntu/dev/graphene/libraries/chain/include', '/home/ubuntu/dev/graphene/libraries/db/include', '/home/ubuntu/dev/graphene/libraries/fc/include'
            ],
            "libraries" : ['-Wl,--no-as-needed  -lsecp256k1 -Wl,--as-needed', '-lgraphene_chain', '-lgraphene_utilities', '-lgraphene_db', '-lfc_debug', '-lssl', '-lboost_iostreams', '-lboost_filesystem', '-lboost_thread', '-lboost_system', '-lboost_chrono', '-lcrypto', '-lboost_coroutine', '-lboost_context', '-lboost_python', '-lboost_date_time', '-L/home/ubuntu/opt/boost_1_57_0/lib', '-L/usr/local/lib', '-L/home/ubuntu/dev/graphene/libraries/utilities', '-L/home/ubuntu/dev/graphene/libraries/chain', '-L/home/ubuntu/dev/graphene/libraries/db', '-L/home/ubuntu/dev/graphene/libraries/fc', '-L/home/ubuntu/dev/graphene/libraries/fc/vendor/secp256k1-zkp/src/project_secp256k1-build/.libs']
        }
    ]
}
