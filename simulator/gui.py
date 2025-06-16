import tkinter as tk
from tkinter import ttk
from simulator.core import TomasuloCore

class TomasuloGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.core = TomasuloCore() 
        self._create_panels()

    def step(self):
        """Executa um ciclo da simulação"""
        self.core.cycle_step()
        self.update_gui()  # Atualiza a interface

    def update_gui(self):
        # Implementação básica para atualizar os componentes gráficos
        self.register_tree.delete(*self.register_tree.get_children())
        for reg in self.core.registers:
            self.register_tree.insert('', 'end', 
                values=(reg.name, reg.value, reg.tag))

    def _create_panels(self):
        # Painel de Controle
        self.control_frame = ttk.Frame(self.root)
        ttk.Button(self.control_frame, text="Step", command=self.step).pack(side=tk.LEFT)
        
        # Painel de Registradores
        self.register_frame = ttk.LabelFrame(self.root, text="Registradores")
        self._create_register_table()
        
        # Layout
        self.control_frame.pack(fill=tk.X)
        self.register_frame.pack(fill=tk.BOTH, expand=True)
    
    def _create_register_table(self):
        columns = ('Reg', 'Value', 'Tag')
        self.register_tree = ttk.Treeview(self.register_frame, columns=columns, show='headings')
        for col in columns:
            self.register_tree.heading(col, text=col)
        self.register_tree.pack(fill=tk.BOTH, expand=True)
