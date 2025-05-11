# 📬 TurboMessage

TurboMessage es un sistema de mensajería distribuido desarrollado con Python y gRPC. Permite a los usuarios registrarse, iniciar sesión, enviar correos, revisar sus bandejas de entrada y salida, marcar mensajes como leídos y eliminar correos. Todo con persistencia en SQLite y una interfaz gráfica hecha con Tkinter.

---

## ⚙️ Características principales

- Registro y autenticación de usuarios (persistente).
- Envío de correos entre usuarios existentes.
- Bandeja de entrada y salida con límite de 5 mensajes cada una.
- Marcado de correos como leídos.
- Eliminación de correos.
- Gestión de sesiones seguras con tokens únicos.
- Interfaz gráfica completa y funcional.
- Concurrencia segura (uso de `threading.Lock` y `SQLite WAL`).
- Estructura modular (cliente, servidor, base de datos, pruebas).

---

## 🗂️ Estructura del proyecto

```
TURBOMESSAGE/
├── mensajes/
│   ├── cliente_mensaje.py       # Interfaz gráfica con Tkinter
│   ├── servidor_mensaje.py      # Servidor gRPC
│   ├── usuarios.py              # Gestión de usuarios
│   ├── mensajes_db.py           # Base de datos de correos
│   ├── test_usuario.py          # Pruebas de usuarios
│   ├── test_mensajes_db.py      # Pruebas de correos
│   ├── mensaje_pb2.py           # Generado automáticamente
│   ├── mensaje_pb2_grpc.py      # Generado automáticamente
│   ├── mensajes.db              # Base de datos de correos
│   ├── usuarios.db              # Base de datos de usuarios
│   └── __init__.py
├── protos/
│   └── mensaje.proto            # Archivo .proto con definición del servicio
└── README.md
```

---

## 📦 Requisitos

- Python 3.9
- `protobuf >= 4.25.3`
- `grpcio >= 1.60.0`
- `grpcio-tools`

Instala los paquetes necesarios:

```bash
pip install protobuf==4.25.3 grpcio==1.60.0 grpcio-tools
```

O si utilizas un ambiente de Conda:
- Puedes descargarlo desde Anaconda
- Utilizar el comando:
```bash
conda install -c conda-forge protobuf=4.25.3 grpcio=1.60.0
```

---

## 🔧 Generación de stubs gRPC

Desde el directorio raíz del proyecto:

```bash
python -m grpc_tools.protoc -I. --python_out=mensajes --pyi_out=mensajes --grpc_python_out=mensajes ./protos/mensaje.proto
```

> ⚠️ En Mac se requiere Python 3.10 específicamente para compatibilidad completa con `grpcio`.

---

## 🚀 Cómo ejecutar

### 1. Inicia el servidor

```bash
python mensajes/servidor_mensaje.py
```

### 2. Ejecuta el cliente (interfaz)

```bash
python mensajes/cliente_mensaje.py
```

---

## 🧪 Pruebas

Puedes ejecutar pruebas básicas con:

```bash
python mensajes/test_usuario.py
python mensajes/test_mensajes_db.py
```

---

## 🛡️ Seguridad

- Las contraseñas se almacenan con hash SHA-256.
- Las sesiones de usuarios están protegidas con tokens UUID4.
- Acceso a base de datos protegido con `threading.Lock` y modo `WAL` activado.

---

## 📝 Licencia

Este proyecto fue desarrollado con fines académicos. Libre de uso bajo los términos de la licencia MIT.

---

## 👨‍💻 Autores

**Abraham Martínez Cerón y Patricio Pizaña Vela**  
Proyecto desarrollado para la asignatura de Sistemas Distribuidos.