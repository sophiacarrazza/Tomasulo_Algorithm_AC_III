# Simulador do Algoritmo de Tomasulo

Este é um simulador didático do algoritmo de Tomasulo implementado em Python com interface gráfica. O simulador demonstra como funciona a execução superescalar com renomeação de registradores, buffer de reordenamento e especulação de branches.

## Características

- **Execução passo a passo**: Permite visualizar cada fase do pipeline (Issue, Execute, Write Result, Commit)
- **Buffer de Reordenamento (ROB)**: Implementa reordenação de instruções para especulação
- **Estações de Reserva**: Suporte para instruções inteiras e de ponto flutuante
- **Especulação de Branches**: Preditor de branch de 2 bits com penalidade de misprediction
- **Métricas de Desempenho**: IPC, stalls, bubbles, etc.
- **Interface Gráfica**: Visualização em tempo real do estado do pipeline

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd Tomasulo_Algorithm_AC_III
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

### Executando o Simulador

```bash
python main.py
```

### Interface Gráfica

A interface gráfica inclui:

- **Painel de Controles**: Botões para Step, Run, Stop, Reset e Load Program
- **Editor de Programa**: Área de texto para inserir código MIPS
- **Métricas**: IPC, instruções completadas, stalls, bubbles
- **Reorder Buffer**: Visualização do estado do ROB
- **Estações de Reserva**: Estado das estações de reserva (Integer e FP)
- **Registradores**: Valores e tags dos registradores
- **Memória**: Conteúdo da memória

### Instruções Suportadas

O simulador suporta as seguintes instruções MIPS:

#### Instruções Aritméticas
- **Básicas**: ADD, SUB, MUL, DIV
- **Imediato**: ADDI

#### Instruções de Memória
- **Load**: LW
- **Store**: SW

#### Instruções de Branch
- **Condicionais**: BEQ, BNE

### Exemplo de Programa

```mips
# Programa de exemplo demonstrando as instruções suportadas
ADD R1, R2, R3      # R1 = R2 + R3
MUL R4, R1, R5      # R4 = R1 * R5 (dependência de R1)

# Instruções de imediato
ADDI R6, R4, 10     # R6 = R4 + 10
SUB R7, R6, R5      # R7 = R6 - R5

# Instruções de memória
LW R8, 100          # R8 = Memory[100]
SW R7, 200          # Memory[200] = R7

# Instruções de branch
BEQ R1, R2, 8       # Branch se R1 == R2
BNE R3, R4, 12      # Branch se R3 != R4

# Mais operações aritméticas
DIV R9, R8, R1      # R9 = R8 / R1
ADD R10, R9, R6     # R10 = R9 + R6
```

## Arquitetura do Simulador

### Componentes Principais

1. **TomasuloCore**: Classe principal que coordena a simulação
2. **ReorderBuffer**: Buffer de reordenamento para especulação
3. **ReservationStations**: Estações de reserva para diferentes tipos de instrução
4. **CommonDataBus**: Barramento de dados comum para broadcast de resultados
5. **TwoBitPredictor**: Preditor de branch de 2 bits
6. **RegisterBank**: Banco de registradores com renomeação

### Fases do Pipeline

1. **Issue**: Despacho de instruções para estações de reserva
2. **Execute**: Execução das instruções nas unidades funcionais
3. **Write Result**: Escrita de resultados no CDB
4. **Commit**: Commit das instruções do ROB

### Especulação de Branches

- Preditor de branch de 2 bits
- Penalidade de 10 ciclos para misprediction
- Flush do pipeline em caso de misprediction

## Configuração

As configurações do simulador podem ser ajustadas no arquivo `simulator/config.py`:

- Tamanho do ROB
- Número de estações de reserva
- Latências das instruções
- Penalidade de branch

## Testes

Para executar os testes:

```bash
python simulator/tests/test_core.py
```

## Estrutura do Projeto

```
Tomasulo_Algorithm_AC_III/
├── main.py                 # Ponto de entrada
├── requirements.txt        # Dependências
├── README.md              # Este arquivo
└── simulator/
    ├── core.py            # Implementação principal do algoritmo
    ├── gui.py             # Interface gráfica
    ├── parser.py          # Parser de instruções MIPS
    ├── config.py          # Configurações
    ├── components/        # Componentes do simulador
    │   ├── branch_predictor.py
    │   ├── cdb.py
    │   ├── reorder_buffer.py
    │   └── reservation_station.py
    └── tests/             # Testes
        └── test_core.py
```

## Contribuição

Para contribuir com o projeto:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Implemente suas mudanças
4. Adicione testes
5. Faça commit e push
6. Abra um Pull Request

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.


