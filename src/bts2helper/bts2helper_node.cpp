#include <string>
#include <nan.h>
#include "bts2helper.hpp"
#include <boost/function.hpp>

using namespace v8;

typedef boost::function<std::string (const std::string& p1, const std::string& p2)> twoStr;

void generic_call(const Nan::FunctionCallbackInfo<v8::Value>& info, twoStr fnc) {

    Isolate* isolate = info.GetIsolate();

    if (info.Length() < 2) {
        Nan::ThrowTypeError("Wrong number of arguments");
        return;
    }

    if (!info[0]->IsString() || !info[1]->IsString()) {
        Nan::ThrowTypeError("Both arguments should be strings");
        return;
    }

    v8::String::Utf8Value param1(info[0]->ToString());
    v8::String::Utf8Value param2(info[1]->ToString());

    std::string p1 (*param1);
    std::string p2 (*param2);

    std::string res = fnc(p1, p2);

    info.GetReturnValue().Set(String::NewFromUtf8(isolate, res.c_str()));
}

void sign_compact(const Nan::FunctionCallbackInfo<v8::Value>& info) {
  return generic_call(info, bts2helper_sign_compact);
}

void tx_digest(const Nan::FunctionCallbackInfo<v8::Value>& info) {
  return generic_call(info, bts2helper_tx_digest);
}


//void Capo(const Nan::FunctionCallbackInfo<v8::Value>& info) {
//
//    Isolate* isolate = info.GetIsolate();
//
//    // Creates a new Object on the V8 heap
//    Local<Object> obj = Object::New(isolate);
//
//    // Transfers the data from result, to obj (see below)
//    obj->Set(String::NewFromUtf8(isolate, "mean"), 
//                            Number::New(isolate, 1));
//    obj->Set(String::NewFromUtf8(isolate, "median"), 
//                            Number::New(isolate, 2));
//    obj->Set(String::NewFromUtf8(isolate, "standard_deviation"), 
//                            Number::New(isolate, 3));
//    obj->Set(String::NewFromUtf8(isolate, "n"), 
//                            String::NewFromUtf8(isolate, "ennnnneeee"));
//
//    info.GetReturnValue().Set(obj);
//}

void Init(v8::Local<v8::Object> exports) {  
    exports->Set(Nan::New("bts2helper_sign_compact").ToLocalChecked(),
                 Nan::New<v8::FunctionTemplate>(sign_compact)->GetFunction());
    exports->Set(Nan::New("bts2helper_tx_digest").ToLocalChecked(),
                 Nan::New<v8::FunctionTemplate>(tx_digest)->GetFunction());
}

NODE_MODULE(bts2helper, Init)  
