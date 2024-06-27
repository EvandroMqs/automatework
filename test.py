import tkinter as tk
import customtkinter as ctk

def on_combobox_select(event):
    selected_item = event.widget.get()
    print(f'Selecionado na Combobox: {selected_item}')

def on_listbox_select(event):
    selected_item = listbox.get(listbox.curselection())
    print(f'Selecionado na Listbox: {selected_item}')

def on_radiobutton_select():
    selected_item = radio_var.get()
    print(f'Selecionado no Radiobutton: {selected_item}')

def on_checkbutton_select():
    selected_items = [check1_var.get(), check2_var.get(), check3_var.get()]
    print(f'Selecionado no Checkbutton: {selected_items}')

# Configuração da janela principal
root = ctk.CTk()
root.title("Teste de Design com Select Boxes")
root.geometry("500x500")

# Configurações de tema do customtkinter
ctk.set_appearance_mode("dark")  # Modos: "System" (padrão), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Temas: "blue" (padrão), "green", "dark-blue"

# Combobox do customtkinter
combo_label = ctk.CTkLabel(root, text="Combobox:")
combo_label.pack(pady=5)
combo = ctk.CTkComboBox(root, values=["Opção 1", "Opção 2", "Opção 3"])
combo.bind("<<ComboboxSelected>>", on_combobox_select)
combo.pack(pady=5)

# Listbox do customtkinter
listbox_label = ctk.CTkLabel(root, text="Listbox:")
listbox_label.pack(pady=5)
listbox_frame = ctk.CTkFrame(root)
listbox_frame.pack(pady=5, fill=tk.BOTH, expand=True)
listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE)
listbox.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
for item in ["Item A", "Item B", "Item C"]:
    listbox.insert(tk.END, item)
listbox.bind("<<ListboxSelect>>", on_listbox_select)

# Radiobuttons do customtkinter
radio_label = ctk.CTkLabel(root, text="Radiobuttons:")
radio_label.pack(pady=5)
radio_var = tk.StringVar(value="Opção 1")
radio1 = ctk.CTkRadioButton(root, text="Opção 1", variable=radio_var, value="Opção 1", command=on_radiobutton_select)
radio2 = ctk.CTkRadioButton(root, text="Opção 2", variable=radio_var, value="Opção 2", command=on_radiobutton_select)
radio3 = ctk.CTkRadioButton(root, text="Opção 3", variable=radio_var, value="Opção 3", command=on_radiobutton_select)
radio1.pack(pady=2)
radio2.pack(pady=2)
radio3.pack(pady=2)

# Checkbuttons do customtkinter
check_label = ctk.CTkLabel(root, text="Checkbuttons:")
check_label.pack(pady=5)
check1_var = tk.BooleanVar()
check2_var = tk.BooleanVar()
check3_var = tk.BooleanVar()
check1 = ctk.CTkCheckBox(root, text="Opção 1", variable=check1_var, command=on_checkbutton_select)
check2 = ctk.CTkCheckBox(root, text="Opção 2", variable=check2_var, command=on_checkbutton_select)
check3 = ctk.CTkCheckBox(root, text="Opção 3", variable=check3_var, command=on_checkbutton_select)
check1.pack(pady=2)
check2.pack(pady=2)
check3.pack(pady=2)

# Combobox do customtkinter (referência)
ctk_label = ctk.CTkLabel(root, text="Customtkinter Combobox:")
ctk_label.pack(pady=5)
ctk_combo = ctk.CTkComboBox(root, values=["Custom 1", "Custom 2", "Custom 3"])
ctk_combo.pack(pady=5)

# Loop principal
root.mainloop()
