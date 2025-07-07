
#!/usr/bin/env python3
"""
prog1.py - Gerador de Matrizes
Cria matrizes com valores aleatórios e envia via TCP para prog2
"""

import numpy as np
import socket
import sys
import time
from common import setup_logging, send_json_data, create_server_socket

def generate_random_matrix(order: int) -> list:
    """Gera uma matriz quadrada com valores aleatórios"""
    # Gera valores entre 1 e 10 para evitar matrizes singulares
    matrix = np.random.uniform(1, 10, (order, order))
    return matrix.tolist()

def main():
    logger = setup_logging("PROG1")
    
    if len(sys.argv) != 3:
        logger.error("Uso: python prog1.py <ordem_matriz> <numero_matrizes>")
        sys.exit(1)
    
    try:
        order = int(sys.argv[1])
        num_matrices = int(sys.argv[2])
        
        if order <= 0 or num_matrices <= 0:
            raise ValueError("Ordem e número de matrizes devem ser positivos")
            
    except ValueError as e:
        logger.error(f"Argumentos inválidos: {e}")
        sys.exit(1)
    
    logger.info(f"Iniciando prog1 - Ordem: {order}, Número de matrizes: {num_matrices}")
    
    # Configuração do servidor
    HOST = '0.0.0.0'
    PORT = 8001
    
    try:
        # Cria servidor TCP
        server_socket = create_server_socket(HOST, PORT)
        logger.info(f"Servidor prog1 ouvindo em {HOST}:{PORT}")
        
        # Aguarda conexão do prog2
        logger.info("Aguardando conexão do prog2...")
        client_socket, client_address = server_socket.accept()
        logger.info(f"prog2 conectado de {client_address}")
        
        # Gera e envia matrizes
        for i in range(num_matrices):
            logger.info(f"Gerando matriz {i+1}/{num_matrices}")
            
            matrix = generate_random_matrix(order)
            timestamp = time.time()
            
            data = {
                'matrix_id': i + 1,
                'matrix': matrix,
                'order': order,
                'timestamp': timestamp,
                'total_matrices': num_matrices
            }
            
            send_json_data(client_socket, data)
            logger.info(f"Matriz {i+1} enviada para prog2")
        
        # Envia sinal de fim
        end_signal = {
            'matrix_id': -1,  # Sinal de fim
            'message': 'FIM'
        }
        send_json_data(client_socket, end_signal)
        logger.info("Sinal de fim enviado para prog2")
        
    except Exception as e:
        logger.error(f"Erro em prog1: {e}")
        sys.exit(1)
    
    finally:
        try:
            client_socket.close()
            server_socket.close()
            logger.info("prog1 finalizado")
        except:
            pass

if __name__ == "__main__":
    main()
