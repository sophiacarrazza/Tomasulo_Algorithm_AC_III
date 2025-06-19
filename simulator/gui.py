import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from simulator.core import TomasuloCore

class TomasuloGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Simulador do Algoritmo de Tomasulo")
        self.geometry("1400x900")
        
        self.core = TomasuloCore()
        self.is_running = False
        
        self._create_widgets()
        self._load_sample_program()
        
    def _create_widgets(self):
        """Cria todos os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame superior - Controles e Programa
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame esquerdo - Controles e Programa
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Controles
        self._create_control_panel(left_frame)
        
        # Programa
        self._create_program_panel(left_frame)
        
        # Frame direito - Métricas
        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Métricas
        self._create_metrics_panel(right_frame)
        
        # Frame inferior - Componentes do Pipeline
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook para organizar os componentes
        self.notebook = ttk.Notebook(bottom_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # ROB
        self._create_rob_panel()
        
        # Estações de Reserva
        self._create_rs_panel()
        
        # Registradores
        self._create_register_panel()
        
        # Memória
        self._create_memory_panel()

    def _create_control_panel(self, parent):
        """Cria o painel de controles"""
        control_frame = ttk.LabelFrame(parent, text="Controles")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botões
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Step", command=self.step).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Run", command=self.run_simulation).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Stop", command=self.stop).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Reset", command=self.reset).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Load Program", command=self.load_program).pack(side=tk.LEFT)
        
        # Informações do ciclo
        info_frame = ttk.Frame(control_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(info_frame, text="Ciclo:").pack(side=tk.LEFT)
        self.cycle_label = ttk.Label(info_frame, text="0")
        self.cycle_label.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(info_frame, text="Instrução Atual:").pack(side=tk.LEFT)
        self.current_inst_label = ttk.Label(info_frame, text="0")
        self.current_inst_label.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(info_frame, text="Total:").pack(side=tk.LEFT)
        self.total_inst_label = ttk.Label(info_frame, text="0")
        self.total_inst_label.pack(side=tk.LEFT, padx=5)

    def _create_program_panel(self, parent):
        """Cria o painel do programa"""
        program_frame = ttk.LabelFrame(parent, text="Programa MIPS")
        program_frame.pack(fill=tk.BOTH, expand=True)
        
        # Área de texto para o programa
        self.program_text = scrolledtext.ScrolledText(program_frame, height=10, width=50)
        self.program_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_metrics_panel(self, parent):
        """Cria o painel de métricas"""
        metrics_frame = ttk.LabelFrame(parent, text="Métricas de Desempenho")
        metrics_frame.pack(fill=tk.X, padx=(10, 0))
        
        # Métricas
        self.metrics_labels = {}
        metrics = [
            ('ipc', 'IPC:'),
            ('completed_instructions', 'Instruções Completadas:'),
            ('stalls', 'Stalls:'),
            ('bubbles', 'Bubbles:'),
            ('total_instructions', 'Total de Instruções:')
        ]
        
        for key, label in metrics:
            frame = ttk.Frame(metrics_frame)
            frame.pack(fill=tk.X, padx=10, pady=2)
            
            ttk.Label(frame, text=label).pack(side=tk.LEFT)
            self.metrics_labels[key] = ttk.Label(frame, text="0")
            self.metrics_labels[key].pack(side=tk.RIGHT)

    def _create_rob_panel(self):
        """Cria o painel do ROB"""
        rob_frame = ttk.Frame(self.notebook)
        self.notebook.add(rob_frame, text="Reorder Buffer (ROB)")
        
        # Treeview para o ROB
        columns = ('Index', 'State', 'Instruction', 'Destination', 'Value', 'Ready')
        self.rob_tree = ttk.Treeview(rob_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.rob_tree.heading(col, text=col)
            self.rob_tree.column(col, width=100)
        
        # Scrollbar
        rob_scrollbar = ttk.Scrollbar(rob_frame, orient=tk.VERTICAL, command=self.rob_tree.yview)
        self.rob_tree.configure(yscrollcommand=rob_scrollbar.set)
        
        self.rob_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rob_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_rs_panel(self):
        """Cria o painel das estações de reserva"""
        rs_frame = ttk.Frame(self.notebook)
        self.notebook.add(rs_frame, text="Estações de Reserva")
        
        # Notebook para diferentes tipos de RS
        rs_notebook = ttk.Notebook(rs_frame)
        rs_notebook.pack(fill=tk.BOTH, expand=True)
        
        # RS Integer
        int_frame = ttk.Frame(rs_notebook)
        rs_notebook.add(int_frame, text="Integer")
        self._create_rs_tree(int_frame, 'INT')
        
        # RS FP
        fp_frame = ttk.Frame(rs_notebook)
        rs_notebook.add(fp_frame, text="Floating Point")
        self._create_rs_tree(fp_frame, 'FP')

    def _create_rs_tree(self, parent, rs_type):
        """Cria uma treeview para um tipo específico de estação de reserva"""
        columns = ('Index', 'Busy', 'Op', 'Vj', 'Vk', 'Qj', 'Qk', 'Dest', 'Cycles', 'Ready')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        setattr(self, f'{rs_type.lower()}_rs_tree', tree)

    def _create_register_panel(self):
        """Cria o painel dos registradores"""
        reg_frame = ttk.Frame(self.notebook)
        self.notebook.add(reg_frame, text="Registradores")
        
        # Treeview para registradores
        columns = ('Register', 'Value', 'Tag')
        self.reg_tree = ttk.Treeview(reg_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.reg_tree.heading(col, text=col)
            self.reg_tree.column(col, width=100)
        
        # Scrollbar
        reg_scrollbar = ttk.Scrollbar(reg_frame, orient=tk.VERTICAL, command=self.reg_tree.yview)
        self.reg_tree.configure(yscrollcommand=reg_scrollbar.set)
        
        self.reg_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        reg_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_memory_panel(self):
        """Cria o painel da memória"""
        mem_frame = ttk.Frame(self.notebook)
        self.notebook.add(mem_frame, text="Memória")
        
        # Treeview para memória
        columns = ('Address', 'Value')
        self.mem_tree = ttk.Treeview(mem_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.mem_tree.heading(col, text=col)
            self.mem_tree.column(col, width=100)
        
        # Scrollbar
        mem_scrollbar = ttk.Scrollbar(mem_frame, orient=tk.VERTICAL, command=self.mem_tree.yview)
        self.mem_tree.configure(yscrollcommand=mem_scrollbar.set)
        
        self.mem_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        mem_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _load_sample_program(self):
        """Carrega um programa de exemplo"""
        sample_program = """# Programa de exemplo para demonstrar o algoritmo de Tomasulo
ADD R1, R2, R3
MUL R4, R1, R5
ADD R6, R4, R7
BEQ R1, R2, 8
LW R8, 100
SW R9, 200
SUB R10, R8, R9
DIV R11, R10, R1"""
        
        self.program_text.delete(1.0, tk.END)
        self.program_text.insert(1.0, sample_program)
        self.load_program_from_text()

    def step(self):
        """Executa um ciclo da simulação"""
        if self.core.current_instruction < len(self.core.instructions) or self._has_pending_instructions():
            self.core.cycle_step()
            self.update_gui()
        else:
            messagebox.showinfo("Simulação", "Todas as instruções foram executadas!")

    def run_simulation(self):
        """Executa a simulação continuamente"""
        if not self.is_running:
            self.is_running = True
            self._run_continuous()

    def _run_continuous(self):
        """Execução contínua da simulação"""
        if self.is_running and (self.core.current_instruction < len(self.core.instructions) or self._has_pending_instructions()):
            self.step()
            self.after(500, self._run_continuous)  # 500ms entre ciclos
        else:
            self.is_running = False
            if self.core.current_instruction >= len(self.core.instructions) and not self._has_pending_instructions():
                messagebox.showinfo("Simulação", "Todas as instruções foram executadas!")

    def stop(self):
        """Para a simulação"""
        self.is_running = False

    def reset(self):
        """Reseta a simulação"""
        self.stop()
        self.core = TomasuloCore()
        self.load_program_from_text()
        self.update_gui()

    def load_program(self):
        """Carrega um programa do arquivo"""
        # Implementação simplificada - carrega do texto atual
        self.load_program_from_text()

    def load_program_from_text(self):
        """Carrega o programa do texto atual"""
        program_text = self.program_text.get(1.0, tk.END)
        self.core.load_program(program_text)
        self.update_gui()

    def _has_pending_instructions(self):
        """Verifica se há instruções pendentes no pipeline"""
        # Verificar ROB
        for entry in self.core.rob.entries:
            if entry.state != 'Empty':
                return True
        
        # Verificar estações de reserva
        for rs_type, stations in self.core.reservation_stations.stations.items():
            for rs in stations:
                if rs.busy:
                    return True
        
        return False

    def update_gui(self):
        """Atualiza todos os componentes da GUI"""
        state = self.core.get_state()
        
        # Atualizar informações básicas
        self.cycle_label.config(text=str(state['cycle']))
        self.current_inst_label.config(text=str(state['current_instruction']))
        self.total_inst_label.config(text=str(state['total_instructions']))
        
        # Atualizar métricas
        for key, label in self.metrics_labels.items():
            value = state['metrics'].get(key, 0)
            if key == 'ipc':
                label.config(text=f"{value:.3f}")
            else:
                label.config(text=str(value))
        
        # Atualizar ROB
        self._update_rob_tree(state['rob'])
        
        # Atualizar estações de reserva
        self._update_rs_trees(state['reservation_stations'])
        
        # Atualizar registradores
        self._update_register_tree(state['registers'])
        
        # Atualizar memória
        self._update_memory_tree()

    def _update_rob_tree(self, rob_state):
        """Atualiza a treeview do ROB"""
        self.rob_tree.delete(*self.rob_tree.get_children())
        
        for entry in rob_state:
            instruction_str = f"{entry['instruction']['opcode']} {' '.join(entry['instruction']['operands'])}" if entry['instruction'] else ""
            self.rob_tree.insert('', 'end', values=(
                entry['index'],
                entry['state'],
                instruction_str,
                entry['destination'],
                entry['value'],
                "Sim" if entry['ready'] else "Não"
            ))

    def _update_rs_trees(self, rs_state):
        """Atualiza as treeviews das estações de reserva"""
        for rs_type in ['INT', 'FP']:
            tree = getattr(self, f'{rs_type.lower()}_rs_tree')
            tree.delete(*tree.get_children())
            
            if rs_type in rs_state:
                for entry in rs_state[rs_type]:
                    tree.insert('', 'end', values=(
                        entry['index'],
                        "Sim" if entry.get('busy', False) else "Não",
                        entry['op'],
                        entry['vj'],
                        entry['vk'],
                        entry['qj'],
                        entry['qk'],
                        entry['dest'],
                        entry['cycles_remaining'],
                        "Sim" if entry['ready'] else "Não"
                    ))

    def _update_register_tree(self, register_state):
        """Atualiza a treeview dos registradores"""
        self.reg_tree.delete(*self.reg_tree.get_children())
        
        for reg_name, reg_data in register_state.items():
            self.reg_tree.insert('', 'end', values=(
                reg_name,
                reg_data['value'],
                reg_data['tag'] if reg_data['tag'] is not None else ""
            ))

    def _update_memory_tree(self):
        """Atualiza a treeview da memória"""
        self.mem_tree.delete(*self.mem_tree.get_children())
        
        for address, value in self.core.memory.items():
            self.mem_tree.insert('', 'end', values=(address, value))

    def run(self):
        """Inicia a aplicação"""
        self.mainloop()
