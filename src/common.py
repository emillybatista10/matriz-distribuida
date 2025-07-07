
import json
import socket
import logging
from typing import Any, Dict

def setup_logging(program_name: str) -> logging.Logger:
    """Configura logging para cada programa"""
    logger = logging.getLogger(program_name)
    logger.setLevel(logging.INFO)
    
    # Remove handlers existentes para evitar duplicação
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        f'[{program_name}] %(asctime)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

def send_json_data(sock: socket.socket, data: Dict[str, Any]) -> None:
    """Envia dados JSON via socket TCP"""
    json_data = json.dumps(data)
    message = json_data.encode('utf-8')
    message_length = len(message)
    
    # Envia o tamanho da mensagem primeiro (4 bytes)
    sock.sendall(message_length.to_bytes(4, byteorder='big'))
    # Envia a mensagem
    sock.sendall(message)

def receive_json_data(sock: socket.socket) -> Dict[str, Any]:
    """Recebe dados JSON via socket TCP"""
    # Recebe o tamanho da mensagem (4 bytes)
    length_bytes = sock.recv(4)
    if not length_bytes:
        raise ConnectionError("Conexão fechada pelo peer")
    
    message_length = int.from_bytes(length_bytes, byteorder='big')
    
    # Recebe a mensagem completa
    message = b''
    while len(message) < message_length:
        chunk = sock.recv(message_length - len(message))
        if not chunk:
            raise ConnectionError("Conexão fechada durante recebimento")
        message += chunk
    
    return json.loads(message.decode('utf-8'))

def create_server_socket(host: str, port: int) -> socket.socket:
    """Cria e configura socket servidor"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    return server_socket

def create_client_socket(host: str, port: int, max_retries: int = 10) -> socket.socket:
    """Cria socket cliente com retry automático"""
    import time
    
    for attempt in range(max_retries):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            return client_socket
        except ConnectionRefusedError:
            if attempt < max_retries - 1:
                time.sleep(1)  # Aguarda 1 segundo antes de tentar novamente
                continue
            raise
    
    raise ConnectionError(f"Não foi possível conectar após {max_retries} tentativas")
