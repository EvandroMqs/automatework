import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog, scrolledtext
import customtkinter as ctk
import requests
import os
import shutil
import fitz  # PyMuPDF para leitura de PDFs
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import re
import configparser

# URL da API hospedada no Render
API_URL = 'https://automatework.onrender.com'

documents_path = os.path.expanduser('~/Documents/AutomateWork')
settings_file = os.path.join(documents_path, 'settings.ini')

def save_settings(settings):
    config = configparser.ConfigParser()
    config['Settings'] = settings
    os.makedirs(documents_path, exist_ok=True)
    with open(settings_file, 'w') as configfile:
        config.write(configfile)

def load_settings():
    config = configparser.ConfigParser()
    if os.path.exists(settings_file) and config.read(settings_file):
        return dict(config['Settings'])
    return {
        'source': '',
        'destination': '',
        'subfolder_name': 'TI',
        'file_name': '01 - Termo de Desconto',
        'use_alternative_dir': 'False',
        'alternative_dir': '',
        'include_name_in_alt': 'False',
        'name_pattern_start': 'Eu,',
        'name_pattern_end': ', portador do CPF',
        'use_filename_as_name': 'False'
    }

def ensure_keys(settings):
    defaults = {
        'name_pattern_start': 'Eu,',
        'name_pattern_end': ', portador do CPF',
        'use_filename_as_name': 'False'
    }
    for key, value in defaults.items():
        if key not in settings:
            settings[key] = value

class PDFHandler(FileSystemEventHandler):
    def __init__(self, update_status, settings):
        self.update_status = update_status
        self.settings = settings

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.pdf'):
            return
        threading.Thread(target=self.process_pdf, args=(event.src_path,)).start()

    def process_pdf(self, path):
        try:
            if self.settings['use_filename_as_name'] == 'True':
                nome_colaborador = os.path.splitext(os.path.basename(path))[0]
            else:
                doc = fitz.open(path)
                page = doc[0]
                text = page.get_text()
                pattern = re.escape(self.settings['name_pattern_start']) + r"\s(.*?)" + re.escape(self.settings['name_pattern_end'])
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    nome_colaborador = match.group(1).strip()
                else:
                    self.update_status("Nome do colaborador não encontrado.")
                    doc.close()
                    return
                doc.close()
            self.organize_files(path, nome_colaborador)
            self.update_status(f"Arquivo '{os.path.basename(path)}' processado e movido.")
        except Exception as e:
            self.update_status(f"Erro ao processar arquivo: {str(e)}")

    def organize_files(self, file_path, name):
        primary_path = os.path.join(self.settings['destination'], name, self.settings['subfolder_name'])
        if not os.path.exists(primary_path):
            os.makedirs(primary_path)
        primary_file_name = self.settings['file_name'] + '.pdf'
        shutil.move(file_path, os.path.join(primary_path, primary_file_name))

        if self.settings['use_alternative_dir'] == 'True':
            alt_file_name = (name + ' - ' + self.settings['file_name'] if self.settings['include_name_in_alt'] == 'True' else self.settings['file_name']) + '.pdf'
            alt_file_path = os.path.join(self.settings['alternative_dir'], alt_file_name)
            shutil.copy(os.path.join(primary_path, primary_file_name), alt_file_path)
            self.update_status(f"Cópia também salva em: {alt_file_path}")

def start_processing(settings):
    log("Iniciando o processamento...")
    event_handler = PDFHandler(log, settings)
    observer = Observer()
    observer.schedule(event_handler, settings['source'], recursive=False)
    observer.start()
    threading.Thread(target=observer.join).start()

def settings_window(settings):
    if hasattr(settings_window, 'win') and settings_window.win.winfo_exists():
        settings_window.win.lift()
        return
    settings_window.win = ctk.CTkToplevel(root)
    win = settings_window.win
    win.title("Ajustes")
    win.geometry("400x500")
    win.configure(bg="black")

    ensure_keys(settings)

    def save_and_close():
        settings['source'] = source_entry.get()
        settings['destination'] = destination_entry.get()
        settings['subfolder_name'] = subfolder_entry.get()
        settings['file_name'] = file_name_entry.get()
        settings['use_alternative_dir'] = 'True' if use_alt_dir_var.get() else 'False'
        settings['alternative_dir'] = alternative_dir_entry.get()
        settings['include_name_in_alt'] = 'True' if include_name_in_alt_var.get() else 'False'
        settings['name_pattern_start'] = name_pattern_start_entry.get()
        settings['name_pattern_end'] = name_pattern_end_entry.get()
        settings['use_filename_as_name'] = 'True' if use_filename_as_name_var.get() else 'False'
        save_settings(settings)
        win.destroy()
        log("Configurações salvas!")

    def browse_folder(entry_var):
        folder_selected = filedialog.askdirectory()
        entry_var.set(folder_selected)

    scroll_frame = ctk.CTkScrollableFrame(win, width=400, height=500)
    scroll_frame.pack(fill='both', expand=True, padx=5, pady=5)

    ctk.CTkLabel(scroll_frame, text="Pasta de Origem:", text_color="white", font=("Arial", 14)).pack()
    source_var = tk.StringVar(value=settings['source'])
    source_frame = ctk.CTkFrame(scroll_frame)
    source_frame.pack(fill='x', padx=5, pady=5)
    source_entry = ctk.CTkEntry(source_frame, textvariable=source_var, font=("Arial", 14))
    source_entry.pack(side='left', fill='x', expand=True)
    ctk.CTkButton(source_frame, text="Browse", command=lambda: browse_folder(source_var)).pack(side='right')

    ctk.CTkLabel(scroll_frame, text="Pasta de Destino:", text_color="white", font=("Arial", 14)).pack()
    destination_var = tk.StringVar(value=settings['destination'])
    destination_frame = ctk.CTkFrame(scroll_frame)
    destination_frame.pack(fill='x', padx=5, pady=5)
    destination_entry = ctk.CTkEntry(destination_frame, textvariable=destination_var, font=("Arial", 14))
    destination_entry.pack(side='left', fill='x', expand=True)
    ctk.CTkButton(destination_frame, text="Browse", command=lambda: browse_folder(destination_var)).pack(side='right')

    ctk.CTkLabel(scroll_frame, text="Nome da Subpasta:", text_color="white", font=("Arial", 14)).pack()
    subfolder_entry = ctk.CTkEntry(scroll_frame, textvariable=tk.StringVar(value=settings['subfolder_name']), font=("Arial", 14))
    subfolder_entry.pack(fill='x', padx=5, pady=5)

    ctk.CTkLabel(scroll_frame, text="Nome do Arquivo:", text_color="white", font=("Arial", 14)).pack()
    file_name_entry = ctk.CTkEntry(scroll_frame, textvariable=tk.StringVar(value=settings['file_name']), font=("Arial", 14))
    file_name_entry.pack(fill='x', padx=5, pady=5)

    ctk.CTkLabel(scroll_frame, text="Padrão de Início do Nome:", text_color="white", font=("Arial", 14)).pack()
    name_pattern_start_entry = ctk.CTkEntry(scroll_frame, textvariable=tk.StringVar(value=settings['name_pattern_start']), font=("Arial", 14))
    name_pattern_start_entry.pack(fill='x', padx=5, pady=5)

    ctk.CTkLabel(scroll_frame, text="Padrão de Fim do Nome:", text_color="white", font=("Arial", 14)).pack()
    name_pattern_end_entry = ctk.CTkEntry(scroll_frame, textvariable=tk.StringVar(value=settings['name_pattern_end']), font=("Arial", 14))
    name_pattern_end_entry.pack(fill='x', padx=5, pady=5)

    use_alt_dir_var = tk.BooleanVar(value=settings['use_alternative_dir'] == 'True')
    ctk.CTkCheckBox(scroll_frame, text="Usar Diretório Alternativo", variable=use_alt_dir_var, text_color="white", font=("Arial", 14)).pack()

    ctk.CTkLabel(scroll_frame, text="Diretório Alternativo:", text_color="white", font=("Arial", 14)).pack()
    alternative_dir_var = tk.StringVar(value=settings['alternative_dir'])
    alternative_dir_frame = ctk.CTkFrame(scroll_frame)
    alternative_dir_frame.pack(fill='x', padx=5, pady=5)
    alternative_dir_entry = ctk.CTkEntry(alternative_dir_frame, textvariable=alternative_dir_var, font=("Arial", 14))
    alternative_dir_entry.pack(side='left', fill='x', expand=True)
    ctk.CTkButton(alternative_dir_frame, text="Browse", command=lambda: browse_folder(alternative_dir_var)).pack(side='right')

    include_name_in_alt_var = tk.BooleanVar(value=settings['include_name_in_alt'] == 'True')
    ctk.CTkCheckBox(scroll_frame, text="Incluir Nome do Colaborador no Arquivo Alternativo", variable=include_name_in_alt_var, text_color="white", font=("Arial", 14)).pack()

    use_filename_as_name_var = tk.BooleanVar(value=settings['use_filename_as_name'] == 'True')
    ctk.CTkCheckBox(scroll_frame, text="Usar Nome do Arquivo como Nome do Colaborador", variable=use_filename_as_name_var, text_color="white", font=("Arial", 14)).pack()

    ctk.CTkButton(scroll_frame, text="Salvar", command=save_and_close).pack(pady=20)

def log(message):
    console_text.config(state='normal')
    console_text.insert(tk.END, message + "\n")
    console_text.see(tk.END)
    console_text.config(state='disabled')

# Funções de API
def register_user(username, password):
    response = requests.post(f'{API_URL}/register', json={'username': username, 'password': password})
    return response.json()

def login_user(username, password):
    response = requests.post(f'{API_URL}/login', json={'username': username, 'password': password})
    return response.json()

# Função para exibir a página de login
def show_login_page():
    for widget in root.winfo_children():
        widget.destroy()

    ctk.CTkLabel(root, text="Login", font=("Arial", 20)).pack(pady=10)

    ctk.CTkLabel(root, text="Username:", font=("Arial", 14)).pack()
    username_entry = ctk.CTkEntry(root, font=("Arial", 14))
    username_entry.pack(pady=5)

    ctk.CTkLabel(root, text="Password:", font=("Arial", 14)).pack()
    password_entry = ctk.CTkEntry(root, show="*", font=("Arial", 14))
    password_entry.pack(pady=5)

    def login():
        username = username_entry.get()
        password = password_entry.get()
        response = login_user(username, password)
        if response['message'] == 'Login successful':
            show_main_page()
        else:
            messagebox.showerror("Error", response['message'])

    def show_register_page():
        show_registration_page()

    ctk.CTkButton(root, text="Login", command=login, font=("Arial", 14)).pack(pady=10)
    ctk.CTkButton(root, text="Register", command=show_register_page, font=("Arial", 14)).pack()

# Função para exibir a página de registro
def show_registration_page():
    for widget in root.winfo_children():
        widget.destroy()

    ctk.CTkLabel(root, text="Register", font=("Arial", 20)).pack(pady=10)

    ctk.CTkLabel(root, text="Username:", font=("Arial", 14)).pack()
    username_entry = ctk.CTkEntry(root, font=("Arial", 14))
    username_entry.pack(pady=5)

    ctk.CTkLabel(root, text="Password:", font=("Arial", 14)).pack()
    password_entry = ctk.CTkEntry(root, show="*", font=("Arial", 14))
    password_entry.pack(pady=5)

    def register():
        username = username_entry.get()
        password = password_entry.get()
        response = register_user(username, password)
        if response['message'] == 'User registered successfully':
            show_login_page()
        else:
            messagebox.showerror("Error", response['message'])

    ctk.CTkButton(root, text="Register", command=register, font=("Arial", 14)).pack(pady=10)
    ctk.CTkButton(root, text="Back to Login", command=show_login_page, font=("Arial", 14)).pack()

# Função para exibir a página principal
def show_main_page():
    for widget in root.winfo_children():
        widget.destroy()

    logo = tk.PhotoImage(file='images/logo.png')
    logo_label = tk.Label(root, image=logo)
    logo_label.pack(pady=10)

    title_label = ttk.Label(root, text="AutomateWork", font=("Arial", 16, "bold"))
    title_label.pack()

    button_automate = ttk.Button(root, text="Automatizar", command=lambda: start_processing(settings), style='TRoundedButton.TButton')
    button_settings = ttk.Button(root, text="Ajustes", command=lambda: settings_window(settings), style='TRoundedButton.TButton')
    button_automate.pack(fill='x', padx=50, pady=10)
    button_settings.pack(fill='x', padx=50, pady=10)

    global console_text
    console_text = scrolledtext.ScrolledText(root, height=8, state='disabled', font=("Arial", 14), bg="black", fg="white")
    console_text.pack(fill='both', expand=True, padx=20, pady=10)
    console_text.config(state='normal')

# GUI setup
root = ctk.CTk()
root.title("AutomateWork")
root.geometry("500x600")
root.iconbitmap('images/icon.ico')

# Carregar configurações
settings = load_settings()

# Exibir a página de login ao iniciar o programa
show_login_page()

root.mainloop()
