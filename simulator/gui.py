import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from simulator.core import TomasuloCore

class TomasuloGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador do Algoritmo de Tomasulo")
        self.geometry("1400x900")
        self.configure(bg="#f7f4fa")
        self.style = ttk.Style(self)
        self._set_modern_theme()
        self.core = TomasuloCore()
        self.is_running = False
        self._create_widgets()
        #self._load_sample_program()

    def _set_modern_theme(self):
        # Tons de roxo
        purple_main = "#7c3aed"  # Roxo principal
        purple_dark = "#5b21b6"  # Roxo escuro
        purple_light = "#ede9fe" # Fundo claro
        purple_bg = "#f7f4fa"    # Fundo geral
        self.style.theme_use('clam')
        self.style.configure('TFrame', background=purple_bg)
        self.style.configure('TLabel', background=purple_bg, font=("Segoe UI", 12))
        self.style.configure('TButton', font=("Segoe UI", 12, "bold"), padding=8, background=purple_main, foreground="#fff", borderwidth=0)
        self.style.map('TButton', background=[('active', purple_dark)])
        self.style.configure('TLabelframe', background=purple_light, font=("Segoe UI", 13, "bold"), borderwidth=2, relief="ridge")
        self.style.configure('TLabelframe.Label', font=("Segoe UI", 14, "bold"), background=purple_main, foreground="#fff")
        self.style.configure('Treeview', font=("Consolas", 11), rowheight=28, fieldbackground="#fff")
        self.style.configure('Treeview.Heading', font=("Segoe UI", 12, "bold"), background=purple_main, foreground="#fff")

    def _create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 12))
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._create_control_panel(left_frame)
        self._create_program_panel(left_frame)
        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self._create_metrics_panel(right_frame)
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        self.notebook = ttk.Notebook(bottom_frame, style='TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self._create_rob_panel()
        self._create_rs_panel()
        self._create_register_panel()
       

    def _create_control_panel(self, parent):
        control_frame = ttk.Labelframe(parent, text="Controles", padding=12)
        control_frame.pack(fill=tk.X, pady=(0, 12))
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=8, pady=8)
        ttk.Button(button_frame, text="⏭ Step", command=self.step, style='TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(button_frame, text="▶ Run", command=self.run_simulation, style='TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(button_frame, text="🔄 Reset", command=self.reset, style='TButton').pack(side=tk.LEFT, padx=(0, 8))
        
        info_frame = ttk.Frame(control_frame)
        info_frame.pack(fill=tk.X, padx=8, pady=(8, 0))
        ttk.Label(info_frame, text="Ciclo:", font=("Segoe UI", 13, "bold"), background="#ede9fe").pack(side=tk.LEFT)
        self.cycle_label = ttk.Label(info_frame, text="0", font=("Segoe UI", 13, "bold"), background="#ede9fe", foreground="#7c3aed")
        self.cycle_label.pack(side=tk.LEFT, padx=(5, 24))
        ttk.Label(info_frame, text="Instrução Atual:", font=("Segoe UI", 13, "bold"), background="#ede9fe").pack(side=tk.LEFT)
        self.current_inst_label = ttk.Label(info_frame, text="0", font=("Segoe UI", 13, "bold"), background="#ede9fe", foreground="#7c3aed")
        self.current_inst_label.pack(side=tk.LEFT, padx=(5, 24))
        ttk.Label(info_frame, text="Total:", font=("Segoe UI", 13, "bold"), background="#ede9fe").pack(side=tk.LEFT)
        self.total_inst_label = ttk.Label(info_frame, text="0", font=("Segoe UI", 13, "bold"), background="#ede9fe", foreground="#7c3aed")
        self.total_inst_label.pack(side=tk.LEFT, padx=5)
        self.back_button = ttk.Button(parent, text="⏪ Voltar", command=self.step_back)
        self.back_button.pack(side="left", padx=5, pady=5)

    def step_back(self):
        self.core.restore_state()
        self.update_gui()

    def _create_program_panel(self, parent):
        program_frame = ttk.Labelframe(parent, text="Programa MIPS", padding=12)
        program_frame.pack(fill=tk.BOTH, expand=True)
        self.program_text = scrolledtext.ScrolledText(program_frame, height=10, width=50, font=("Consolas", 13), bg="#f7f4fa", fg="#222", insertbackground="#7c3aed", borderwidth=2, relief="groove")
        self.program_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def _create_metrics_panel(self, parent):
        metrics_frame = ttk.Labelframe(parent, text="Métricas de Desempenho", padding=12)
        metrics_frame.pack(fill=tk.X, padx=(8, 0))
        self.metrics_labels = {}
        metrics = [
            ('ipc', 'IPC:'),
            ('completed_instructions', 'Instruções Completadas:'),
            ('bubbles', 'Bubbles:'),
            ('total_instructions', 'Total de Instruções:')
        ]
        for key, label in metrics:
            frame = ttk.Frame(metrics_frame)
            frame.pack(fill=tk.X, padx=8, pady=4)
            ttk.Label(frame, text=label, font=("Segoe UI", 12, "bold"), foreground="#7c3aed").pack(side=tk.LEFT)
            self.metrics_labels[key] = ttk.Label(frame, text="0", font=("Segoe UI", 12, "bold"), foreground="#222")
            self.metrics_labels[key].pack(side=tk.RIGHT)

    def _create_rob_panel(self):
        rob_frame = ttk.Frame(self.notebook)
        self.notebook.add(rob_frame, text="Reorder Buffer (ROB)")
        columns = ('Index', 'State', 'Instruction', 'Destination', 'Value', 'Ready')
        self.rob_tree = ttk.Treeview(rob_frame, columns=columns, show='headings', height=10, style='Treeview')
        for col in columns:
            self.rob_tree.heading(col, text=col)
            self.rob_tree.column(col, width=120, anchor=tk.CENTER)
        rob_scrollbar = ttk.Scrollbar(rob_frame, orient=tk.VERTICAL, command=self.rob_tree.yview)
        self.rob_tree.configure(yscrollcommand=rob_scrollbar.set)
        self.rob_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)
        rob_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_rs_panel(self):
        rs_frame = ttk.Frame(self.notebook)
        self.notebook.add(rs_frame, text="Estações de Reserva")
        rs_notebook = ttk.Notebook(rs_frame)
        rs_notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        int_frame = ttk.Frame(rs_notebook)
        rs_notebook.add(int_frame, text="Integer")
        self._create_rs_tree(int_frame, 'INT')
        fp_frame = ttk.Frame(rs_notebook)

        self._create_rs_tree(fp_frame, 'FP')

    def _create_rs_tree(self, parent, rs_type):
        columns = ('Index', 'Busy', 'Op', 'Vj', 'Vk', 'Qj', 'Qk', 'Dest', 'Cycles', 'Ready')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=8, style='Treeview')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=90, anchor=tk.CENTER)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        setattr(self, f'{rs_type.lower()}_rs_tree', tree)

    def _create_register_panel(self):
        reg_frame = ttk.Frame(self.notebook)
        self.notebook.add(reg_frame, text="Registradores")
        columns = ('Register', 'Value', 'Tag')
        self.reg_tree = ttk.Treeview(reg_frame, columns=columns, show='headings', height=15, style='Treeview')
        for col in columns:
            self.reg_tree.heading(col, text=col)
            self.reg_tree.column(col, width=110, anchor=tk.CENTER)
        reg_scrollbar = ttk.Scrollbar(reg_frame, orient=tk.VERTICAL, command=self.reg_tree.yview)
        self.reg_tree.configure(yscrollcommand=reg_scrollbar.set)
        self.reg_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)
        reg_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Painel de edição de registrador
        edit_frame = ttk.Labelframe(reg_frame, text="Editar Registrador", padding=8)
        edit_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=8, pady=8)
        ttk.Label(edit_frame, text="Registrador:").pack(anchor=tk.W)
        self.reg_edit_combo = ttk.Combobox(edit_frame, values=[f"R{i}" for i in range(32)], state="readonly")
        self.reg_edit_combo.pack(fill=tk.X, pady=2)
        ttk.Label(edit_frame, text="Novo valor:").pack(anchor=tk.W, pady=(8,0))
        self.reg_edit_value = tk.Entry(edit_frame)
        self.reg_edit_value.pack(fill=tk.X, pady=2)
        ttk.Button(edit_frame, text="Atualizar", command=self._update_register_value, style='TButton').pack(pady=8, fill=tk.X)

    

    def _load_sample_program(self):
        sample_program = """# Programa de exemplo para demonstrar o algoritmo de Tomasulo
# Instruções básicas
ADD R1, R2, R3
MUL R4, R1, R5

# Instruções de imediato
ADDI R6, R4, 10
SUB R7, R6, R5

# Instruções de memória
LW R8, 100
SW R7, 200

# Instruções de branch
BEQ R1, R2, 8
BNE R3, R4, 12

# Mais operações aritméticas
DIV R9, R8, R1
ADD R10, R9, R6"""
        self.program_text.delete(1.0, tk.END)
        self.program_text.insert(1.0, sample_program)
        self.load_program_from_text()

    def step(self):
        """Executa um ciclo da simulação"""
        if self.core.cycle_step():
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
        if self.is_running:
            if self.core.cycle_step():
                self.update_gui()
                self.after(400, self._run_continuous)  # 400ms entre ciclos
            else:
                self.is_running = False
                messagebox.showinfo("Simulação", "Todas as instruções foram executadas!")

    def stop(self):
        self.is_running = False

    def reset(self):
        self.stop()
        self.core = TomasuloCore()
        self.load_program_from_text()
        self.update_gui()

    def load_program(self):
        self.load_program_from_text()

    def load_program_from_text(self):
        program_text = self.program_text.get(1.0, tk.END)
        self.core.load_program(program_text)
        self.update_gui()

    def _has_pending_instructions(self):
        """Verifica se há instruções pendentes no pipeline"""
        return self.core._has_work_to_do()

    def update_gui(self):
        state = self.core.get_state()
        # Realce visual para ciclo e instrução atual
        self.cycle_label.config(text=str(state['cycle']), foreground="#7c3aed")
        self.current_inst_label.config(text=str(state['current_instruction']), foreground="#7c3aed")
        self.total_inst_label.config(text=str(state['total_instructions']), foreground="#7c3aed")
        for key, label in self.metrics_labels.items():
            value = state['metrics'].get(key, 0)
            if key == 'ipc':
                label.config(text=f"{value:.3f}")
            else:
                label.config(text=str(value))
        self._update_rob_tree(state['rob'])
        self._update_rs_trees(state['reservation_stations'])
        self._update_register_tree(state['registers'])
        self._update_memory_tree()

    def _update_rob_tree(self, rob_state):
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
        self.reg_tree.delete(*self.reg_tree.get_children())
        for reg_name, reg_data in register_state.items():
            self.reg_tree.insert('', 'end', values=(
                reg_name,
                reg_data['value'],
                reg_data['tag'] if reg_data['tag'] is not None else ""
            ))

    def _update_memory_tree(self):
        self.mem_tree.delete(*self.mem_tree.get_children())
        for address, value in self.core.memory.items():
            self.mem_tree.insert('', 'end', values=(address, value))

    def _update_register_value(self):
        reg = self.reg_edit_combo.get()
        try:
            value = int(self.reg_edit_value.get())
        except Exception:
            messagebox.showerror("Erro", "Digite um valor inteiro válido!")
            return
        if reg in self.core.registers.values:
            self.core.registers.values[reg] = value
            self.update_gui()
        else:
            messagebox.showerror("Erro", f"Registrador {reg} não existe!")

    def run(self):
        self.mainloop()
