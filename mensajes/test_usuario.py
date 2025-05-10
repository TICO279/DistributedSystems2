from usuarios import inicializar_bd, registrar_usuarios, autenticar_usuario

def main():
    inicializar_bd()
    # Try registering a user
    ok = registrar_usuarios("alice", "s3cret")
    print("Registered alice:", ok)
    # Authenticate correct password
    print("Auth alice / s3cret:", autenticar_usuario("alice", "s3cret"))
    # Wrong password
    print("Auth alice / wrong:", autenticar_usuario("alice", "wrong"))

if __name__ == "__main__":
    main()
