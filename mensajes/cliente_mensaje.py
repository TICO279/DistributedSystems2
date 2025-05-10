import sys, getpass, grpc
from typing import Optional
import tkinter as tk
from tkinter import messagebox

import mensaje_pb2, mensaje_pb2_grpc

API: Optional[mensaje_pb2_grpc.MensajeriaStub] = None
AUTH: Optional[mensaje_pb2_grpc.AutenticadorStub] = None
TOKEN: str = ""
USER: str = ""

# ------------------------------
#  Inicialización del canal
# ------------------------------

def init_channel() -> None:
    global API, AUTH
    chan = grpc.insecure_channel("localhost:50051")
    AUTH = mensaje_pb2_grpc.AutenticadorStub(chan)
    API = mensaje_pb2_grpc.MensajeriaStub(chan)

# ------------------------------
#  Ventana de Inicio de Sesión
# ------------------------------

class VentanaLogin:
    def __init__(self, root, auth_stub):
        self.root = root
        self.root.title("TurboMessage - Login")
        self.auth = auth_stub

        tk.Label(root, text="Usuario").pack()
        self.entry_usuario = tk.Entry(root)
        self.entry_usuario.pack()

        tk.Label(root, text="Contraseña").pack()
        self.entry_contra = tk.Entry(root, show="*")
        self.entry_contra.pack()

        tk.Button(root, text="Iniciar sesión", command=self.login).pack()

        tk.Button(root, text="Registrarse", command=self.abrir_ventana_registro).pack()

    def abrir_ventana_registro(self):
        ventana_registro = tk.Toplevel(self.root)
        self.root.withdraw()
        VentanaRegistro(ventana_registro, self.auth)

    def login(self):
        import mensaje_pb2  # evita circularidad
        global TOKEN, USER
        usuario = self.entry_usuario.get()
        contrasena = self.entry_contra.get()
        rsp = self.auth.Autenticar(mensaje_pb2.AuthenticationRequest(usuario=usuario, contrasena=contrasena))
        if rsp.status:
            TOKEN = rsp.token
            USER = usuario
            messagebox.showinfo("Login", "Inicio de sesión exitoso")
            self.root.destroy()
            nuevo_root = tk.Tk()
            VentanaMenuPrincipal(nuevo_root)
            nuevo_root.mainloop()
        else:
            messagebox.showerror("Error", rsp.mensaje)

# ------------------------------
#  Ventana de registrar cuenta
# ------------------------------

class VentanaRegistro:
    def __init__(self, root, auth_stub):
        self.root = root
        self.root.title("TurboMessage - Registro")
        self.auth = auth_stub

        tk.Label(root, text="Nuevo usuario").pack()
        self.entry_usuario = tk.Entry(root)
        self.entry_usuario.pack()

        tk.Label(root, text="Contraseña").pack()
        self.entry_contra = tk.Entry(root, show="*")
        self.entry_contra.pack()

        tk.Button(root, text="Registrar", command=self.registrar).pack()

    def registrar(self):
        import mensaje_pb2
        usuario = self.entry_usuario.get()
        contrasena = self.entry_contra.get()
        rsp = self.auth.Registrar(mensaje_pb2.AuthenticationRequest(usuario=usuario, contrasena=contrasena))
        if rsp.status:
            global USER, TOKEN
            USER = usuario
            TOKEN = ""
            messagebox.showinfo("Registro", rsp.mensaje)
            self.root.destroy()
            nuevo_root = tk.Tk()
            VentanaMenuPrincipal(nuevo_root)
            nuevo_root.mainloop()
        else:
            messagebox.showerror("Error", rsp.mensaje)

# ------------------------------
#  Ventana Menú Principal
# ------------------------------

class VentanaMenuPrincipal:
    
    def __init__(self, root):
        self.root = root
        self.root.title("TurboMessage - Menú Principal")

        tk.Label(root, text=f"Bienvenido, {USER}").pack(pady=10)

        tk.Button(root, text="Bandeja de Entrada", command=self.ver_bandeja_entrada).pack(pady=5)
        tk.Button(root, text="Redactar Correo", command=self.redactar_correo).pack(pady=5)
        tk.Button(root, text="Cerrar Sesión", command=self.root.quit).pack(pady=20)

    def ver_bandeja_entrada(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Bandeja de Entrada")

        lista = tk.Listbox(ventana, width=80)
        lista.pack(padx=10, pady=10)

        correos = []

        try:
            rsp = API.ObtenerBandejaEntrada(mensaje_pb2.UserRequest(usuario=USER, token=TOKEN))
            if not rsp.correos:
                lista.insert(tk.END, "(Bandeja Vacía)")
            else:
                for c in rsp.correos:
                    flag = "✓" if c.leido else "•"
                    linea = f"{flag} {c.idCorreo[:8]}  {c.remitente:<10}  {c.asunto}"
                    lista.insert(tk.END, linea)
                    correos.append(c)
        except Exception as e:
            lista.insert(tk.END, f"⚠️ Error: {str(e)}")
    
        def abrir_correo(event):
            seleccion = lista.curselection()
            if not seleccion:
                return
            idx = seleccion[0]
            if idx >= len(correos):
                return
            correo = correos[idx]

            try:
                bandeja_rsp = API.ObtenerBandejaEntrada(mensaje_pb2.UserRequest(usuario=USER, token=TOKEN))
                correo_actual = None
                for c in bandeja_rsp.correos:
                    if c.idCorreo == correo.idCorreo:
                        correo_actual = c
                        break
                if correo_actual is None:
                    messagebox.showerror("Error", "No se pudo encontrar el correo seleccionado.")
                    return
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo obtener el correo: {str(e)}")
                return
            
            try:
                API.Leido(mensaje_pb2.LeidoRequest(usuario=USER, idCorreo=correo_actual.idCorreo, token=TOKEN))
            except Exception as e:
                pass

            vista = tk.Toplevel(ventana)
            vista.title("Leer Correo")
            contenido = f"De: {correo_actual.remitente}\nAsunto: {correo_actual.asunto}\nFecha: {correo_actual.fecha}\n\n{correo_actual.contenido}"
            tk.Message(vista, text=contenido, width=600).pack(padx=10, pady=10)

        lista.bind("<Double-1>", abrir_correo)


    def redactar_correo(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Redactar Correo")

        tk.Label(ventana, text="Para:").pack()
        entry_para = tk.Entry(ventana, width=50)
        entry_para.pack()

        tk.Label(ventana, text="Asunto:").pack()
        entry_asunto = tk.Entry(ventana, width=50)
        entry_asunto.pack()

        tk.Label(ventana, text="Mensaje:").pack()
        text_mensaje = tk.Text(ventana, width=60, height=10)
        text_mensaje.pack()

        def enviar():
            dst = entry_para.get()
            asunto = entry_asunto.get()
            cuerpo = text_mensaje.get("1.0", tk.END).strip()
            try:
                rsp = API.EnviarCorreo(mensaje_pb2.CorreoNuevo(
                    remitente=USER,
                    destinatario=dst,
                    asunto=asunto,
                    contenido=cuerpo,
                    token=TOKEN
                ))
                if rsp.exito:
                    messagebox.showinfo("Éxito", "Correo enviado correctamente")
                    ventana.destroy()
                else:
                    messagebox.showerror("Error", rsp.message)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo enviar el correo {str(e)}")
        tk.Button(ventana, text="Enviar", command=enviar).pack(pady=10)

# ------------------------------
#  Comandos del CLI
# ------------------------------

def cmd_register() -> None:
    u = input("Nuevo usuario: ")
    p = getpass.getpass("Contraseña: ")
    rsp = AUTH.Registrar(mensaje_pb2.AuthenticationRequest(usuario=u, contrasena=p))
    icon = "✅" if rsp.status else "❌"
    print(f"{icon} {rsp.mensaje}")


def cmd_login() -> None:
    global TOKEN, USER
    u = input("Usuario: ")
    p = getpass.getpass("Contraseña: ")
    rsp = AUTH.Autenticar(mensaje_pb2.AuthenticationRequest(usuario=u, contrasena=p))
    if rsp.status:
        TOKEN, USER = rsp.token, u
        print("🔓  Sesión iniciada.")
    else:
        print("❌  ", rsp.mensaje)


def cmd_inbox() -> None:
    rsp = API.ObtenerBandejaEntrada(mensaje_pb2.UserRequest(usuario=USER, token=TOKEN))
    if not rsp.correos:
        print("(bandeja vacía)")
        return
    for c in rsp.correos:
        flag = "✓" if c.leido else "•"
        print(f"{flag} {c.idCorreo[:8]}  {c.remitente:<10}  {c.asunto}")


def cmd_send() -> None:
    dst = input("Para:    ")
    subj = input("Asunto:  ")
    body = input("Mensaje: ")
    rsp = API.EnviarCorreo(mensaje_pb2.CorreoNuevo(
        remitente=USER, destinatario=dst, asunto=subj, contenido=body, token=TOKEN))
    icon = "✅" if rsp.exito else "❌"
    print(f"{icon} {rsp.mensaje}")


def cmd_mark_read() -> None:
    mid = input("ID del correo a marcar leído: ")
    rsp = API.Leido(mensaje_pb2.LeidoRequest(idCorreo=mid, usuario=USER, token=TOKEN))
    icon = "✅" if rsp.exito else "❌"
    print(f"{icon} {rsp.mensaje}")


def cmd_delete() -> None:
    mid = input("ID del correo a eliminar: ")
    rsp = API.EliminarCorreo(mensaje_pb2.EliminarRequest(
        idCorreo=mid, usuario=USER, Bandeja=mensaje_pb2.ENTRADA, token=TOKEN))
    icon = "✅" if rsp.exito else "❌"
    print(f"{icon} {rsp.mensaje}")

# ------------------------------
#  Tabla de comandos
# ------------------------------

MENU = {
    "r": cmd_register,
    "l": cmd_login,
    "i": cmd_inbox,
    "s": cmd_send,
    "m": cmd_mark_read,
    "d": cmd_delete,
    "q": lambda: sys.exit(0),
}

# ------------------------------
#  Bucle interactivo
# ------------------------------

def main() -> None:
    init_channel()
    print("Comandos: r egistrar · l ogin · i nbox · s end · m ark read · d elete · q uit")
    while True:
        cmd = input("> ").strip().lower()
        MENU.get(cmd, lambda: print("¿? comando desconocido"))()


if __name__ == "__main__":
    init_channel()
    ventana = tk.Tk()
    VentanaLogin(ventana, AUTH)
    ventana.mainloop()
