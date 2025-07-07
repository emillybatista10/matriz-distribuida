
#!/usr/bin/env python3
"""
prog2.py - Processador de Matrizes
Recebe matrizes de prog1, calcula inversa e determinante, envia para prog3
"""

import numpy as np
import socket
import sys
import time
from common import setup_logging, send_json_data, receive_json_data, create_server_socket, create_client_socket

def process_matrix(matrix_data: list) -> dict:
    """Processa a matriz: calcula inversa e determinante"""
    matrix = np.array(matrix_data)
    
    try:
        # Calcula determinante
        det = np.linalg.det(matrix)
        
        # Calcula matriz inversa (se possível)
        if abs(det) < 1e-10:  # Matriz quase singular
            inverse = None
            error = "Matriz singular ou quase singular"
        else:
            inverse = np.linalg.inv(matrix).tolist()
            error = None
            
        return {
            'determinant': float(det),
            'inverse': inverse,
            'error': error
        }
        
    except np.linalg.LinAlgError as e:
        return {
            'determinant': None,
            'inverse': None,
            'error': f"Erro de álgebra linear: {str(e)}"
        }

def main():
    logger = setup_logging("PROG2")
    logger.info("Iniciando prog2")
    
    # Configuração como cliente do prog1
    PROG1_HOST = 'prog1'  # Nome do container
    PROG1_PORT = 8001
    
    # Configuração como servidor para prog3
    HOST = '0.0.0.0'
    PORT = 8002
    
    prog1_socket = None
    prog3_socket = None
    server_socket = None
    
    try:
        # Conecta ao prog1
        logger.info(f"Conectando ao prog1 em {PROG1_HOST}:{PROG1_PORT}")
        prog1_socket = create_client_socket(PROG1_HOST, PROG1_PORT)
        logger.info("Conectado ao prog1")
        
        # Cria servidor para prog3
        server_socket = create_server_socket(HOST, PORT)
        logger.info(f"Servidor prog2 ouvindo em {HOST}:{PORT}")
        
        # Aguarda conexão do prog3
        logger.info("Aguardando conexão do prog3...")
        prog3_socket, prog3_address = server_socket.accept()
        logger.info(f"prog3 conectado de {prog3_address}")
        
        # Processa matrizes
        matrix_count = 0
        while True:
            try:
                # Recebe dados do prog1
                data = receive_json_data(prog1_socket)
                
                # Verifica se é sinal de fim
                if data.get('matrix_id') == -1:
                    logger.info("Sinal de fim recebido do prog1")
                    # Envia sinal de fim para prog3
                    end_signal = {
                        'matrix_id': -1,
                        'message': 'FIM'
                    }
                    send_json_data(prog3_socket, end_signal)
                    break
                
                matrix_count += 1
                matrix_id = data['matrix_id']
                logger.info(f"Processando matriz {matrix_id}")
                
                # Processa a matriz
                result = process_matrix(data['matrix'])
                
                # Prepara dados para envio ao prog3
                response = {
                    'matrix_id': matrix_id,
                    'original_timestamp': data['timestamp'],
                    'processing_timestamp': time.time(),
                    'order': data['order'],
                    'determinant': result['determinant'],
                    'inverse': result['inverse'],
                    'error': result['error'],
                    'total_matrices': data['total_matrices']
                }
                
                # Envia resultado para prog3
                send_json_data(prog3_socket, response)
                
                if result['error']:
                    logger.warning(f"Matriz {matrix_id}: {result['error']}")
                else:
                    logger.info(f"Matriz {matrix_id} processada - Det: {result['determinant']:.4f}")
                    
            except Exception as e:
                logger.error(f"Erro ao processar matriz: {e}")
                break
        
        logger.info(f"prog2 processou {matrix_count} matrizes")
        
    except Exception as e:
        logger.error(f"Erro em prog2: {e}")
        sys.exit(1)
    
    finally:
        try:
            if prog1_socket:
                prog1_socket.close()
            if prog3_socket:
                prog3_socket.close()
            if server_socket:
                server_socket.close()
            logger.info("prog2 finalizado")
        except:
            pass

if __name__ == "__main__":
    main()
