from simulator.components.branch_predictor import OneBitPredictor
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
        self.bp = OneBitPredictor()
        self.committed_instructions = []  # Lista para rastrear instruções commitadas
        self.metrics = {
            'ipc': 0.0,
            'stalls': 0,
            'total_instructions': 0,
            'completed_instructions': 0,
            'bubbles': 0,
            'mispredictions': 0,
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
        self.label_map = {} # Mapeia labels para endereços de PC
        self.flush_rob_entry_index = -1 # Guarda o índice do ROB da instrução de desvio que causou o flush
        self.misprediction_target_pc = -1 # Guarda o PC de destino correto após uma predição errada
        self.last_branch_prediction = None
        self.branch_history = []  # Histórico de branches executados

    def save_state(self):
        # Salva uma cópia profunda do estado atual
        state = {
            'cycle': self.cycle,
            'instructions': copy.deepcopy(self.instructions),
            'current_instruction': self.current_instruction,
            'reservation_stations': copy.deepcopy(self.reservation_stations),
            'rob': copy.deepcopy(self.rob),
            'registers': copy.deepcopy(self.registers),
            'committed_instructions': copy.deepcopy(self.committed_instructions),
            'pc': self.pc,
            'flush_needed': self.flush_needed,
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
            self.committed_instructions = copy.deepcopy(state['committed_instructions'])
            self.pc = state['pc']
            self.flush_needed = state['flush_needed']

    def load_program(self, program_text):
        """Carrega um programa MIPS, mapeando labels primeiro."""
        self.instructions = []
        self.label_map = {}
        self.committed_instructions = []  # Limpar instruções commitadas
        lines = program_text.strip().split('\n')
        
        # Primeiro passo: Mapear todas as labels para seus PCs
        current_pc = 0
        parsed_lines = []
        for line in lines:
            clean_line = line.strip()
            if not clean_line or clean_line.startswith('#'):
                continue
            
            if ':' in clean_line:
                label, rest_of_line = clean_line.split(':', 1)
                self.label_map[label.strip()] = current_pc
                clean_line = rest_of_line.strip()
            
            if clean_line:
                parsed_lines.append(clean_line)
                current_pc += 1

        # Segundo passo: Parsear as instruções
        for pc, line in enumerate(parsed_lines):
            instruction = parse_instruction(line)
            if instruction:
                instruction['pc'] = pc
                # Resolver o alvo do branch para um PC
                if instruction['type'] == 'BRANCH':
                    label = instruction['operands'][2]
                    if label in self.label_map:
                        instruction['target_pc'] = self.label_map[label]
                    else:
                        # Tratar erro de label não encontrada se necessário
                        instruction['target_pc'] = -1 # Indicador de erro
                self.instructions.append(instruction)

        self.metrics['total_instructions'] = len(self.instructions)

    def cycle_step(self):
        self.save_state() 
        if not self._has_work_to_do():
            return False

        if self.flush_needed:
            self._flush_pipeline()
            self.flush_needed = False
            self.cycle += 1
            self._update_metrics()
            return True
        self._commit()
        self._execute()
        self._issue()
        self._write_result()
        

        self._count_bubbles()

        # Atualiza IPC, stalls, etc
        self.cycle += 1
        self._update_metrics()
        return True

    def _has_work_to_do(self):
        """Verifica se ainda há trabalho para fazer"""
        # Se o pipeline foi limpo, pode haver instruções no ROB para cometer
        # mas o PC pode já ter chegado ao fim.
        if self.pc < len(self.instructions):
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
        
        # Não emite novas instruções se um flush estiver pendente
        if self.flush_needed:
            return

        instructions_issued = 0
        max_issue_per_cycle = 2 # Grau de superescalar
        
        while self.pc < len(self.instructions) and instructions_issued < max_issue_per_cycle:
            if self.rob.entries[self.rob.tail].state != 'Empty':
                self.metrics['stalls'] += 1 # Stall por falta de espaço no ROB
                break 

            instruction = self.instructions[self.pc]
            
            rs_type = self._get_rs_type(instruction['type'])
            available_rs = self._find_available_rs(rs_type)
            
            if available_rs:
                rob_entry_idx = self.rob.tail
                rob_entry = self.rob.entries[rob_entry_idx]
                
                # Preencher a entrada do ROB
                rob_entry.state = 'Issued'
                rob_entry.instruction = instruction
                rob_entry.pc = instruction['pc']

                # Lógica de desvio
                is_branch = instruction['type'] == 'BRANCH'
                predicted_taken = False
                if is_branch:
                    predicted_taken = self.bp.predict(instruction['pc'])
                    rob_entry.destination = rob_entry_idx
                    rob_entry.predicted_taken = predicted_taken
                    rob_entry.target_pc = instruction.get('target_pc', -1)
                else:
                    rob_entry.destination = instruction['operands'][0]

                # Renomeação de registradores e captura de operandos
                rs = available_rs
                rs.busy = True
                rs.op = instruction['opcode']
                rs.dest = rob_entry_idx
                
                dest_reg = None
                if not is_branch:
                    dest_reg = instruction['operands'][0]
                    rob_entry.old_tag = self.registers.tags.get(dest_reg)
                
                # Lógica de operandos CORRIGIDA e REFINADA
                op = instruction['opcode']
                ops = instruction['operands']
                src1_reg, src2_reg, immediate = None, None, None

                # Identificar operandos fonte com base no formato da instrução MIPS
                if op in ['ADD', 'SUB', 'MUL', 'DIV']: # R-type: op rd, rs, rt
                    src1_reg, src2_reg = ops[1], ops[2]
                elif op in ['ADDI']: # I-type: op rt, rs, imm
                    src1_reg, immediate = ops[1], int(ops[2])
                elif op in ['LW', 'SW']: # I-type: op rt, imm(rs)
                    # Simplificação do parser: LW/SW rt, rs, imm
                    src1_reg, immediate = ops[1], int(ops[2]) 
                elif op in ['BEQ', 'BNE']: # I-type: op rs, rt, label
                    src1_reg, src2_reg = ops[0], ops[1]
                
                # Preencher Vj e Qj (Primeiro operando fonte)
                if src1_reg:
                    tag = self.registers.tags.get(src1_reg)
                    if tag is None:
                        rs.vj = self.registers.values.get(src1_reg, 0)
                        rs.qj = None
                    else:
                        rob_dep_entry = self.rob.entries[tag]
                        if rob_dep_entry.ready:
                            rs.vj = rob_dep_entry.value
                            rs.qj = None
                        else:
                            rs.qj = tag
                
                # Preencher Vk e Qk (Segundo operando fonte ou imediato)
                if src2_reg:
                    tag = self.registers.tags.get(src2_reg)
                    if tag is None:
                        rs.vk = self.registers.values.get(src2_reg, 0)
                        rs.qk = None
                    else:
                        rob_dep_entry = self.rob.entries[tag]
                        if rob_dep_entry.ready:
                            rs.vk = rob_dep_entry.value
                            rs.qk = None
                        else:
                            rs.qk = tag
                elif immediate is not None:
                    # Para ADDI, LW, o segundo valor vem do imediato
                    rs.vk = immediate
                    rs.qk = None
                
                rs.cycles_remaining = self._get_latency(instruction['opcode'])
                
                if not is_branch and dest_reg:
                    self.registers.tags[dest_reg] = rob_entry_idx
                
                self.rob.tail = (self.rob.tail + 1) % len(self.rob.entries)
                instructions_issued += 1

                # Atualizar PC para a próxima instrução (especulativamente)
                if is_branch and predicted_taken:
                    self.pc = rob_entry.target_pc
                else:
                    self.pc += 1
            else:
                self.metrics['stalls'] += 1 # Stall por falta de ER
                break # Não há estação de reserva, parar de emitir

    def _execute(self):
        """Fase de execução das instruções prontas de forma superescalar."""
        for rs in self.reservation_stations.stations['INT'] + self.reservation_stations.stations['FP'] + self.reservation_stations.stations['MEM']:
            # Condição para executar: pronta e não já alocada a uma unidade
            if rs.busy and rs.qj is None and rs.qk is None:
                is_already_processing = any(unit['current_instruction'] is rs for unit in self.execution_units.values())
                
                if not is_already_processing:
                    # Encontra uma unidade de execução livre do tipo correto
                    unit_type_needed = self._get_execution_unit_type(rs.op)
                    for unit_name, unit_state in self.execution_units.items():
                        if unit_name.startswith(unit_type_needed) and not unit_state['busy']:
                            unit_state['busy'] = True
                            unit_state['current_instruction'] = rs
                            break # Alocou, passa para a próxima ER

        # Decrementar contadores e finalizar execução para TODAS as unidades em paralelo
        for unit, state in self.execution_units.items():
            if state['busy'] and state['current_instruction'] is not None:
                rs = state['current_instruction']
                
                if rs.cycles_remaining > 0:
                    rs.cycles_remaining -= 1
                
                if rs.cycles_remaining == 0:
                    rob_entry = self.rob.entries[rs.dest]
                    result = self._execute_instruction(rs.op, rs.vj, rs.vk)
                    
                    if rob_entry.instruction and rob_entry.instruction['type'] == 'BRANCH':
                        # Salve a predição feita ANTES do update (o que o preditor achava)
                        predicted = self.bp.predict(rob_entry.pc)
                        actual_taken = bool(result)
                        rob_entry.actual_outcome = actual_taken

                        # Salve no histórico
                        self.branch_history.append({
                            'pc': rob_entry.pc,
                            'predicted': predicted,
                            'actual': actual_taken,
                            'opcode': rob_entry.instruction['opcode'],
                            'operands': rob_entry.instruction['operands']
                        })

                        self.last_branch_prediction = {
                            'pc': rob_entry.pc,
                            'predicted_taken': predicted,
                            'opcode': rob_entry.instruction['opcode'],
                            'operands': rob_entry.instruction['operands']
                        }

                        self.bp.update(rob_entry.pc, actual_taken)

                        if rob_entry.predicted_taken != actual_taken:
                            self.metrics['mispredictions'] += 1
                            self.flush_needed = True
                            self.flush_rob_entry_index = rs.dest
                            if actual_taken:
                                self.misprediction_target_pc = rob_entry.target_pc
                            else:
                                self.misprediction_target_pc = rob_entry.pc + 1
                    
                    rs.result = result
                    rs.ready = True
                    
                    # Libera a unidade de execução para o próximo ciclo
                    state['busy'] = False
                    state['current_instruction'] = None

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
                    # Não libere a estação aqui. Apenas marque o ROB como pronto.
                    self.cdb.broadcast(rs.result, rs.dest)
                    self._update_waiting_stations(rs.dest, rs.result)
                    
                    if rs.dest is not None:
                        rob_entry = self.rob.entries[rs.dest]
                        rob_entry.value = rs.result
                        rob_entry.ready = True
                        rob_entry.state = 'Writeback'
                    
                    # A estação permanece ocupada até o commit
                    rs.ready = False # Previne re-broadcast no próximo ciclo

    def _commit(self):
        """Confirma até 4 instruções por ciclo."""
        commit_count = 0
        max_commit_per_cycle = 4

        while commit_count < max_commit_per_cycle:
            rob_entry = self.rob.entries[self.rob.head]

            if rob_entry.state == 'Empty' or not rob_entry.ready:
                break

            if rob_entry.ready and rob_entry.instruction:
                # Adicionar instrução à lista de commitadas
                committed_inst = {
                    'instruction': rob_entry.instruction,
                    'cycle_committed': self.cycle,
                    'rob_index': self.rob.head,
                    'destination': rob_entry.destination,
                    'value': rob_entry.value
                }
                self.committed_instructions.append(committed_inst)
                
                if rob_entry.instruction['type'] != 'BRANCH':
                    dest_reg = rob_entry.destination
                    if isinstance(dest_reg, str) and self.registers.tags.get(dest_reg) == self.rob.head:
                        self.registers.values[dest_reg] = rob_entry.value
                        self.registers.tags[dest_reg] = None
                
                # Para SW, atualiza a memória aqui
                if rob_entry.instruction['opcode'] == 'SW':
                    addr = rob_entry.value # Endereço calculado na fase de execução
                    val_reg = rob_entry.instruction['operands'][0]
                    # O valor a ser escrito vem do registrador de origem, que já deve estar pronto no ROB
                    # Esta lógica pode precisar de refinamento, dependendo de como os valores dos operandos de SW são tratados
                    # No momento, vamos assumir que o valor está em `vj` da RS, mas isso não é passado para o ROB.
                    # Por simplicidade, vamos pular a atualização real da memória por enquanto.
                    pass

                # Agora, libere a estação de reserva associada a esta entrada do ROB
                for stations in self.reservation_stations.stations.values():
                    for rs in stations:
                        if rs.dest == self.rob.head:
                            rs.reset() # Reseta a estação para o estado inicial
                            break
                
                self.metrics['completed_instructions'] += 1
                rob_entry.__init__() # Reseta a entrada do ROB para 'Empty'
                self.rob.head = (self.rob.head + 1) % len(self.rob.entries)
                commit_count += 1
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

    def _flush_pipeline(self):
        """Limpa o pipeline após uma predição de desvio incorreta."""
        # 1. Atualiza o PC para o caminho correto
        self.pc = self.misprediction_target_pc

        # 2. Limpa as instruções especulativas do ROB
        # O tail do ROB aponta para a próxima posição livre. As instruções
        # especulativas estão entre o desvio e o tail.
        
        current_idx = (self.flush_rob_entry_index + 1) % len(self.rob.entries)
        while current_idx != self.rob.tail:
            entry_to_flush = self.rob.entries[current_idx]
            if entry_to_flush.state != 'Empty':
                # Restaura o tag do registrador de destino
                if entry_to_flush.instruction and entry_to_flush.instruction['type'] != 'BRANCH':
                    dest_reg = entry_to_flush.destination
                    if dest_reg and self.registers.tags.get(dest_reg) == current_idx:
                         self.registers.tags[dest_reg] = entry_to_flush.old_tag

                # Limpa a entrada
                entry_to_flush.__init__() # Reseta para o estado inicial

            current_idx = (current_idx + 1) % len(self.rob.entries)
        
        # 3. Reposiciona o tail do ROB para depois do branch
        self.rob.tail = (self.flush_rob_entry_index + 1) % len(self.rob.entries)

        # 4. Limpa todas as estações de reserva
        self.reservation_stations.reset()
        
        # 5. Limpa os flags de controle
        self.flush_rob_entry_index = -1
        self.misprediction_target_pc = -1
        self.flush_needed = False

    def _get_execution_unit_type(self, opcode):
        """Mapeia um opcode para o TIPO de unidade de execução (genérico)."""
        if opcode in ['ADD', 'SUB', 'ADDI']:
            return 'INT_ALU'
        elif opcode in ['MUL']:
            return 'FP_MUL'
        elif opcode in ['DIV']:
            return 'FP_DIV'
        elif opcode == 'LW':
            return 'MEM_LOAD'
        elif opcode == 'SW':
            return 'MEM_STORE'
        elif opcode in ['BNE', 'BEQ']:
            return 'BRANCH'
        return 'INT_ALU' # Padrão

    def _update_metrics(self):
        """Atualiza as métricas de desempenho."""
        if self.cycle > 0:
            self.metrics['ipc'] = self.metrics['completed_instructions'] / self.cycle
        else:
            self.metrics['ipc'] = 0.0

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
        """Retorna o estado do ROB para a GUI"""
        rob_state = []
        for i, entry in enumerate(self.rob.entries):
            if entry.state != 'Empty':
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
        """Retorna o estado dos registradores para a GUI"""
        register_state = {}
        for reg_name in self.registers.values.keys():
            register_state[reg_name] = {
                'value': self.registers.values[reg_name],
                'tag': self.registers.tags[reg_name]
            }
        return register_state

    def _get_committed_instructions_state(self):
        """Retorna o estado das instruções commitadas para a GUI"""
        return self.committed_instructions.copy()

    def get_last_branch_prediction(self):
        """Retorna a última predição de desvio executada (ou None se não houver)."""
        return self.last_branch_prediction

    def get_branch_history(self):
        """Retorna o histórico de branches executados para a GUI."""
        return self.branch_history
