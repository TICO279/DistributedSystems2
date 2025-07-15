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

def centrar_ventana(ventana, ancho=400, alto=300):
    ventana.update_idletasks()
    w = ancho
    h = alto
    x = (ventana.winfo_screenwidth() // 2) - (w // 2)
    y = (ventana.winfo_screenheight() // 2) - (h // 2)
    ventana.geometry(f"{w}x{h}+{x}+{y}")

# ------------------------------
#  Ventana de Inicio de Sesión
# ------------------------------

class VentanaLogin:
    def __init__(self, root, auth_stub):
        self.root = root
        self.root.title("TurboMessage - Login")
        centrar_ventana(root, 400, 250)
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
        centrar_ventana(ventana_registro, 400, 250)
        VentanaRegistro(ventana_registro, self.auth)
        ventana_registro.transient(self.root)
        ventana_registro.grab_set()
        self.root.wait_window(ventana_registro)

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
        centrar_ventana(root, 400, 250)
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
            VentanaLogin(nuevo_root, self.auth)
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
        centrar_ventana(root, 400, 300)

        tk.Label(root, text=f"Bienvenido, {USER}").pack(pady=10)

        tk.Button(root, text="Bandeja de Entrada", command=self.ver_bandeja_entrada).pack(pady=5)
        tk.Button(root, text="Bandeja de Salida", command=self.ver_bandeja_salida).pack(pady=5)
        tk.Button(root, text="Redactar Correo", command=self.redactar_correo).pack(pady=5)
        tk.Button(root, text="Cerrar Sesión", command=self.cerrar_sesion).pack(pady=20)

    def cerrar_sesion(self):
        confirm = messagebox.askyesno("Confirmar", "¿Desea cerrar la sesión?")
        if not confirm:
            return

        global USER, TOKEN
        USER = ""
        TOKEN = ""
        
        self.root.destroy()
        nuevo_root = tk.Tk()
        VentanaLogin(nuevo_root, AUTH)
        nuevo_root.mainloop()

    def mostrar_bandeja(self, titulo: str, obtener_rpc, mostrar_remitente: bool):
        ventana = tk.Toplevel(self.root)
        centrar_ventana(ventana, 700, 400)
        ventana.title(titulo)
        ventana.transient(self.root)
        ventana.grab_set()
        
        lista = tk.Listbox(ventana, width=80)
        lista.pack(padx=10, pady=10)

        correos = []

        try:
            rsp = obtener_rpc(mensaje_pb2.UserRequest(usuario=USER, token=TOKEN))
            if not rsp.correos:
                lista.insert(tk.END, "(Bandeja Vacía)")
            else:
                for c in rsp.correos:
                    flag = "✓" if c.leido else "•"
                    persona = c.remitente if mostrar_remitente else c.destinatario
                    linea = f"{flag} {c.idCorreo[:8]}  {persona:<10}  {c.asunto}"
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
            if mostrar_remitente and not correo.leido:
                try:
                    API.Leido(mensaje_pb2.LeidoRequest(usuario=USER, idCorreo=correo.idCorreo, token=TOKEN))
                    correo.leido = True
                    flag = "✓"
                    persona = correo.remitente
                    nueva_linea = f"{flag} {correo.idCorreo[:8]}  {persona:<10}  {correo.asunto}"
                    lista.delete(idx)
                    lista.insert(idx, nueva_linea)
                except:
                    pass

            vista = tk.Toplevel(ventana)
            centrar_ventana(vista, 600, 350)
            vista.title("Leer Correo")
            vista.transient(ventana)
            vista.grab_set()

            cabecera = f"De: {correo.remitente}" if mostrar_remitente else f"Para: {correo.destinatario}"
            contenido = f"{cabecera}\nAsunto: {correo.asunto}\nFecha: {correo.fecha}\n\n{correo.contenido}"
            tk.Message(vista, text=contenido, width=600, justify="left").pack(padx=10, pady=10, anchor="w")

        lista.bind("<Double-1>", abrir_correo)

        def eliminar_correo():
            seleccion = lista.curselection()
            if not seleccion:
                return
            idx = seleccion[0]
            if idx >= len(correos):
                return
            correo = correos[idx]
            confirm = messagebox.askyesno("Confirmar", "¿Eliminar este correo?")
            if not confirm:
                return
            try:
                tipo_bandeja = mensaje_pb2.ENTRADA if mostrar_remitente else mensaje_pb2.SALIDA
                rsp = API.EliminarCorreo(mensaje_pb2.EliminarRequest(
                    usuario=USER,
                    idCorreo=correo.idCorreo,
                    Bandeja=tipo_bandeja,
                    token=TOKEN
                ))
                if rsp.exito:
                    messagebox.showinfo("Eliminado", "Correo eliminado correctamente")
                    ventana.destroy()
                    self.mostrar_bandeja(titulo=titulo, obtener_rpc=obtener_rpc, mostrar_remitente=mostrar_remitente)
                else:
                    messagebox.showerror("Error", rsp.mensaje)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el correo {str(e)}")
        tk.Button(ventana, text="Eliminar Correo", command=eliminar_correo).pack(pady=5)

        self.root.wait_window(ventana)

    def ver_bandeja_entrada(self):
        self.mostrar_bandeja("Bandeja de Entrada", API.ObtenerBandejaEntrada, mostrar_remitente=True)
    
    def ver_bandeja_salida(self):
        self.mostrar_bandeja("Bandeja de Salida", API.ObtenerBandejaSalida, mostrar_remitente=False)

    def redactar_correo(self):
        ventana = tk.Toplevel(self.root)
        centrar_ventana(ventana, 500, 400)
        ventana.title("Redactar Correo")
        ventana.transient(self.root)
        ventana.grab_set()

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
                    messagebox.showerror("Error", rsp.mensaje)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo enviar el correo {str(e)}")

        tk.Button(ventana, text="Enviar", command=enviar).pack(pady=10)

        self.root.wait_window(ventana)


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
"""
if __name__ == "__main__":
    init_channel()
    print("Comandos: r egistrar · l ogin · i nbox · s end · m ark read · d elete · q uit")
    while True:
        cmd = input("> ").strip().lower()
        MENU.get(cmd, lambda: print("¿? comando desconocido"))()
"""

if __name__ == "__main__":
    init_channel()
    ventana = tk.Tk()
    VentanaLogin(ventana, AUTH)
    ventana.mainloop()