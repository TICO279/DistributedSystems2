from mensajes_db import inicializar_bd, create_message, get_inbox, get_outbox, mark_as_read, delete_message

def main():
    # Reset test DB
    import os
    if os.path.exists("mensajes.db"):
        os.remove("mensajes.db")

    inicializar_bd()
    # Insert 2 messages
    create_message("1","alice","bob","Hola","¿Cómo estás?")
    create_message("2","bob","alice","Re:Hola","Bien, gracias.")

    print("Alice inbox:", get_inbox("alice"))
    print("Bob inbox:", get_inbox("bob"))

    mark_as_read("2","alice")
    print("Alice after read:", get_inbox("alice"))

    delete_message("1","bob","entrada")
    print("Bob after delete:", get_inbox("bob"))

if __name__=="__main__":
    main()
