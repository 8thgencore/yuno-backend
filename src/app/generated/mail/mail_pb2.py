# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: mail/mail.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0fmail/mail.proto\x12\x04mail".\n\x0bSendRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x10\n\x08otp_code\x18\x02 \x01(\t""\n\x0cSendResponse\x12\x12\n\nis_success\x18\x01 \x01(\x08\x32\x82\x01\n\x04Mail\x12>\n\x15SendConfirmationEmail\x12\x11.mail.SendRequest\x1a\x12.mail.SendResponse\x12:\n\x11SendPasswordReset\x12\x11.mail.SendRequest\x1a\x12.mail.SendResponseB\x10Z\x0email.v1;mailv1b\x06proto3',
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "mail.mail_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    _globals["DESCRIPTOR"]._loaded_options = None
    _globals["DESCRIPTOR"]._serialized_options = b"Z\016mail.v1;mailv1"
    _globals["_SENDREQUEST"]._serialized_start = 25
    _globals["_SENDREQUEST"]._serialized_end = 71
    _globals["_SENDRESPONSE"]._serialized_start = 73
    _globals["_SENDRESPONSE"]._serialized_end = 107
    _globals["_MAIL"]._serialized_start = 110
    _globals["_MAIL"]._serialized_end = 240
# @@protoc_insertion_point(module_scope)
