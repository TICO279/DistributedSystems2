from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TipoBandeja(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ENTRADA: _ClassVar[TipoBandeja]
    SALIDA: _ClassVar[TipoBandeja]
ENTRADA: TipoBandeja
SALIDA: TipoBandeja

class UserRequest(_message.Message):
    __slots__ = ("usuario", "token")
    USUARIO_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    usuario: str
    token: str
    def __init__(self, usuario: _Optional[str] = ..., token: _Optional[str] = ...) -> None: ...

class Correo(_message.Message):
    __slots__ = ("idCorreo", "remitente", "destinatario", "asunto", "contenido", "fecha", "leido")
    IDCORREO_FIELD_NUMBER: _ClassVar[int]
    REMITENTE_FIELD_NUMBER: _ClassVar[int]
    DESTINATARIO_FIELD_NUMBER: _ClassVar[int]
    ASUNTO_FIELD_NUMBER: _ClassVar[int]
    CONTENIDO_FIELD_NUMBER: _ClassVar[int]
    FECHA_FIELD_NUMBER: _ClassVar[int]
    LEIDO_FIELD_NUMBER: _ClassVar[int]
    idCorreo: str
    remitente: str
    destinatario: str
    asunto: str
    contenido: str
    fecha: str
    leido: bool
    def __init__(self, idCorreo: _Optional[str] = ..., remitente: _Optional[str] = ..., destinatario: _Optional[str] = ..., asunto: _Optional[str] = ..., contenido: _Optional[str] = ..., fecha: _Optional[str] = ..., leido: bool = ...) -> None: ...

class BandejaReply(_message.Message):
    __slots__ = ("correos",)
    CORREOS_FIELD_NUMBER: _ClassVar[int]
    correos: _containers.RepeatedCompositeFieldContainer[Correo]
    def __init__(self, correos: _Optional[_Iterable[_Union[Correo, _Mapping]]] = ...) -> None: ...

class EnviarCorreoReply(_message.Message):
    __slots__ = ("exito", "mensaje", "idCorreo")
    EXITO_FIELD_NUMBER: _ClassVar[int]
    MENSAJE_FIELD_NUMBER: _ClassVar[int]
    IDCORREO_FIELD_NUMBER: _ClassVar[int]
    exito: bool
    mensaje: str
    idCorreo: str
    def __init__(self, exito: bool = ..., mensaje: _Optional[str] = ..., idCorreo: _Optional[str] = ...) -> None: ...

class AuthenticationRequest(_message.Message):
    __slots__ = ("usuario", "contrasena")
    USUARIO_FIELD_NUMBER: _ClassVar[int]
    CONTRASENA_FIELD_NUMBER: _ClassVar[int]
    usuario: str
    contrasena: str
    def __init__(self, usuario: _Optional[str] = ..., contrasena: _Optional[str] = ...) -> None: ...

class AuthenticationReply(_message.Message):
    __slots__ = ("mensaje", "status", "token")
    MENSAJE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    mensaje: str
    status: bool
    token: str
    def __init__(self, mensaje: _Optional[str] = ..., status: bool = ..., token: _Optional[str] = ...) -> None: ...

class LeidoRequest(_message.Message):
    __slots__ = ("usuario", "idCorreo")
    USUARIO_FIELD_NUMBER: _ClassVar[int]
    IDCORREO_FIELD_NUMBER: _ClassVar[int]
    usuario: str
    idCorreo: str
    def __init__(self, usuario: _Optional[str] = ..., idCorreo: _Optional[str] = ...) -> None: ...

class OperacionReply(_message.Message):
    __slots__ = ("exito", "mensaje")
    EXITO_FIELD_NUMBER: _ClassVar[int]
    MENSAJE_FIELD_NUMBER: _ClassVar[int]
    exito: bool
    mensaje: str
    def __init__(self, exito: bool = ..., mensaje: _Optional[str] = ...) -> None: ...

class CorreoNuevo(_message.Message):
    __slots__ = ("remitente", "destinatario", "asunto", "contenido")
    REMITENTE_FIELD_NUMBER: _ClassVar[int]
    DESTINATARIO_FIELD_NUMBER: _ClassVar[int]
    ASUNTO_FIELD_NUMBER: _ClassVar[int]
    CONTENIDO_FIELD_NUMBER: _ClassVar[int]
    remitente: str
    destinatario: str
    asunto: str
    contenido: str
    def __init__(self, remitente: _Optional[str] = ..., destinatario: _Optional[str] = ..., asunto: _Optional[str] = ..., contenido: _Optional[str] = ...) -> None: ...

class EliminarRequest(_message.Message):
    __slots__ = ("usuario", "idCorreo", "Bandeja")
    USUARIO_FIELD_NUMBER: _ClassVar[int]
    IDCORREO_FIELD_NUMBER: _ClassVar[int]
    BANDEJA_FIELD_NUMBER: _ClassVar[int]
    usuario: str
    idCorreo: str
    Bandeja: TipoBandeja
    def __init__(self, usuario: _Optional[str] = ..., idCorreo: _Optional[str] = ..., Bandeja: _Optional[_Union[TipoBandeja, str]] = ...) -> None: ...
