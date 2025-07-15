# TurboMessage

This project implements a **distributed email system** in Python using **gRPC**, with both a **graphical Tkinter interface** and **command-line support**. It features user authentication, secure token-based messaging, inbox/outbox management, and SQLite-based persistent storage.

## Features

- **gRPC Server in Python**:
  - Handles user authentication, email sending, inbox/outbox retrieval, marking messages as read, and logical deletion.
  - Uses UUID-based token validation for user sessions.
  - Enforces per-user message limits (5 messages per inbox/outbox).

- **Tkinter GUI Client**:
  - `cliente_mensaje.py`: Login, registration, email composing, inbox/outbox viewing, and message deletion.
  - Responsive layout with modal windows for each operation.
  - Visually marks unread emails and updates status upon read.

- **Command-Line Interface**:
  - CLI built into `cliente_mensaje.py` allows registration, login, sending messages, viewing inbox, marking as read, and deleting.
  - Useful for quick testing or terminal usage.

- **Database Management**:
  - `mensajes_db.py`: Handles message creation, retrieval, update, and logical deletion with `threading.Lock`.
  - `usuarios.py`: Stores hashed user passwords and checks for uniqueness during registration.

- **Testing Scripts**:
  - `test_usuario.py`: Validates user registration and login with correct/incorrect passwords.
  - `test_mensajes_db.py`: Inserts test messages, simulates reading/deletion, and prints inbox status.

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/YourUsername/TurboMessage.git
   cd TurboMessage


2.  **Generate Protobuf Files**:
    ```bash
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. mensaje.proto

3.  **Run the Server**:
    ```bash
    python servidor_mensaje.py

4.  **Start the Client**:
    ```bash
    python cliente_mensaje.py

5.  **Run Tests (Optional)**:
    ```bash
    python test_usuario.py
    python test_mensajes_db.py

## Notes and Limitations

-   The server stores tokens in memory; sessions reset when the server restarts.

-   Each inbox and outbox is limited to 5 messages per user.

-   Deletion is logical first; messages are physically deleted when both sender and recipient remove them.

-   No attachments or rich formatting are supported --- only plain text emails.

-   GUI uses Tkinter, which may require adaptation for different platforms.

-   Error handling assumes correct server availability; no retries or failovers are implemented.
