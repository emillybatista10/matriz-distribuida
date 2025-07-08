
# Sistema Distribuído de Processamento de Matrizes

Sistema distribuído para processamento de matrizes utilizando Docker e comunicação TCP entre containers.

##  Descrição

Este projeto implementa um sistema distribuído composto por três programas que trabalham em conjunto para processar matrizes:

- **prog1.py**: Gera matrizes aleatórias e envia via TCP para prog2
- **prog2.py**: Calcula determinante e matriz inversa, envia resultados para prog3
- **prog3.py**: Exibe resultados formatados com estatísticas de tempo

##  Arquitetura

```
┌─────────────┐  TCP:8001  ┌─────────────┐  TCP:8002  ┌─────────────┐
│    prog1    │──────────▶│    prog2    │──────────▶│    prog3    │
│  (Gerador)  │            │(Processador)│            │ (Exibidor)  │
└─────────────┘            └─────────────┘            └─────────────┘
```

## Execução Rápida

### Usando Docker Compose (Recomendado)

```bash
# Execute o sistema
docker compose up --build

# Para executar com parâmetros customizados
MATRIX_SIZE=50 NUM_MATRICES=3 docker compose up --build
```

### Execução Local (sem Docker)

```bash
# Instale as dependências
pip install -r requirements.txt

# Execute em terminais separados (ordem importante):
# Terminal 1:
python src/prog1.py 3 2

# Terminal 2 (após prog1 iniciar):
python src/prog2.py

# Terminal 3 (após prog2 conectar):
python src/prog3.py
```

## 📁 Estrutura do Projeto

```
matriz-distribuida/
├── src/                    # Código fonte
│   ├── prog1.py           # Gerador de matrizes (servidor TCP:8001)
│   ├── prog2.py           # Processador (cliente:8001, servidor:8002)
│   ├── prog3.py           # Exibidor (cliente:8002)
│   └── common.py          # Funções de comunicação TCP e logging
├── docker/                # Dockerfiles
│   ├── Dockerfile.prog1
│   ├── Dockerfile.prog2
│   └── Dockerfile.prog3
├── docker-compose.yml     # Orquestração dos containers
├── requirements.txt       # Dependências Python
├── .env                   # Variáveis de ambiente
└── README.md             # Documentação
```

##  Configuração

### Variáveis de Ambiente (.env)

```env
# Configurações da matriz
MATRIX_SIZE=100
NUM_MATRICES=5

# Configurações de rede
NETWORK_NAME=matriz-network

# Configurações de volumes
DATA_VOLUME=matriz-data
```

### Requisitos

- Docker >= 20.10
- Docker Compose >= 2.0
- Python 3.11+ (para execução local)
- numpy >= 1.26.0

## Desenvolvimento

### Logs e Debugging

```bash
# Visualizar logs dos containers
docker compose logs -f

# Logs de um container específico
docker compose logs prog1

# Parar todos os containers
docker compose down
```

##  Funcionalidades

### prog1.py (Gerador)
- Gera matrizes quadradas com valores aleatórios (1-10)
- Atua como servidor TCP na porta 8001
- Envia matrizes via JSON para prog2
- Parâmetros: `python prog1.py <ordem> <num_matrizes>`

### prog2.py (Processador)
- Conecta ao prog1 (porta 8001) como cliente
- Atua como servidor TCP na porta 8002 para prog3
- Calcula determinante e matriz inversa
- Trata matrizes singulares adequadamente
- Envia resultados processados para prog3

### prog3.py (Exibidor)
- Conecta ao prog2 (porta 8002) como cliente
- Exibe resultados formatados com emojis
- Calcula estatísticas de tempo de processamento
- Mostra tempo total do sistema e tempo médio por matriz
