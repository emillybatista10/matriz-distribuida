
#!/usr/bin/env python3
"""
prog3.py - Exibidor de Resultados
Recebe resultados de prog2 e exibe na tela com tempo total
"""

import socket
import sys
import time
from common import setup_logging, receive_json_data, create_client_socket

def format_matrix(matrix: list, precision: int = 4) -> str:
    """Formata matriz para exibição"""
    if matrix is None:
        return "Matriz não disponível"
    
    lines = []
    for row in matrix:
        formatted_row = [f"{val:>{precision+6}.{precision}f}" for val in row]
        lines.append("  [" + " ".join(formatted_row) + "]")
    
    return "\n".join(lines)

def main():
    logger = setup_logging("PROG3")
    logger.info("Iniciando prog3")
    
    # Configuração como cliente do prog2
    PROG2_HOST = 'prog2'  # Nome do container
    PROG2_PORT = 8002
    
    prog2_socket = None
    
    try:
        # Conecta ao prog2
        logger.info(f"Conectando ao prog2 em {PROG2_HOST}:{PROG2_PORT}")
        prog2_socket = create_client_socket(PROG2_HOST, PROG2_PORT)
        logger.info("Conectado ao prog2")
        
        # Recebe e exibe resultados
        matrix_count = 0
        total_processing_time = 0
        first_timestamp = None
        
        print("\n" + "="*80)
        print("SISTEMA DISTRIBUÍDO DE PROCESSAMENTO DE MATRIZES")
        print("="*80)
        
        while True:
            try:
                # Recebe dados do prog2
                data = receive_json_data(prog2_socket)
                
                # Verifica se é sinal de fim
                if data.get('matrix_id') == -1:
                    logger.info("Sinal de fim recebido do prog2")
                    break
                
                matrix_count += 1
                matrix_id = data['matrix_id']
                
                # Calcula tempos
                original_timestamp = data['original_timestamp']
                processing_timestamp = data['processing_timestamp']
                current_timestamp = time.time()
                
                if first_timestamp is None:
                    first_timestamp = original_timestamp
                
                total_time = current_timestamp - original_timestamp
                processing_time = processing_timestamp - original_timestamp
                display_time = current_timestamp - processing_timestamp
                
                total_processing_time = current_timestamp - first_timestamp
                
                # Exibe resultado
                print(f"\n{'─'*80}")
                print(f"MATRIZ {matrix_id}/{data['total_matrices']} (Ordem {data['order']}x{data['order']})")
                print(f"{'─'*80}")
                
                if data['error']:
                    print(f"❌ ERRO: {data['error']}")
                else:
                    print(f"✅ DETERMINANTE: {data['determinant']:.6f}")
                    print(f"\n📊 MATRIZ INVERSA:")
                    print(format_matrix(data['inverse']))
                
                print(f"\n⏱️  TEMPOS:")
                print(f"   • Geração → Processamento: {processing_time:.4f}s")
                print(f"   • Processamento → Exibição: {display_time:.4f}s")
                print(f"   • Tempo total (geração → exibição): {total_time:.4f}s")
                
                logger.info(f"Matriz {matrix_id} exibida - Tempo total: {total_time:.4f}s")
                
            except Exception as e:
                logger.error(f"Erro ao receber dados: {e}")
                break
        
        # Exibe estatísticas finais
        print(f"\n{'='*80}")
        print(f"ESTATÍSTICAS FINAIS")
        print(f"{'='*80}")
        print(f"📈 Total de matrizes processadas: {matrix_count}")
        print(f"⏱️  Tempo total do sistema: {total_processing_time:.4f}s")
        if matrix_count > 0:
            print(f"📊 Tempo médio por matriz: {total_processing_time/matrix_count:.4f}s")
        print(f"{'='*80}\n")
        
        logger.info(f"prog3 exibiu {matrix_count} matrizes em {total_processing_time:.4f}s")
        
    except Exception as e:
        logger.error(f"Erro em prog3: {e}")
        sys.exit(1)
    
    finally:
        try:
            if prog2_socket:
                prog2_socket.close()
            logger.info("prog3 finalizado")
        except:
            pass

if __name__ == "__main__":
    main()
