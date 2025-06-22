from simulator.components.branch_predictor import TwoBitPredictor
from simulator.components.cdb import CommonDataBus
from simulator.components.reorder_buffer import ReorderBuffer
from simulator.components.reservation_station import ReservationStations
from simulator.parser import parse_instruction
import copy

class ROBState:
    EMPTY = 'Empty'
    ISSUED = 'Issued'
    EXECUTING = 'Executing'
    WRITEBACK = 'Writeback'
    COMMIT = 'Commit'

class RegisterBank:
    def __init__(self):
        self.registers = {}
        self.tags = {}
        self.values = {}
        
        # Inicializar registradores MIPS
        for i in range(32):
            reg_name = f"R{i}"
            self.registers[reg_name] = 0
            self.tags[reg_name] = None
            self.values[reg_name] = 0

class TomasuloCore:
    def __init__(self):
        self.state_stack = []
        self.cycle = 0
        self.instructions = []
        self.current_instruction = 0
        self.reservation_stations = ReservationStations()
        self.rob = ReorderBuffer(size=32)
        self.cdb = CommonDataBus()
        self.registers = RegisterBank()
        self.bp = TwoBitPredictor()
        self.metrics = {
            'ipc': 0.0,
            'stalls': 0,
            'total_instructions': 0,
            'completed_instructions': 0,
            'bubbles': 0
        }
        self.execution_units = {
            'INT_ALU1': {'busy': False, 'cycles_remaining': 0, 'current_instruction': None},
            'INT_ALU2': {'busy': False, 'cycles_remaining': 0, 'current_instruction': None},
            'FP_ALU': {'busy': False, 'cycles_remaining': 0, 'current_instruction': None},
            'FP_MUL': {'busy': False, 'cycles_remaining': 0, 'current_instruction': None},
            'FP_DIV': {'busy': False, 'cycles_remaining': 0, 'current_instruction': None},
            'MEM_LOAD': {'busy': False, 'cycles_remaining': 0, 'current_instruction': None},
            'MEM_STORE': {'busy': False, 'cycles_remaining': 0, 'current_instruction': None},
            'BRANCH': {'busy': False, 'cycles_remaining': 0, 'current_instruction': None}
        }
        self.memory = {}
        self.pc = 0
        self.branch_misprediction = False
        self.flush_needed = False
        self.state_stack = []  # Pilha para estados anteriores

    def save_state(self):
        # Salva uma cópia profunda do estado atual
        state = {
            'cycle': self.cycle,
            'instructions': copy.deepcopy(self.instructions),
            'current_instruction': self.current_instruction,
            'reservation_stations': copy.deepcopy(self.reservation_stations),
            'rob': copy.deepcopy(self.rob),
            'registers': copy.deepcopy(self.registers),
            # Adicione outros componentes se necessário
        }
        self.state_stack.append(state)

    def restore_state(self):
        if self.state_stack:
            state = self.state_stack.pop()
            self.cycle = state['cycle']
            self.instructions = copy.deepcopy(state['instructions'])
            self.current_instruction = state['current_instruction']
            self.reservation_stations = copy.deepcopy(state['reservation_stations'])
            self.rob = copy.deepcopy(state['rob'])
            self.registers = copy.deepcopy(state['registers'])

    def load_program(self, program_text):
        """Carrega um programa MIPS"""
        lines = program_text.strip().split('\n')
        self.instructions = []
        for line in lines:
            if line.strip() and not line.strip().startswith('#'):
                instruction = parse_instruction(line.strip())
                if instruction:
                    instruction['pc'] = len(self.instructions)
                    self.instructions.append(instruction)
        self.metrics['total_instructions'] = len(self.instructions)

    def cycle_step(self):
        self.save_state() 
        if not self._has_work_to_do():
            return False

        if self.flush_needed:
            self._flush_pipeline()
            self.flush_needed = False

        self._commit()
        self._write_result()
        self._execute()
        self._issue()

   
        self._count_bubbles()

        # Atualiza IPC, stalls, etc
        self.cycle += 1
        self._update_metrics()
        return True


    def _has_work_to_do(self):
        """Verifica se ainda há trabalho para fazer"""
        # Verificar se ainda há instruções para processar
        if self.current_instruction < len(self.instructions):
            return True
            
        # Verificar se há instruções pendentes no ROB
        for entry in self.rob.entries:
            if entry.state != 'Empty':
                return True
                
        # Verificar se há estações de reserva ocupadas
        for rs_type, stations in self.reservation_stations.stations.items():
            for rs in stations:
                if rs.busy:
                    return True
                    
        return False
    
    def _count_bubbles(self):
        bubbles_this_cycle = 0
        for rs_type, stations in self.reservation_stations.stations.items():
            for rs in stations:
                if rs.busy and (rs.qj is not None or rs.qk is not None):
                    bubbles_this_cycle += 1
        self.metrics['bubbles'] += bubbles_this_cycle


    def _issue(self):
        """Fase de despacho de instruções - Superescalar (múltiplas instruções por ciclo)"""
        
        if self.current_instruction >= len(self.instructions):
            return
            
        # Tentar despachar até 4 instruções por ciclo (grau de superescalar)
        instructions_issued = 0
        max_issue_per_cycle = 2
        
        while (self.current_instruction < len(self.instructions) and 
               instructions_issued < max_issue_per_cycle):
            instruction = self.instructions[self.current_instruction]
            
            # Verificar se há espaço no ROB
            if self.rob.entries[self.rob.tail].state == 'Empty':
                # Verificar se há estação de reserva disponível
                rs_type = self._get_rs_type(instruction['type'])
                available_rs = self._find_available_rs(rs_type)
                
                if available_rs is not None:
                    # Alocar entrada no ROB
                    rob_entry = self.rob.entries[self.rob.tail]
                    rob_entry.state = 'Issued'
                    rob_entry.instruction = instruction
                    # Para branch, destination é o próprio índice do ROB
                    if instruction['type'] == 'BRANCH':
                        rob_entry.destination = self.rob.tail
                    else:
                        rob_entry.destination = instruction['operands'][0]
                    
                    # Configurar estação de reserva
                    rs = available_rs
                    rs.busy = True
                    rs.op = instruction['opcode']
                    rs.dest = self.rob.tail
                    
                    # Capturar o tag do registrador de destino ANTES de atualizar
                    dest_reg = None
                    if instruction['type'] != 'BRANCH' and len(instruction['operands']) > 0:
                        dest_reg = instruction['operands'][0]
                        old_tag = self.registers.tags[dest_reg] if dest_reg in self.registers.tags else None
                    else:
                        old_tag = None
                    
                    # Verificar operandos
                    if len(instruction['operands']) > 1:
                        operand1 = instruction['operands'][1]
                        if operand1 in self.registers.tags:
                            if self.registers.tags[operand1] is None:
                                rs.vj = int(self.registers.values[operand1])
                                rs.qj = None
                            else:
                                rs.vj = None
                                rs.qj = self.registers.tags[operand1]
                        else:
                            rs.vj = 0
                            rs.qj = None
                    
                    if len(instruction['operands']) > 2:
                        operand2 = instruction['operands'][2]
                        if instruction['opcode'] == 'ADDI':
                            # Trata sempre como imediato
                            try:
                                rs.vk = int(operand2)
                                rs.qk = None
                            except Exception:
                                rs.vk = 0
                                rs.qk = None
                        else:
                            # Se for registrador
                            if operand2 in self.registers.tags:
                                if self.registers.tags[operand2] is None:
                                    rs.vk = int(self.registers.values[operand2])
                                    rs.qk = None
                                else:
                                    rs.vk = None
                                    rs.qk = self.registers.tags[operand2]
                            else:
                                # Caso não seja registrador conhecido, trata como 0
                                try:
                                    rs.vk = int(operand2)
                                    rs.qk = None
                                except Exception:
                                    rs.vk = 0
                                    rs.qk = None
                    
                    # Definir latência da instrução
                    rs.cycles_remaining = self._get_latency(instruction['opcode'])
                    
                    # Atualizar registrador de destino (exceto branch)
                    # CORREÇÃO: só atualizar o tag do registrador de destino DEPOIS de capturar dependências
                    if dest_reg is not None and dest_reg in self.registers.tags:
                        self.registers.tags[dest_reg] = self.rob.tail
                    
                    # Atualizar tail do ROB
                    self.rob.tail = (self.rob.tail + 1) % len(self.rob.entries)
                    
                    self.current_instruction += 1
                    instructions_issued += 1
                else:
                    # Não há estação de reserva disponível - stall
                    self.metrics['stalls'] += 1
                    break  # Parar de tentar despachar mais instruções
            else:
                # Não há espaço no ROB - stall
                self.metrics['stalls'] += 1
                break  # Parar de tentar despachar mais instruções

    def _execute(self):
    
        # Executar em todas as estações de reserva em paralelo
        for rs_type, stations in self.reservation_stations.stations.items():
            for rs in stations:
                if rs.busy and rs.qj is None and rs.qk is None and rs.cycles_remaining > 0:
                    # Se ainda estava no estado ISSUED, marca como EXECUTING no ROB
                    rob_entry = self.rob.entries[rs.dest]
                    if rob_entry.state == ROBState.ISSUED:
                        rob_entry.state = ROBState.EXECUTING


                    # Avança execução (decrementa ciclos restantes)
                    rs.cycles_remaining -= 1

                    # Se terminou execução
                    if rs.cycles_remaining == 0:
                        result = self._execute_instruction(rs.op, rs.vj, rs.vk)
                        rs.result = int(result) if result is not None else 0
                        rs.ready = True

    # Executar instruções de memória em paralelo com instruções aritméticas
        self._execute_memory_operations()

    def _execute_memory_operations(self):
        """Executa operações de memória em paralelo"""
        # Buscar instruções de memória prontas para execução
        for rs_type, stations in self.reservation_stations.stations.items():
            for rs in stations:
                if (rs.busy and rs.qj is None and rs.qk is None and 
                    rs.op in ['LW', 'SW'] and rs.cycles_remaining > 0):
                    rs.cycles_remaining -= 1
                    if rs.cycles_remaining == 0:
                        if rs.op == 'LW':
                            # Load: usar vj como endereço
                            result = self.memory.get(rs.vj, 0)
                        else:  # SW
                            # Store: usar vj como endereço, vk como valor
                            self.memory[rs.vj] = rs.vk
                            result = rs.vk
                        rs.result = int(result) if result is not None else 0
                        rs.ready = True

    def _write_result(self):
        """Fase de escrita de resultados"""
        for rs_type, stations in self.reservation_stations.stations.items():
            for rs in stations:
                if rs.busy and rs.ready:
                    self.cdb.broadcast(rs.result, rs.dest)
                    self._update_waiting_stations(rs.dest, rs.result)
                    # Marcar entrada do ROB como pronta para qualquer instrução
                    if rs.dest is not None:
                        self.rob.entries[rs.dest].value = rs.result
                        self.rob.entries[rs.dest].ready = True
                    if rs.dest is not None:
                        rob_entry = self.rob.entries[rs.dest]
                        rob_entry.value = rs.result
                        rob_entry.ready = True
                        rob_entry.state = ROBState.WRITEBACK

                # NÃO LIMPE O rs.busy AQUI! Deixe ele ocupado até a instrução realmente fazer Commit
                    rs.ready = False

    def _commit(self):
        commits_this_cycle = 0
        max_commit_per_cycle = 2  # Pode ajustar conforme sua arquitetura

        while commits_this_cycle < max_commit_per_cycle:
            head_entry = self.rob.entries[self.rob.head]

            if head_entry.state != ROBState.EMPTY and head_entry.ready:
                if head_entry.instruction and head_entry.instruction['type'] == 'BRANCH':
                    self._handle_branch_commit(head_entry)
                else:
                    # Só escreve no registrador se ele ainda está esperando este ROB
                    dest_reg = head_entry.destination
                    if dest_reg and dest_reg in self.registers.tags:
                        if self.registers.tags[dest_reg] == self.rob.head:
                            self.registers.values[dest_reg] = head_entry.value
                            self.registers.tags[dest_reg] = None

                # Libera a estação de reserva correspondente
                for rs_type, stations in self.reservation_stations.stations.items():
                    for rs in stations:
                        if rs.dest == self.rob.head:
                            rs.busy = False
                            rs.op = None
                            rs.vj = None
                            rs.vk = None
                            rs.qj = None
                            rs.qk = None
                            rs.dest = None
                            rs.result = None
                            rs.cycles_remaining = 0
                            rs.ready = False

                # Limpa entrada do ROB
                head_entry.state = ROBState.EMPTY
                head_entry.instruction = None
                head_entry.destination = None
                head_entry.value = None
                head_entry.ready = False

                # Avança o head do ROB
                self.rob.head = (self.rob.head + 1) % len(self.rob.entries)
                self.metrics['completed_instructions'] += 1
                commits_this_cycle += 1
            else:
                break


    def _execute_instruction(self, opcode, vj, vk):
        """Executa uma instrução e retorna o resultado"""
        # Verificar se os operandos são válidos
        if vj is None or vk is None:
            return 0
            
        # Instruções aritméticas básicas
        if opcode == 'ADD':
            return vj + vk
        elif opcode == 'SUB':
            return vj - vk
        elif opcode == 'MUL':
            return vj * vk
        elif opcode == 'DIV':
            return vj // vk if vk != 0 else 0
            
        # Instruções de imediato
        elif opcode == 'ADDI':
            return vj + vk  # vk é o valor imediato
            
        # Instruções de memória
        elif opcode == 'LW':
            return self.memory.get(vj, 0)
        elif opcode == 'SW':
            self.memory[vj] = vk
            return vk
            
        # Instruções de branch
        elif opcode == 'BEQ':
            return 1 if vj == vk else 0
        elif opcode == 'BNE':
            return 1 if vj != vk else 0
            
        return 0

    def _get_rs_type(self, instruction_type):
        """Retorna o tipo de estação de reserva para o tipo de instrução"""
        if instruction_type in ['INT']:
            return 'INT'
        elif instruction_type in ['FP']:
            return 'FP'
        elif instruction_type in ['MEM']:
            return 'MEM'
        else:
            return 'INT'  # Default

    def _find_available_rs(self, rs_type):
        """Encontra uma estação de reserva disponível"""
        for rs in self.reservation_stations.stations[rs_type]:
            if not rs.busy:
                return rs
        return None

    def _get_latency(self, opcode):
        """Retorna a latência de uma instrução"""
        latencies = {
            # Instruções aritméticas básicas
            'ADD': 1, 'SUB': 1, 'MUL': 3, 'DIV': 10,
            
            # Instruções de imediato
            'ADDI': 1,
            
            # Instruções de memória
            'LW': 2, 'SW': 1,
            
            # Instruções de branch
            'BEQ': 1, 'BNE': 1
        }
        return latencies.get(opcode, 1)

    def _update_waiting_stations(self, tag, value):
        """Atualiza estações de reserva que esperam por um resultado"""
        for rs_type, stations in self.reservation_stations.stations.items():
            for rs in stations:
                if rs.busy:
                    if rs.qj == tag:
                        rs.vj = value
                        rs.qj = None
                    if rs.qk == tag:
                        rs.vk = value
                        rs.qk = None

    def _handle_branch_commit(self, rob_entry):
        """Trata o commit de uma instrução de branch"""
        # Para branches, sempre assumir que não tomou o branch (especulação conservadora)
        # Em uma implementação real, isso seria baseado no preditor de branch
        actual_taken = rob_entry.value == 1
        predicted_taken = False  # Assumir que não toma o branch
        
        if actual_taken != predicted_taken:
            # Misprediction - flush pipeline
            self.branch_misprediction = True
            self.flush_needed = True
            self.metrics['bubbles'] += 10  # Penalidade de branch

    def _flush_pipeline(self):
        """Flush do pipeline após misprediction"""
        # Limpar estações de reserva
        for rs_type, stations in self.reservation_stations.stations.items():
            for rs in stations:
                rs.busy = False
                rs.ready = False
        
        # Resetar registradores tags
        for reg in self.registers.tags:
            self.registers.tags[reg] = None

    def _update_metrics(self):
        """Atualiza métricas de desempenho"""
        if self.cycle > 0:
            self.metrics['ipc'] = self.metrics['completed_instructions'] / self.cycle

    def get_state(self):
        """Retorna o estado atual do simulador para a GUI"""
        return {
            'cycle': self.cycle,
            'metrics': self.metrics.copy(),
            'rob': self._get_rob_state(),
            'reservation_stations': self._get_rs_state(),
            'registers': self._get_register_state(),
            'current_instruction': self.current_instruction,
            'total_instructions': len(self.instructions)
        }

    def _get_rob_state(self):
   
        rob_state = []
        for i, entry in enumerate(self.rob.entries):
            if entry.state != ROBState.EMPTY:
                rob_state.append({
                    'index': i,
                    'state': entry.state,
                    'instruction': entry.instruction,
                    'destination': entry.destination,
                    'value': entry.value,
                    'ready': entry.ready
                })
        return rob_state


    def _get_rs_state(self):
        """Retorna o estado das estações de reserva"""
        rs_state = {}
        for rs_type, stations in self.reservation_stations.stations.items():
            rs_state[rs_type] = []
            for i, rs in enumerate(stations):
                if rs.busy:
                    rs_state[rs_type].append({
                        'index': i,
                        'op': rs.op,
                        'vj': rs.vj,
                        'vk': rs.vk,
                        'qj': rs.qj,
                        'qk': rs.qk,
                        'dest': rs.dest,
                        'cycles_remaining': rs.cycles_remaining,
                        'ready': rs.ready
                    })
        return rs_state

    def _get_register_state(self):
        """Retorna o estado dos registradores"""
        reg_state = {}
        for reg_name in self.registers.registers:
            reg_state[reg_name] = {
                'value': self.registers.values[reg_name],
                'tag': self.registers.tags[reg_name]
            }
        return reg_state
