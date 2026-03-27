import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
from mysql.connector import Error
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF
import datetime

# Configuración Visual Premium
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class DatabaseHelper:
    def conectar(self):
        try:
            # Conectando estrictamente a la base de datos 'ice2'
            return mysql.connector.connect(host='localhost', database='ice2', user='root', password='')
        except Error as e:
            messagebox.showerror("Error BD", f"Asegúrate de que XAMPP esté encendido.\nError: {e}")
            return None

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ICEFRIOHIELO - Sistema POS Premium v2.0")
        self.geometry("1300x800")
        self.db = DatabaseHelper()
        self.usuario_actual = None 
        
        self.configurar_estilos_tablas()
        self.mostrar_login()

    def configurar_estilos_tablas(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=35, borderwidth=0, font=('Arial', 11))
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background="#1f538d", foreground="white", font=('Arial', 11, 'bold'), padding=5)

    def limpiar_pantalla(self):
        for widget in self.winfo_children(): widget.destroy()

    # ==========================================
    # LOGIN
    # ==========================================
    def mostrar_login(self):
        self.limpiar_pantalla()
        self.grid_rowconfigure(0, weight=1); self.grid_columnconfigure(0, weight=1)
        
        frame = ctk.CTkFrame(self, width=400, height=500, corner_radius=15)
        frame.grid(row=0, column=0)
        frame.grid_propagate(False)
        
        ctk.CTkLabel(frame, text="ICEFRIOHIELO", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(50, 20))
        self.user_entry = ctk.CTkEntry(frame, placeholder_text="Usuario", width=280, height=45)
        self.user_entry.pack(pady=15)
        self.pass_entry = ctk.CTkEntry(frame, placeholder_text="Contraseña", show="*", width=280, height=45)
        self.pass_entry.pack(pady=15)
        ctk.CTkButton(frame, text="Ingresar", width=280, height=50, font=ctk.CTkFont(weight="bold"), command=self.validar_login).pack(pady=30)
        
        # Credenciales de prueba (Administrador por defecto)
        self.user_entry.insert(0, "admin")
        self.pass_entry.insert(0, "admin123")

    def validar_login(self):
        conn = self.db.conectar()
        if not conn: return
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Personal WHERE usuario=%s AND contrasena=%s", (self.user_entry.get(), self.pass_entry.get()))
        usr = cursor.fetchone()
        conn.close()
        
        if usr:
            self.usuario_actual = usr
            self.mostrar_app_principal()
        else: messagebox.showerror("Error", "Credenciales incorrectas")

    # ==========================================
    # APP PRINCIPAL Y SIDEBAR
    # ==========================================
    def mostrar_app_principal(self):
        self.limpiar_pantalla()
        self.grid_rowconfigure(0, weight=1); self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)
        
        ctk.CTkLabel(self.sidebar, text="ICEFRIOHIELO", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=20)
        ctk.CTkLabel(self.sidebar, text=f"{self.usuario_actual['nombreCompleto']}\n{self.usuario_actual['rol']}", text_color="#2fa572").grid(row=1, column=0, pady=(0,20))

        ctk.CTkButton(self.sidebar, text="🛒 Punto de Venta", command=lambda: self.cambiar_pestana("pos")).grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        ctk.CTkButton(self.sidebar, text="📋 Histórico de Ventas", command=lambda: self.cambiar_pestana("historial")).grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        ctk.CTkButton(self.sidebar, text="🚨 Registrar Merma", command=lambda: self.cambiar_pestana("mermas")).grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        
        if self.usuario_actual['rol'] == 'Administrador':
            ctk.CTkButton(self.sidebar, text="📦 Gestión de Productos", command=lambda: self.cambiar_pestana("productos")).grid(row=5, column=0, padx=20, pady=5, sticky="ew")
            ctk.CTkButton(self.sidebar, text="👥 Gestión Usuarios", command=lambda: self.cambiar_pestana("usuarios")).grid(row=6, column=0, padx=20, pady=5, sticky="ew")
            ctk.CTkButton(self.sidebar, text="📊 Dashboard & Reportes", fg_color="#d35400", hover_color="#a04000", command=lambda: self.cambiar_pestana("dashboard")).grid(row=7, column=0, padx=20, pady=5, sticky="ew")
            
        ctk.CTkButton(self.sidebar, text="🚪 Salir", fg_color="#c0392b", hover_color="#922b21", command=self.mostrar_login).grid(row=11, column=0, padx=20, pady=20, sticky="ew")

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.carrito = [] 
        self.cambiar_pestana("pos")

    def cambiar_pestana(self, nombre):
        for widget in self.main_frame.winfo_children(): widget.destroy()
        if nombre == "pos": self.construir_pos()
        elif nombre == "historial": self.construir_historial()
        elif nombre == "mermas": self.construir_mermas()
        elif nombre == "productos": self.construir_productos()
        elif nombre == "usuarios": self.construir_usuarios()
        elif nombre == "dashboard": self.construir_dashboard()

    # ==========================================
    # MÓDULO: PUNTO DE VENTA (Con Filtros y Toppings)
    # ==========================================
    def construir_pos(self):
        self.main_frame.grid_columnconfigure(0, weight=3); self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_rowconfigure(2, weight=1)
        
        ctk.CTkLabel(self.main_frame, text="Punto de Venta", font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,10))

        # Barra de Filtros (Categorías de la BD ice2)
        filter_frame = ctk.CTkScrollableFrame(self.main_frame, orientation="horizontal", height=50)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=(0,10), pady=(0,10))
        ctk.CTkButton(filter_frame, text="Todos", width=100, command=lambda: self.filtrar_pos("")).pack(side="left", padx=5)
        
        conn = self.db.conectar()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT idCategoria, nombre FROM Categorias")
            for cat in cur.fetchall():
                ctk.CTkButton(filter_frame, text=cat[1], width=100, fg_color="#8e44ad", hover_color="#732d91", 
                              command=lambda c=cat[0]: self.filtrar_pos(c)).pack(side="left", padx=5)
            conn.close()

        # Catálogo Izquierdo
        left_panel = ctk.CTkFrame(self.main_frame)
        left_panel.grid(row=2, column=0, sticky="nsew", padx=(0,10))
        
        cols = ("ID", "Producto", "Precio", "Stock")
        self.tree_pos = ttk.Treeview(left_panel, columns=cols, show="headings")
        for c in cols: self.tree_pos.heading(c, text=c)
        self.tree_pos.column("ID", width=50); self.tree_pos.column("Precio", width=80); self.tree_pos.column("Stock", width=60)
        self.tree_pos.pack(fill="both", expand=True, padx=10, pady=10)
        
        btn_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkLabel(btn_frame, text="Cantidad:").pack(side="left", padx=5)
        self.pos_cant = ctk.CTkEntry(btn_frame, width=60)
        self.pos_cant.insert(0, "1")
        self.pos_cant.pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="✅ Agregar a Ticket / Topping", fg_color="#27ae60", hover_color="#1e8449", command=self.agregar_carrito).pack(side="left", padx=10)

        # Ticket Derecho
        right_panel = ctk.CTkFrame(self.main_frame)
        right_panel.grid(row=1, column=1, rowspan=2, sticky="nsew")
        ctk.CTkLabel(right_panel, text="Ticket Actual", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        
        cols_tk = ("Producto", "Cant", "Subtotal")
        self.tree_ticket = ttk.Treeview(right_panel, columns=cols_tk, show="headings")
        for c in cols_tk: self.tree_ticket.heading(c, text=c)
        self.tree_ticket.column("Cant", width=50); self.tree_ticket.column("Subtotal", width=80)
        self.tree_ticket.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkButton(right_panel, text="❌ Quitar Seleccionado", fg_color="#c0392b", hover_color="#922b21", command=self.quitar_carrito).pack(pady=5)
        self.lbl_total = ctk.CTkLabel(right_panel, text="Total: $0.00", font=ctk.CTkFont(size=30, weight="bold"), text_color="#2fa572")
        self.lbl_total.pack(pady=15)
        ctk.CTkButton(right_panel, text="💰 COBRAR TICKET", height=60, font=ctk.CTkFont(size=18, weight="bold"), command=self.procesar_venta).pack(fill="x", padx=10, pady=15)
        
        self.filtrar_pos("")

    def filtrar_pos(self, id_categoria):
        for item in self.tree_pos.get_children(): self.tree_pos.delete(item)
        conn = self.db.conectar()
        if not conn: return
        cursor = conn.cursor(dictionary=True)
        if id_categoria == "":
            cursor.execute("SELECT idProducto, nombre, precio, stock FROM Productos WHERE stock > 0")
        else:
            cursor.execute("SELECT idProducto, nombre, precio, stock FROM Productos WHERE stock > 0 AND idCategoria=%s", (id_categoria,))
        for p in cursor.fetchall():
            self.tree_pos.insert("", "end", values=(p['idProducto'], p['nombre'], float(p['precio']), p['stock']))
        conn.close()

    def agregar_carrito(self):
        sel = self.tree_pos.selection()
        if not sel: return messagebox.showwarning("Aviso", "Selecciona un producto o topping.")
        item = self.tree_pos.item(sel[0])['values']
        
        try:
            cant = int(self.pos_cant.get())
            if cant <= 0 or cant > int(item[3]): raise ValueError
        except ValueError:
            return messagebox.showerror("Error", "Cantidad inválida o stock insuficiente.")
        
        subtotal = float(item[2]) * cant
        for prod in self.carrito:
            if prod["id"] == item[0]:
                prod["cantidad"] += cant
                prod["subtotal"] += subtotal
                self.actualizar_ticket()
                return
        self.carrito.append({"id": item[0], "nombre": item[1], "cantidad": cant, "subtotal": subtotal})
        self.actualizar_ticket()

    def quitar_carrito(self):
        sel = self.tree_ticket.selection()
        if not sel: return
        self.carrito.pop(self.tree_ticket.index(sel[0]))
        self.actualizar_ticket()

    def actualizar_ticket(self):
        for item in self.tree_ticket.get_children(): self.tree_ticket.delete(item)
        total = 0
        for i in self.carrito:
            self.tree_ticket.insert("", "end", values=(i["nombre"], i["cantidad"], f"${i['subtotal']:.2f}"))
            total += i["subtotal"]
        self.lbl_total.configure(text=f"Total: ${total:.2f}")

    def procesar_venta(self):
        if not self.carrito: return
        conn = self.db.conectar()
        try:
            cur = conn.cursor()
            total = sum(i["subtotal"] for i in self.carrito)
            # Guardamos la Venta en BD 'ice2'
            cur.execute("INSERT INTO Ventas (totalVenta, idPersonal) VALUES (%s, %s)", (total, self.usuario_actual['idPersonal']))
            id_venta = cur.lastrowid
            
            for i in self.carrito:
                # Guardamos Detalles
                cur.execute("INSERT INTO DetalleVentas (idVenta, idProducto, cantidad, subtotal) VALUES (%s,%s,%s,%s)", 
                            (id_venta, i["id"], i["cantidad"], i["subtotal"]))
                # Descontamos Stock
                cur.execute("UPDATE Productos SET stock = stock - %s WHERE idProducto = %s", (i["cantidad"], i["id"]))
                
            conn.commit()
            messagebox.showinfo("Éxito", f"Ticket #{id_venta} cobrado.")
            self.carrito = []
            self.actualizar_ticket()
            self.filtrar_pos("")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e))
        finally: 
            conn.close()

    # ==========================================
    # MÓDULO: HISTÓRICO (MASTER-DETALLE)
    # ==========================================
    def construir_historial(self):
        self.main_frame.grid_rowconfigure(1, weight=1); self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.main_frame, text="Histórico de Ventas (Clic en un ticket para ver detalles)", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=10, sticky="w")
        
        # Maestro (Ventas)
        cols_v = ("Folio", "Fecha", "Total Venta", "Cajero")
        self.tree_ventas = ttk.Treeview(self.main_frame, columns=cols_v, show="headings")
        for c in cols_v: self.tree_ventas.heading(c, text=c)
        self.tree_ventas.grid(row=1, column=0, sticky="nsew", pady=5)
        self.tree_ventas.bind("<<TreeviewSelect>>", self.cargar_detalle_ticket)

        ctk.CTkLabel(self.main_frame, text="Desglose Exacto del Ticket", font=ctk.CTkFont(size=18, weight="bold")).grid(row=2, column=0, pady=10, sticky="w")
        
        # Detalle
        cols_d = ("Producto", "Cantidad", "Subtotal", "Vendedor que atendió")
        self.tree_detalle = ttk.Treeview(self.main_frame, columns=cols_d, show="headings")
        for c in cols_d: self.tree_detalle.heading(c, text=c)
        self.tree_detalle.grid(row=3, column=0, sticky="nsew", pady=5)
        
        conn = self.db.conectar()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT idVenta, fecha, totalVenta, Vendedor FROM VistaReporteVentas ORDER BY idVenta DESC")
            for r in cur.fetchall(): 
                self.tree_ventas.insert("", "end", values=(r[0], r[1], f"${r[2]:.2f}", r[3]))
            conn.close()

    def cargar_detalle_ticket(self, event):
        sel = self.tree_ventas.selection()
        if not sel: return
        folio = self.tree_ventas.item(sel[0])['values'][0]
        
        for item in self.tree_detalle.get_children(): self.tree_detalle.delete(item)
        conn = self.db.conectar()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT Producto, cantidad, subtotal, Vendedor FROM vw_detalle_ticket_app WHERE Folio = %s", (folio,))
        for r in cur.fetchall():
            self.tree_detalle.insert("", "end", values=(r['Producto'], r['cantidad'], f"${r['subtotal']:.2f}", r['Vendedor']))
        conn.close()

    # ==========================================
    # MÓDULO: REGISTRO DE MERMAS
    # ==========================================
    def construir_mermas(self):
        ctk.CTkLabel(self.main_frame, text="Registro de Mermas (Pérdidas)", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=20, anchor="w")
        
        form = ctk.CTkFrame(self.main_frame, width=500, corner_radius=15)
        form.pack(pady=20, ipadx=40, ipady=40)
        
        conn = self.db.conectar()
        cur = conn.cursor()
        cur.execute("SELECT idProducto, nombre, stock FROM Productos WHERE stock > 0")
        self.prods_mermas = {f"{r[1]} (Stock: {r[2]})": r[0] for r in cur.fetchall()}
        conn.close()

        ctk.CTkLabel(form, text="Seleccione el producto dañado:", font=ctk.CTkFont(weight="bold")).pack(pady=(10,5))
        self.cb_mermas = ctk.CTkComboBox(form, values=list(self.prods_mermas.keys()), width=350, height=40)
        self.cb_mermas.pack(pady=5)
        
        ctk.CTkLabel(form, text="Cantidad a desechar:", font=ctk.CTkFont(weight="bold")).pack(pady=(15,5))
        self.ent_merma_cant = ctk.CTkEntry(form, width=150, height=40)
        self.ent_merma_cant.pack(pady=5)
        
        ctk.CTkLabel(form, text="Motivo (Ej. Caducado, Derretido):", font=ctk.CTkFont(weight="bold")).pack(pady=(15,5))
        self.ent_merma_motivo = ctk.CTkEntry(form, width=350, height=40)
        self.ent_merma_motivo.pack(pady=5)
        
        ctk.CTkButton(form, text="🚨 Registrar y Descontar", height=45, fg_color="#d35400", hover_color="#a04000", font=ctk.CTkFont(weight="bold"), command=self.guardar_merma).pack(pady=30)

    def guardar_merma(self):
        prod_str = self.cb_mermas.get()
        if prod_str not in self.prods_mermas: return
        id_prod = self.prods_mermas[prod_str]
        motivo = self.ent_merma_motivo.get()
        
        try: cant = int(self.ent_merma_cant.get())
        except ValueError: return messagebox.showerror("Error", "Cantidad inválida.")

        if not motivo: return messagebox.showwarning("Aviso", "Justifique el motivo.")

        conn = self.db.conectar()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Mermas (idProducto, cantidad, motivo, idPersonal) VALUES (%s, %s, %s, %s)",
                           (id_prod, cant, motivo, self.usuario_actual['idPersonal']))
            cursor.execute("UPDATE Productos SET stock = stock - %s WHERE idProducto = %s", (cant, id_prod))
            conn.commit()
            messagebox.showinfo("Éxito", "Merma registrada correctamente.")
            self.cambiar_pestana("mermas") 
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error SQL", str(e))
        finally:
            conn.close()

    # ==========================================
    # GESTIÓN DE USUARIOS (Admin)
    # ==========================================
    def construir_usuarios(self):
        ctk.CTkLabel(self.main_frame, text="Gestión de Personal", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)
        
        form = ctk.CTkFrame(self.main_frame); form.pack(pady=10, fill="x", padx=20)
        self.u_nom = ctk.CTkEntry(form, placeholder_text="Nombre Completo"); self.u_nom.pack(side="left", padx=5)
        self.u_usr = ctk.CTkEntry(form, placeholder_text="Usuario"); self.u_usr.pack(side="left", padx=5)
        self.u_pwd = ctk.CTkEntry(form, placeholder_text="Contraseña"); self.u_pwd.pack(side="left", padx=5)
        self.u_rol = ctk.CTkComboBox(form, values=["Vendedor", "Administrador"]); self.u_rol.pack(side="left", padx=5)
        ctk.CTkButton(form, text="➕ Crear Usuario", command=self.crear_usuario).pack(side="left", padx=10)
        
        cols = ("ID", "Nombre", "Rol", "Usuario")
        self.tree_usr = ttk.Treeview(self.main_frame, columns=cols, show="headings")
        for c in cols: self.tree_usr.heading(c, text=c)
        self.tree_usr.pack(fill="both", expand=True, padx=20, pady=10)
        self.cargar_usuarios()

    def cargar_usuarios(self):
        for item in self.tree_usr.get_children(): self.tree_usr.delete(item)
        conn = self.db.conectar()
        cur = conn.cursor()
        cur.execute("SELECT idPersonal, nombreCompleto, rol, usuario FROM Personal")
        for r in cur.fetchall(): self.tree_usr.insert("", "end", values=r)
        conn.close()

    def crear_usuario(self):
        conn = self.db.conectar()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO Personal (nombreCompleto, rol, usuario, contrasena) VALUES (%s,%s,%s,%s)",
                        (self.u_nom.get(), self.u_rol.get(), self.u_usr.get(), self.u_pwd.get()))
            conn.commit(); self.cargar_usuarios()
            messagebox.showinfo("Éxito", "Usuario creado")
        except Exception as e: messagebox.showerror("Error", str(e))
        finally: conn.close()

    # ==========================================
    # GESTIÓN DE PRODUCTOS (Admin)
    # ==========================================
    def construir_productos(self):
        ctk.CTkLabel(self.main_frame, text="Gestión de Catálogo y Precios", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)
        
        form = ctk.CTkFrame(self.main_frame); form.pack(pady=10, fill="x", padx=20)
        self.p_nom = ctk.CTkEntry(form, placeholder_text="Nombre Producto"); self.p_nom.pack(side="left", padx=5)
        self.p_pre = ctk.CTkEntry(form, placeholder_text="Precio", width=80); self.p_pre.pack(side="left", padx=5)
        self.p_stk = ctk.CTkEntry(form, placeholder_text="Stock", width=80); self.p_stk.pack(side="left", padx=5)
        ctk.CTkButton(form, text="➕ Agregar Producto", command=self.crear_producto).pack(side="left", padx=10)
        ctk.CTkButton(form, text="🗑️ Eliminar Seleccionado", fg_color="#c0392b", command=self.eliminar_producto).pack(side="right", padx=10)
        
        cols = ("ID", "Producto", "Precio", "Stock Actual", "Mínimo")
        self.tree_prod = ttk.Treeview(self.main_frame, columns=cols, show="headings")
        for c in cols: self.tree_prod.heading(c, text=c)
        self.tree_prod.pack(fill="both", expand=True, padx=20, pady=10)
        self.cargar_gestion_productos()

    def cargar_gestion_productos(self):
        for item in self.tree_prod.get_children(): self.tree_prod.delete(item)
        conn = self.db.conectar()
        cur = conn.cursor()
        cur.execute("SELECT idProducto, nombre, precio, stock, stockMinimo FROM Productos")
        for r in cur.fetchall(): self.tree_prod.insert("", "end", values=r)
        conn.close()

    def crear_producto(self):
        conn = self.db.conectar()
        try:
            cur = conn.cursor()
            # En ice2, el idCategoria puede ser nulo o especificar un default. Usaremos 1.
            cur.execute("INSERT INTO Productos (nombre, precio, stock, stockMinimo, idCategoria) VALUES (%s,%s,%s,10,1)",
                        (self.p_nom.get(), float(self.p_pre.get()), int(self.p_stk.get())))
            conn.commit(); self.cargar_gestion_productos()
        except Exception as e: messagebox.showerror("Error", str(e))
        finally: conn.close()

    def eliminar_producto(self):
        sel = self.tree_prod.selection()
        if not sel: return
        item_id = self.tree_prod.item(sel[0])['values'][0]
        conn = self.db.conectar()
        try:
            conn.cursor().execute("DELETE FROM Productos WHERE idProducto=%s", (item_id,))
            conn.commit(); self.cargar_gestion_productos()
            messagebox.showinfo("Éxito", "Eliminado correctamente.")
        except Exception as e: messagebox.showerror("Error", "No se puede eliminar porque tiene ventas o mermas asociadas.")
        finally: conn.close()

    # ==========================================
    # DASHBOARD, REPORTES E INTELIGENCIA (Admin)
    # ==========================================
    def construir_dashboard(self):
        self.main_frame.grid_rowconfigure(2, weight=1); self.main_frame.grid_columnconfigure(0, weight=1); self.main_frame.grid_columnconfigure(1, weight=1)
        
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)
        ctk.CTkLabel(header, text="Analítica y Reportes Ejecutivos", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="📄 Exportar a PDF", fg_color="#c0392b", hover_color="#922b21", command=self.exportar_pdf).pack(side="right", padx=5)
        ctk.CTkButton(header, text="📊 Exportar a Excel", fg_color="#27ae60", hover_color="#1e8449", command=self.exportar_excel).pack(side="right", padx=5)

        # Gráfica
        chart_frame = ctk.CTkFrame(self.main_frame); chart_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10, padx=10)
        conn = self.db.conectar()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT Vendedor, IngresosGenerados FROM vw_estadisticas_vendedores")
        datos_vendedores = cur.fetchall()
        
        if datos_vendedores:
            nombres = [str(d['Vendedor']) for d in datos_vendedores]
            ventas = [float(d['IngresosGenerados']) for d in datos_vendedores]
            fig, ax = plt.subplots(figsize=(8, 3), facecolor='#2b2b2b')
            ax.set_facecolor('#2b2b2b')
            ax.bar(nombres, ventas, color='#3498db')
            ax.set_title('Rendimiento de Ventas por Personal', color='white', fontweight='bold')
            ax.tick_params(colors='white')
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        # BI (Sugerencias Inteligentes)
        bi_frame = ctk.CTkFrame(self.main_frame)
        bi_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(bi_frame, text="Inteligencia de Negocio y Sugerencias de Inventario", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        texto_bi = ctk.CTkTextbox(bi_frame, font=("Arial", 14), text_color="#f1c40f")
        texto_bi.pack(fill="both", expand=True, padx=10, pady=10)
        
        cur.execute("SELECT nombre, stock FROM Productos WHERE stock <= stockMinimo")
        alertas = cur.fetchall()
        sugerencias = "📈 ANÁLISIS AUTOMÁTICO DE LA BD ICE2:\n\n"
        if alertas:
            sugerencias += "🚨 ALERTA DE DESABASTO / RIESGO DE MERMA:\n"
            for a in alertas: sugerencias += f"  - Urge reabastecer: {a['nombre']} (Quedan solo {a['stock']})\n"
        else: sugerencias += "✅ Inventario sano. No hay productos bajo el mínimo.\n"
        
        cur.execute("SELECT p.nombre, sum(dv.cantidad) as total FROM DetalleVentas dv JOIN Productos p ON dv.idProducto = p.idProducto GROUP BY p.idProducto ORDER BY total ASC LIMIT 3")
        peores = cur.fetchall()
        if peores:
            sugerencias += "\n💡 ESTRATEGIA DE ROTACIÓN (Baja venta):\n"
            for p in peores: sugerencias += f"  - Promocionar o reducir compra de: {p['nombre']}\n"

        texto_bi.insert("0.0", sugerencias)
        texto_bi.configure(state="disabled")
        conn.close()

    def exportar_excel(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], title="Guardar Reporte Excel")
        if not filepath: return
        conn = self.db.conectar()
        try:
            df_vendedores = pd.read_sql("SELECT * FROM vw_estadisticas_vendedores", conn)
            df_detalle = pd.read_sql("SELECT * FROM vw_detalle_ticket_app", conn)
            with pd.ExcelWriter(filepath) as writer:
                df_vendedores.to_excel(writer, sheet_name='Estadisticas Personal', index=False)
                df_detalle.to_excel(writer, sheet_name='Desglose de Tickets', index=False)
            messagebox.showinfo("Éxito", "Reporte Excel generado correctamente.")
        except Exception as e: messagebox.showerror("Error", str(e))
        finally: conn.close()

    def exportar_pdf(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], title="Guardar Reporte PDF")
        if not filepath: return
        conn = self.db.conectar()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM vw_estadisticas_vendedores")
        datos = cur.fetchall()
        conn.close()

        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, "Reporte Ejecutivo - ICEFRIOHIELO", ln=True, align='C')
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(200, 10, f"Generado el: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
            pdf.ln(10)
            
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(80, 10, "Vendedor", border=1)
            pdf.cell(50, 10, "Tickets Emitidos", border=1)
            pdf.cell(60, 10, "Ingresos Generados", border=1)
            pdf.ln()
            
            pdf.set_font("Arial", '', 12)
            for d in datos:
                pdf.cell(80, 10, str(d['Vendedor']), border=1)
                pdf.cell(50, 10, str(d['TotalTickets']), border=1, align='C')
                pdf.cell(60, 10, f"${float(d['IngresosGenerados']):.2f}", border=1, align='R')
                pdf.ln()
                
            pdf.output(filepath)
            messagebox.showinfo("Éxito", "Reporte PDF generado correctamente.")
        except Exception as e: messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = App()
    app.mainloop()