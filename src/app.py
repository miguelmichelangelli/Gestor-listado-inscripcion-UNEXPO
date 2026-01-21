import tkinter as tk
from tkinter import messagebox, ttk, font
import sqlite3 as sql
import os
import re
import pdfplumber
import ctypes 

# Importando mis plugins
from plugins.add_student import add_student
from plugins.update_student import update_student
from plugins.delete_student import delete_student

# ------------------------------------------
#   VALIDACIÓN DE ENTRADAS
# ------------------------------------------
def validar_datos(exp, dia, hora, turno, sem, rend, acad):
    """Retorna (True, "") si todo está bien, o (False, "Mensaje de error") si falla algo."""
    
    # 1. Campos Vacíos
    if not all([exp, dia, hora, turno, sem, rend, acad]):
        return False, "Todos los campos son obligatorios."

    # 2. Expediente: Solo números, 9-10 caracteres
    if not re.fullmatch(r'\d{9,10}', exp):
        return False, "El Expediente debe contener solo números (entre 9 y 10 dígitos)."

    # 3. Fecha: dd/mm/aa (Ej: 25/01/2025)
    if not re.fullmatch(r'\d{1,2}/\d{1,2}/\d{4}', dia):
        return False, "Formato de fecha inválido. Use dd/mm/aaaa (Ej: 15/05/2025)."

    # 4. Hora: hh:mm
    if not re.fullmatch(r'\d{2}:\d{2}', hora):
        return False, "Formato de hora inválido. Use hh:mm (Ej: 09:30)."

    # 5. Validaciones Numéricas
    try:
        # Turno: número
        if not turno.isdigit():
            return False, "El Turno debe ser un número entero."

        # Semestre: 1 al 10
        if not (1 <= int(sem) <= 10):
            return False, "El Semestre debe ser un número entre 1 y 10."

        # Rendimiento: <= 1
        if not (0 <= float(rend) <= 1):
            return False, "El Rendimiento debe estar entre 0 y 1."

        # Académico: 0 <= x <= 10
        if not (0 <= float(acad) <= 10):
            return False, "El Índice Académico debe estar entre 0 y 10."

    except ValueError:
        return False, "Turno, Semestre, Rendimiento y Académico deben ser valores numéricos."

    return True, ""

# ------------------------------------------
#   LÓGICA DEL PROCESAMIENTO DE DATOS
# ------------------------------------------

def procesar_pdf_texto_plano():
    pdf_path = "Turnos de Inscripción 2025-2.pdf"
    db_name = 'unexpo.db'

    # Verifico si la DB ya existe para ahorrar tiempo
    if os.path.exists(db_name):
        try:
            conn = sql.connect(db_name)
            cursor = conn.cursor()
            # Chequeo rápido para ver si la tabla tiene datos
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='unexpo'")
            if cursor.fetchone():
                cursor.execute("SELECT count(*) FROM unexpo")
                total = cursor.fetchone()[0]
                if total > 0:
                    conn.close()
                    print(f" [DB] Base de datos cargada con {total} registros.")
                    return total
            conn.close()
        except: pass

    # Si no hay DB ni PDF, no puedo hacer nada
    if not os.path.exists(pdf_path): return 0

    print(" [PDF] Iniciando escaneo y extracción de datos...")
    conn = sql.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS unexpo") 
    cursor.execute('''CREATE TABLE unexpo 
                     (expediente TEXT PRIMARY KEY, dia_inscripcion TEXT, hora TEXT, 
                      turno TEXT, semestre TEXT, rendimiento TEXT, academico TEXT)''')
    
    contador = 0
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if not texto: continue
            
            # Leo línea por línea buscando patrones de expediente
            for linea in texto.split('\n'):
                linea = linea.strip()
                match_exp = re.match(r'^(\d{5,})', linea)
                
                if match_exp:
                    exp = match_exp.group(1)
                    contenido = linea.replace(exp, '', 1).strip()
                    dia, hora, turno, sem, rend, acad = "N/A", "N/A", "S/N", "S/N", "0.00", "0.00"

                    try:
                        # Extracción con Regex para asegurar precisión
                        match_hora = re.search(r'(\d{1,2}:\d{2})', contenido)
                        if match_hora:
                            hora = match_hora.group(1)
                            contenido = contenido.replace(hora, '')
                        
                        match_fecha = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', contenido)
                        if match_fecha:
                            dia = match_fecha.group(1)
                            contenido = contenido.replace(dia, '')

                        decimales = re.findall(r'(\d+\.\d{2})', contenido)
                        if len(decimales) >= 2:
                            rend, acad = decimales[0], decimales[1]
                            contenido = contenido.replace(rend, '').replace(acad, '')
                        elif len(decimales) == 1:
                            rend = decimales[0]
                            contenido = contenido.replace(rend, '')

                        enteros = re.findall(r'\b\d+\b', contenido)
                        enteros = [n for n in enteros if int(n) < 2000]
                        if len(enteros) >= 1:
                            enteros_int = [int(x) for x in enteros]
                            turno = str(max(enteros_int))
                            if len(enteros) > 1:
                                for x in enteros:
                                    if x != turno and int(x) <= 15: sem = x; break
                        
                        cursor.execute("INSERT OR REPLACE INTO unexpo VALUES (?,?,?,?,?,?,?)", 
                                     (exp, dia, hora, turno, sem, rend, acad))
                        contador += 1
                    except: pass

    conn.commit()
    conn.close()
    return contador

# ------------------------------------------
#   INTERFAZ GRÁFICA (GUI)
# ------------------------------------------

class AppUNEXPO:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión Académica - UNEXPO")
        self.root.geometry("800x700")
        self.root.configure(bg="#f0f2f5")

        # Configuración para que el icono se vea en la barra de tareas de Windows
        try:
            myappid = 'unexpo.gestor.inscripcion.v1' 
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except: pass

        # Carga del logo institucional
        try:
            img_logo = tk.PhotoImage(file="logo_unexpo.png")
            self.root.iconphoto(True, img_logo) 
        except:
            print("Aviso: No se encontró el logo.")

        # Estilos visuales
        self.estilo = ttk.Style()
        self.estilo.theme_use('clam')

        self.colores = {
            "primario": "#00007E",
            "fondo": "#f0f2f5",      
            "texto": "#333333",
            "verde": "#28a745",
            "naranja": "#fd7e14",
            "rojo": "#dc3545"
        }

        self.fuente_titulo = font.Font(family="Helvetica", size=16, weight="bold")
        self.fuente_normal = font.Font(family="Helvetica", size=11)
        self.fuente_negrita = font.Font(family="Helvetica", size=11, weight="bold")

        self.estilo.configure("TFrame", background=self.colores["fondo"])
        self.estilo.configure("TLabel", background=self.colores["fondo"], foreground=self.colores["texto"], font=self.fuente_normal)
        self.estilo.configure("TButton", font=self.fuente_negrita, padding=6)
        self.estilo.configure("TNotebook", background=self.colores["fondo"], tabposition='n')
        self.estilo.configure("TNotebook.Tab", font=("Helvetica", 10, "bold"), padding=[15, 5], background="#e0e0e0")
        self.estilo.map("TNotebook.Tab", background=[("selected", self.colores["primario"])], foreground=[("selected", "white")])

        # Header
        header = tk.Frame(self.root, bg=self.colores["primario"], height=60)
        header.pack(fill="x")
        tk.Label(header, text="UNEXPO | GESTIÓN DE INSCRIPCIONES", bg=self.colores["primario"], fg="white", 
                 font=("Helvetica", 14, "bold")).pack(pady=15)

        # Sistema de Pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=20, pady=20)

        self.tab_buscar = ttk.Frame(self.notebook)
        self.tab_agregar = ttk.Frame(self.notebook)
        self.tab_actualizar = ttk.Frame(self.notebook)
        self.tab_borrar = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_buscar, text="  🔍 CONSULTAR  ")
        self.notebook.add(self.tab_agregar, text="  ➕ AGREGAR  ")
        self.notebook.add(self.tab_actualizar, text="  ✏️ EDITAR  ")
        self.notebook.add(self.tab_borrar, text="  🗑️ ELIMINAR  ")

        self.crear_tab_buscar()
        self.crear_tab_agregar()
        self.crear_tab_actualizar()
        self.crear_tab_borrar()

    # --- Pestaña Consultar ---
    def crear_tab_buscar(self):
        frame = ttk.Frame(self.tab_buscar); frame.pack(pady=30)
        tk.Label(frame, text="Ingrese Número de Expediente", font=self.fuente_titulo).pack(pady=(0, 15))
        self.ent_bus_exp = ttk.Entry(frame, font=("Helvetica", 14), justify="center", width=25)
        self.ent_bus_exp.pack(ipady=5); self.ent_bus_exp.bind('<Return>', lambda e: self.buscar())
        
        tk.Button(frame, text="BUSCAR EXPEDIENTE", command=self.buscar, bg=self.colores["primario"], fg="white", 
                  font=self.fuente_negrita, relief="flat", cursor="hand2", padx=20, pady=5).pack(pady=20)
        
        self.frame_res = tk.LabelFrame(frame, text=" Detalles ", font=self.fuente_negrita, bg="white", fg="#555", padx=20, pady=20)
        self.frame_res.pack(fill="both", expand=True, ipadx=10)
        self.lbl_res = tk.Label(self.frame_res, text="Realice una búsqueda...", bg="white", font=("Consolas", 11), justify="left")
        self.lbl_res.pack()

    def buscar(self):
        exp = "".join(re.findall(r'\d+', self.ent_bus_exp.get()))
        conn = sql.connect('unexpo.db'); cursor = conn.cursor()
        cursor.execute("SELECT * FROM unexpo WHERE expediente = ?", (exp,))
        res = cursor.fetchone(); conn.close()
        if res:
            t = (f"Expediente           :  {res[0]}\n--------------------------------------\n"
                 f"📅 Día Inscripción    :  {res[1]}\n🕒 Hora               :  {res[2]}\n"
                 f"🔢 Turno              :  {res[3]}\n🎓 Semestre           :  {res[4]}\n"
                 f"📊 Índice Rendimiento :  {res[5]}\n📈 Índice Académico   :  {res[6]}")
            self.lbl_res.config(text=t, fg="black", font=("Consolas", 12))
        else: self.lbl_res.config(text=f"❌ No se encontró: {exp}", fg="red")

    # --- Pestaña Agregar ---
    def crear_tab_agregar(self):
        f = ttk.Frame(self.tab_agregar); f.pack(pady=20)
        tk.Label(f, text="Nuevo Registro Estudiantil", font=self.fuente_titulo).grid(row=0, column=0, columnspan=2, pady=20)
        self.ent_add = {}
        # Aquí actualicé los nombres de las etiquetas
        campos = ["Expediente", "Día", "Hora", "Turno", "Semestre", "Índice de Rendimiento", "Índice Académico"]
        for i, c in enumerate(campos):
            tk.Label(f, text=c+":", font=self.fuente_negrita).grid(row=i+1, column=0, sticky="e", padx=10, pady=8)
            e = ttk.Entry(f, width=25, font=self.fuente_normal); e.grid(row=i+1, column=1, sticky="w", padx=10); self.ent_add[c] = e
        tk.Button(f, text="GUARDAR REGISTRO", command=self.agregar, bg=self.colores["verde"], fg="white", padx=15).grid(row=8, column=0, columnspan=2, pady=30)

    def agregar(self):
        try:
            # 1. Obtener valores
            exp = self.ent_add["Expediente"].get()
            dia = self.ent_add["Día"].get()
            hora = self.ent_add["Hora"].get()
            turno = self.ent_add["Turno"].get()
            sem = self.ent_add["Semestre"].get()
            rend = self.ent_add["Índice de Rendimiento"].get()
            acad = self.ent_add["Índice Académico"].get()

            # 2. VALIDAR ANTES DE GUARDAR
            es_valido, mensaje_error = validar_datos(exp, dia, hora, turno, sem, rend, acad)
            
            if not es_valido:
                messagebox.showerror("Error de Validación", mensaje_error)
                return  # Se detiene la función aquí

            # 3. Si todo está bien, guardar
            add_student(sql, (exp, dia, hora, turno, sem, rend, acad))
            messagebox.showinfo("Éxito", "Guardado Correctamente")
            [self.ent_add[c].delete(0,'end') for c in self.ent_add]
        
        except Exception as e: 
            messagebox.showerror("Error Inesperado", str(e))

    # --- Pestaña Actualizar ---
    def crear_tab_actualizar(self):
        f = ttk.Frame(self.tab_actualizar); f.pack(pady=20)
        
        # Título
        tk.Label(f, text="Modificar Datos Existentes", font=self.fuente_titulo).grid(row=0, column=0, columnspan=2, pady=20)
        
        # 1. Bloque de Búsqueda (El Expediente)
        tk.Label(f, text="Expediente (Clave):", font=("Helvetica", 11, "bold"), fg=self.colores["primario"]).grid(row=1, column=0, sticky="e", padx=10, pady=8)
        self.ent_upd_exp = ttk.Entry(f, width=25, font=("Helvetica", 11, "bold"))
        self.ent_upd_exp.grid(row=1, column=1, sticky="w", padx=10)

        # 2. SEPARADOR VISUAL
        tk.Frame(f, height=2, bg="#ccc").grid(row=2, column=0, columnspan=2, sticky="ew", pady=15)

        # 3. Bloque de Datos (Igual al de Agregar)
        self.ent_upd = {}
        campos = ["Día", "Hora", "Turno", "Semestre", "Índice de Rendimiento", "Índice Académico"]
        for i, c in enumerate(campos):
            tk.Label(f, text=c+":", font=self.fuente_negrita).grid(row=i+3, column=0, sticky="e", padx=10, pady=8)
            e = ttk.Entry(f, width=25, font=self.fuente_normal)
            e.grid(row=i+3, column=1, sticky="w", padx=10)
            self.ent_upd[c] = e

        # Botón
        tk.Button(f, text="ACTUALIZAR DATOS", command=self.actualizar, bg=self.colores["naranja"], fg="white", padx=15).grid(row=10, column=0, columnspan=2, pady=30)

    def actualizar(self):
        try:
            # 1. Obtener valores
            exp = self.ent_upd_exp.get() # El expediente viene de su input propio
            dia = self.ent_upd["Día"].get()
            hora = self.ent_upd["Hora"].get()
            turno = self.ent_upd["Turno"].get()
            sem = self.ent_upd["Semestre"].get()
            rend = self.ent_upd["Índice de Rendimiento"].get()
            acad = self.ent_upd["Índice Académico"].get()

            # 2. VALIDAR ANTES DE ACTUALIZAR
            es_valido, mensaje_error = validar_datos(exp, dia, hora, turno, sem, rend, acad)

            if not es_valido:
                messagebox.showerror("Error de Validación", mensaje_error)
                return

            # 3. Empaquetar tupla (orden esperado por tu DB/Plugin)
            # NOTA: Asegúrate de que update_student espere este orden. 
            # Si tu query SQL es UPDATE ... SET dia=?, ... WHERE expediente=?
            # entonces el expediente va AL FINAL de la tupla.
            d = (dia, hora, turno, sem, rend, acad, exp)
            
            update_student(sql, d)
            messagebox.showinfo("Éxito", "Datos Actualizados")
        
        except Exception as e: 
            messagebox.showerror("Error", str(e))

    # --- Pestaña Eliminar ---
    def crear_tab_borrar(self):
        f = ttk.Frame(self.tab_borrar); f.pack(pady=40)
        tk.Label(f, text="⚠️ Eliminar Estudiante", font=self.fuente_titulo, fg=self.colores["rojo"]).pack(pady=10)
        tk.Label(f, text="Expediente a eliminar:").pack()
        self.ent_del = ttk.Entry(f, font=("Helvetica", 14), justify="center"); self.ent_del.pack(pady=15, ipady=5)
        tk.Button(f, text="ELIMINAR REGISTRO", command=self.borrar, bg=self.colores["rojo"], fg="white", padx=20).pack(pady=10)

    def borrar(self):
        if messagebox.askyesno("Confirmar", "Esta acción no se puede deshacer."):
            delete_student(sql, self.ent_del.get()); messagebox.showinfo("Hecho", "Eliminado")

if __name__ == "__main__":
    # Arrancando el sistema
    try:
        total = procesar_pdf_texto_plano()
        if total == 0: print("Sistema iniciado.")
    except Exception as e:
        print(f"Error de inicio: {e}")

    root = tk.Tk()
    app = AppUNEXPO(root)
    root.mainloop()