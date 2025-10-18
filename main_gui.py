"""
🌸 Procesamiento de Imágenes
Interfaz gráfica usando Tkinter con pestañas.

Sistema de operaciones sin acumulación:
- Cada transformación parte de la imagen ORIGINAL
- Se guarda en una lista y se recalcula desde cero
- Si cambias un parámetro, reemplaza la operación anterior
- Resultado = Original + todas las operaciones en orden
"""

import sys
import os
from PIL import Image, ImageTk
import image_processing_lib as ip
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class ImageApp:
    def __init__(self, root):
        self.root = root
        root.title('🌸 Image Studio – Procesamiento de Imágenes')
        
        # ===== ESTADO DE LA APLICACIÓN =====
        # Guardamos la imagen original sin tocar, y self.img es lo que se muestra
        # Las operaciones se guardan en self.operations y se aplican todas de una
        self.original = None              # imagen de referencia (nunca se modifica)
        self.img = None                   # resultado visible (se actualiza al aplicar ops)
        self.img_tk = None                # foto de Tkinter (para mostrar en canvas)
        self.img_path = None              # ruta del archivo actual
        self.second_img = None            # segunda imagen para fusión
        
        # Lista de operaciones activas: [(tipo, {parámetros}), ...]
        # Ejemplo: [('brightness', {'value': 50}), ('gamma', {'gamma': 1.5})]
        self.operations = []
        
        # Zoom visual: solo para la vista, no modifica la imagen
        self.display_scale = 1.0
        

        
        # ===== VARIABLES DE INTERACCIÓN (recorte con mouse) =====
        self.crop_mode = False            # ¿estamos en modo seleccionar área?
        self.crop_start = None            # punto inicial del recorte (x, y)
        self.crop_end = None              # punto final del recorte (x, y)
        self.crop_rect = None             # ID del rectángulo dibujado en canvas
        
        # ===== VARIABLES DE INTERACCIÓN (zoom con mouse) =====
        self.zoom_mode = False            # ¿estamos en modo zoom?
        self.zoom_point = None            # punto donde hicimos click
        self.zoom_factor = 2.0            # factor de ampliación (2x = dobla tamaño)
        
        # ===== COLORES (tema rosa claro) =====
        self.pink_bg = '#FFF0F6'          # fondo principal
        self.pink_panel = '#FFD6E8'       # pestañas y paneles
        self.pink_accent = '#FFB6C1'      # botones al pasar mouse
        self.pink_button = '#FFE8F1'      # botones normales
        self.text_dark = '#2b2b2b'        # texto modo claro
        self.text_light = '#f6f6f6'       # texto modo oscuro
        
        # ===== COLORES (tema oscuro) =====
        self.dark_bg = '#2b2b35'          # fondo tema oscuro
        self.dark_panel = '#3a3942'       # paneles tema oscuro
        self.dark_accent = '#6f4a7a'      # acentos tema oscuro
        
        # Configura el fondo de la ventana
        root.configure(bg=self.pink_bg)
        
        # Crea el sistema de estilos de Tkinter
        self.style = ttk.Style()
        
        try:
            # Intenta usar el tema 'clam' que funciona bien en todas las plataformas
            self.style.theme_use('clam')
        except:
            # Si falla, usa el tema por defecto (sin problemas)
            pass
        
        # Define estilos personalizados para frames, labels, botones
        self.style.configure('Pink.TFrame', background=self.pink_bg)
        self.style.configure('Pink.TLabel', background=self.pink_bg, foreground=self.text_dark, font=('Segoe UI', 10))
        self.style.configure('PinkBold.TLabel', background=self.pink_bg, foreground=self.text_dark, font=('Segoe UI', 10, 'bold'))
        self.style.configure('Pink.TButton', background=self.pink_button, foreground=self.text_dark, borderwidth=0, focusthickness=3, padding=6)
        self.style.map('Pink.TButton', background=[('active', self.pink_accent)])
        self.style.configure('Pink.TNotebook', background=self.pink_bg)
        self.style.configure('Pink.TNotebook.Tab', background=self.pink_panel, padding=[10, 6], font=('Segoe UI', 9))
        self.style.map('Pink.TNotebook.Tab', background=[('selected', self.pink_accent)])
        
        # ===== MENÚ SUPERIOR =====
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='📁 Abrir imagen', command=self.open_image)
        filemenu.add_command(label='🖼️ Abrir segunda imagen', command=self.open_second_image)
        filemenu.add_command(label='💾 Guardar resultado', command=self.save_image)
        filemenu.add_separator()
        filemenu.add_command(label='❌ Salir', command=root.quit)
        menubar.add_cascade(label='Archivo', menu=filemenu)
        root.config(menu=menubar)
        
        # ===== LAYOUT PRINCIPAL =====
        # La ventana se divide en dos: izquierda (imagen grande) y derecha (controles)
        left = tk.Frame(root, bg=self.pink_bg)
        left.pack(side='left', fill='both', expand=True)
        right = tk.Frame(root, width=380, bg=self.pink_bg)
        right.pack(side='right', fill='y')
        
        # Canvas donde se muestra la imagen
        # Es un área negra donde dibujamos la foto
        self.canvas = tk.Canvas(left, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Barra de estado en la parte inferior
        # Muestra mensajes como "🖼️ Imagen abierta", "✨ Brillo aplicado", etc.

        # ===== PESTAÑAS (Notebook) =====
        # Sistema de tabs para organizar los controles
        notebook = ttk.Notebook(right, style='Pink.TNotebook')
        notebook.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Crea las 6 pestañas vacías
        file_tab = ttk.Frame(notebook, style='Pink.TFrame')
        adjust_tab = ttk.Frame(notebook, style='Pink.TFrame')
        geom_tab = ttk.Frame(notebook, style='Pink.TFrame')
        channels_tab = ttk.Frame(notebook, style='Pink.TFrame')
        fusion_tab = ttk.Frame(notebook, style='Pink.TFrame')
        hist_tab = ttk.Frame(notebook, style='Pink.TFrame')
        
        # Agrega las pestañas con sus etiquetas
        notebook.add(file_tab, text='📁 Archivo')
        notebook.add(adjust_tab, text='🎨 Ajustes')
        notebook.add(geom_tab, text='📐 Geometría')
        notebook.add(channels_tab, text='🧩 Canales / Color')
        notebook.add(fusion_tab, text='🔀 Fusión')
        notebook.add(hist_tab, text='📊 Histograma / Export')
        
        # ===== PESTAÑA: ARCHIVO =====
        ttk.Label(file_tab, text='📂 Controles de archivo', style='PinkBold.TLabel').pack(pady=6)
        ttk.Button(file_tab, text='📁 Abrir imagen', style='Pink.TButton', command=self.open_image).pack(fill='x', padx=6, pady=4)
        ttk.Button(file_tab, text='🖼️ Abrir segunda imagen', style='Pink.TButton', command=self.open_second_image).pack(fill='x', padx=6, pady=4)
        ttk.Button(file_tab, text='💾 Guardar resultado', style='Pink.TButton', command=self.save_image).pack(fill='x', padx=6, pady=4)
        ttk.Separator(file_tab).pack(fill='x', pady=8)
        ttk.Button(file_tab, text='🔁 Restaurar original', style='Pink.TButton', command=self.restore_original).pack(fill='x', padx=6, pady=4)
        ttk.Separator(file_tab).pack(fill='x', pady=6)
        
        
        # Cambio de tema
        self.mode_btn = ttk.Button(file_tab, text='🌙 Modo oscuro', style='Pink.TButton', command=self.toggle_mode)
        self.mode_btn.pack(fill='x', padx=6, pady=4)
        ttk.Separator(file_tab).pack(fill='x', pady=6)
        
        # Gestión de operaciones
        ttk.Button(file_tab, text='📋 Ver operaciones aplicadas', style='Pink.TButton', command=self.show_operations).pack(fill='x', padx=6, pady=4)
        ttk.Button(file_tab, text='↩️ Deshacer última operación', style='Pink.TButton', command=self.undo_last_operation).pack(fill='x', padx=6, pady=4)
        ttk.Button(file_tab, text='🗑️ Limpiar todas las operaciones', style='Pink.TButton', command=self.clear_operations).pack(fill='x', padx=6, pady=4)
        
        # ===== PESTAÑA: AJUSTES (Brillo y Contraste) =====
        ttk.Label(adjust_tab, text='🌈 Brillo y Contraste', style='PinkBold.TLabel').pack(pady=6)
        
        # Brillo global: un slider que suma/resta el mismo valor a todos los píxeles
        ttk.Label(adjust_tab, text='Brillo global (-255 a 255)', style='Pink.TLabel').pack()
        self.brightness_scale = tk.Scale(adjust_tab, from_=-255, to=255, orient='horizontal', bg=self.pink_bg, highlightthickness=0)
        self.brightness_scale.set(0)
        self.brightness_scale.pack(fill='x', padx=6)
        ttk.Button(adjust_tab, text='✨ Aplicar brillo', style='Pink.TButton', command=self.apply_brightness).pack(fill='x', padx=6, pady=6)
        
        # Brillo por canal: ajusta cada color (R, G, B) por separado
        ttk.Label(adjust_tab, text='🔴🟢🔵 Brillo por canal (R,G,B)', style='Pink.TLabel').pack(pady=(6,0))
        self.br_r = tk.Scale(adjust_tab, from_=-255, to=255, orient='horizontal', bg=self.pink_bg, highlightthickness=0)
        self.br_g = tk.Scale(adjust_tab, from_=-255, to=255, orient='horizontal', bg=self.pink_bg, highlightthickness=0)
        self.br_b = tk.Scale(adjust_tab, from_=-255, to=255, orient='horizontal', bg=self.pink_bg, highlightthickness=0)
        self.br_r.pack(fill='x', padx=6)
        self.br_g.pack(fill='x', padx=6)
        self.br_b.pack(fill='x', padx=6)
        ttk.Button(adjust_tab, text='✨ Aplicar brillo por canal', style='Pink.TButton', command=self.apply_brightness_channels).pack(fill='x', padx=6, pady=6)
        
        # Contraste logarítmico: usa logaritmos para mejorar detalles en sombras
        ttk.Label(adjust_tab, text='🔎 Contraste logarítmico (c)', style='Pink.TLabel').pack(pady=(6,0))
        self.log_c = tk.Entry(adjust_tab)
        self.log_c.insert(0, '1.0')
        self.log_c.pack(fill='x', padx=6)
        ttk.Button(adjust_tab, text='✨ Aplicar log', style='Pink.TButton', command=self.apply_log).pack(fill='x', padx=6, pady=6)
        
        # Gamma correction: aclara (gamma<1) u oscurece (gamma>1)
        ttk.Label(adjust_tab, text='⚡ Contraste exponencial / gamma', style='Pink.TLabel').pack(pady=(4,0))
        self.gamma_e = tk.Entry(adjust_tab)
        self.gamma_e.insert(0, '1.0')
        self.gamma_e.pack(fill='x', padx=6)
        ttk.Button(adjust_tab, text='✨ Aplicar gamma', style='Pink.TButton', command=self.apply_gamma).pack(fill='x', padx=6, pady=6)
        
        # ===== PESTAÑA: GEOMETRÍA =====
        ttk.Label(geom_tab, text='📐 Operaciones geométricas', style='PinkBold.TLabel').pack(pady=6)
        
        # Rotación: ingresa grados (positivo = sentido antihorario)
        ttk.Label(geom_tab, text='Rotación (grados)', style='Pink.TLabel').pack()
        self.rotate_entry = tk.Entry(geom_tab)
        self.rotate_entry.insert(0, '0')
        self.rotate_entry.pack(fill='x', padx=6)
        ttk.Button(geom_tab, text='🔁 Rotar', style='Pink.TButton', command=self.apply_rotate).pack(fill='x', padx=6, pady=6)
        
        # Recorte interactivo con mouse
        ttk.Button(geom_tab, text='✂️ Modo recorte (mouse)', style='Pink.TButton', command=self.toggle_crop_mode).pack(fill='x', padx=6, pady=6)
        self.crop_mode_label = ttk.Label(geom_tab, text='', style='Pink.TLabel')
        self.crop_mode_label.pack(pady=4)
        ttk.Button(geom_tab, text='✅ Aplicar recorte seleccionado', style='Pink.TButton', command=self.apply_crop_selected).pack(fill='x', padx=6, pady=6)
        
        # Zoom interactivo con mouse
        ttk.Button(geom_tab, text='🔍 Modo zoom (mouse)', style='Pink.TButton', command=self.toggle_zoom_mode).pack(fill='x', padx=6, pady=6)
        self.zoom_mode_label = ttk.Label(geom_tab, text='', style='Pink.TLabel')
        self.zoom_mode_label.pack(pady=4)
        
        # Zoom visual: solo para ver a diferentes escalas, no modifica la imagen
        ttk.Label(geom_tab, text='🔎 Zoom visual (solo visualizar)', style='Pink.TLabel').pack(pady=(6,0))
        self.visual_zoom = tk.Scale(geom_tab, from_=0.2, to=3.0, resolution=0.1, orient='horizontal', command=self.on_visual_zoom, sliderlength=14)
        self.visual_zoom.set(1.0)
        self.visual_zoom.pack(fill='x', padx=6, pady=(0,8))
        
        # ===== PESTAÑA: CANALES Y COLOR =====
        ttk.Label(channels_tab, text='🧩 Extracción y conversiones', style='PinkBold.TLabel').pack(pady=6)
        ttk.Button(channels_tab, text='🔴🟢🔵 Extraer R,G,B', style='Pink.TButton', command=self.extract_rgb).pack(fill='x', padx=6, pady=4)
        ttk.Button(channels_tab, text='🟦🟨🟩🖤 Extraer C,M,Y,K', style='Pink.TButton', command=self.extract_cmyk).pack(fill='x', padx=6, pady=4)
        ttk.Button(channels_tab, text='🪞 Negativo', style='Pink.TButton', command=self.apply_negative).pack(fill='x', padx=6, pady=4)
        ttk.Button(channels_tab, text='⚪ Convertir a grises', style='Pink.TButton', command=self.apply_gray).pack(fill='x', padx=6, pady=4)
        
        # Binarización: convierte a blanco y negro
        ttk.Label(channels_tab, text='⚫ Binarizar (umbral)', style='Pink.TLabel').pack(pady=(6,0))
        self.thresh_scale = tk.Scale(channels_tab, from_=0, to=255, orient='horizontal', bg=self.pink_bg, highlightthickness=0)
        self.thresh_scale.set(128)
        self.thresh_scale.pack(fill='x', padx=6)
        ttk.Button(channels_tab, text='⚫ Binarizar', style='Pink.TButton', command=self.apply_binarize).pack(fill='x', padx=6, pady=6)
        
        # ===== PESTAÑA: FUSIÓN =====
        ttk.Label(fusion_tab, text='🔀 Fusión de imágenes', style='PinkBold.TLabel').pack(pady=6)
        ttk.Label(fusion_tab, text='Alpha (0-1)', style='Pink.TLabel').pack()
        self.alpha_entry = tk.Entry(fusion_tab)
        self.alpha_entry.insert(0, '0.5')
        self.alpha_entry.pack(fill='x', padx=6)
        ttk.Button(fusion_tab, text='🔀 Fusionar', style='Pink.TButton', command=self.apply_fuse).pack(fill='x', padx=6, pady=6)
        ttk.Button(fusion_tab, text='✨ Fusionar ecualizadas', style='Pink.TButton', command=self.apply_fuse_eq).pack(fill='x', padx=6, pady=6)
        
        # ===== PESTAÑA: HISTOGRAMA =====
        ttk.Label(hist_tab, text='📊 Histograma', style='PinkBold.TLabel').pack(pady=6)
        ttk.Button(hist_tab, text='📈 Mostrar histograma', style='Pink.TButton', command=self.show_histogram).pack(fill='x', padx=6, pady=6)
        
        # Tamaño inicial de la ventana
        root.geometry('1200x760')
        root.bind('<Configure>', self.on_root_configure)

    # ===== MANEJO DE ARCHIVOS =====
    
    def open_image(self):
        # Abre diálogo de selección de archivo
        p = filedialog.askopenfilename(filetypes=[('Images', '*.png;*.jpg;*.jpeg;*.bmp;*.tiff')])
        if p:
            # Carga la imagen con la librería
            self.original = ip.load_image(p)
            # Comienza sin modificaciones
            self.img = self.original.copy()
            self.img_path = p
            # Limpia operaciones previas
            self.operations = []
            self.show_image(self.img)
            self.status.config(text=f'🖼️ Abierta: {os.path.basename(p)}')

    def open_second_image(self):
        # Para operaciones que necesitan dos imágenes (fusión)
        p = filedialog.askopenfilename(filetypes=[('Images', '*.png;*.jpg;*.jpeg;*.bmp;*.tiff')])
        if p:
            self.second_img = ip.load_image(p)
            self.status.config(text=f'🖼️ Segunda imagen: {os.path.basename(p)}')

    def save_image(self):
        # Guarda la imagen con todas las operaciones aplicadas
        if self.img is None:
            messagebox.showwarning('Aviso', 'No hay imagen para guardar')
            return
        p = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG', '*.png'), ('JPEG', '*.jpg')])
        if p:
            ip.save_image(self.img, p)
            self.status.config(text=f'💾 Guardada: {os.path.basename(p)}')

    def restore_original(self):
        # Vuelve a la imagen original sin ninguna operación
        if self.original is None:
            messagebox.showinfo('Restaurar', 'No hay imagen original')
            return
        self.operations = []
        self.img = self.original.copy()
        self.show_image(self.img)
        self.status.config(text='🔁 Restaurado a original')

    # ===== VISUALIZACIÓN =====
    
    def show_image(self, img):
        # Redimensiona la imagen para que quepa en el canvas manteniendo aspecto
        if img is None:
            return
        w, h = img.size
        canv_w = max(200, int(self.canvas.winfo_width() or 800))
        canv_h = max(200, int(self.canvas.winfo_height() or 600))
        
        # Calcula escala para que quepa pero sin distorsionar
        scale = self.display_scale * min(1.0, canv_w / w, canv_h / h)
        
        # Si necesita redimensionarse, usa LANCZOS (mejor calidad)
        if scale < 1.0 or abs(scale - 1.0) > 1e-6:
            disp = img.resize((max(1, int(w*scale)), max(1, int(h*scale))), Image.LANCZOS)
        else:
            disp = img.copy()
        
        # Convierte PIL a formato Tkinter y la dibuja
        self.img_tk = ImageTk.PhotoImage(disp)
        self.canvas.delete('all')
        self.canvas.create_image(0, 0, anchor='nw', image=self.img_tk)

    def on_visual_zoom(self, val):
        # El slider de zoom solo cambia cómo se visualiza, no modifica la imagen
        try:
            self.display_scale = float(val)
            if self.img:
                self.show_image(self.img)
        except:
            pass

    def on_root_configure(self, event):
        # Cada vez que se redimensiona la ventana, redibujar la imagen
        if self.img:
            self.show_image(self.img)

    # ===== TRANSFORMACIONES (Sistema de operaciones) =====
    
    def apply_brightness(self):
        # Brillo: obtiene valor del slider, elimina brillo anterior si existe,
        # agrega el nuevo y recalcula todas las operaciones
        if not self.original:
            return
        val = self.brightness_scale.get()
        # Reemplaza brillo anterior si lo hay
        self.operations = [op for op in self.operations if op[0] != 'brightness']
        self.operations.append(('brightness', {'value': val}))
        self.apply_operations()
        self.status.config(text=f'✨ Brillo: {val}')

    def apply_brightness_channels(self):
        # Similar pero para cada canal por separado
        if not self.original:
            return
        r, g, b = self.br_r.get(), self.br_g.get(), self.br_b.get()
        self.operations = [op for op in self.operations if op[0] != 'brightness_channels']
        self.operations.append(('brightness_channels', {'r': r, 'g': g, 'b': b}))
        self.apply_operations()
        self.status.config(text=f'✨ Brillo RGB: {r},{g},{b}')

    def apply_log(self):
        # Contraste logarítmico
        if not self.original:
            return
        try:
            c = float(self.log_c.get())
        except:
            c = 1.0
        self.operations = [op for op in self.operations if op[0] != 'log']
        self.operations.append(('log', {'c': c}))
        self.apply_operations()
        self.status.config(text=f'🔎 Log c={c}')

    def apply_gamma(self):
        # Gamma correction / contraste exponencial
        if not self.original:
            return
        try:
            g = float(self.gamma_e.get())
        except:
            g = 1.0
        self.operations = [op for op in self.operations if op[0] != 'gamma']
        self.operations.append(('gamma', {'gamma': g}))
        self.apply_operations()
        self.status.config(text=f'⚡ Gamma={g}')

    def apply_rotate(self):
        # Rotación en grados
        if not self.original:
            return
        try:
            ang = float(self.rotate_entry.get())
        except:
            ang = 0
        self.operations = [op for op in self.operations if op[0] != 'rotate']
        self.operations.append(('rotate', {'angle': ang}))
        self.apply_operations()
        self.status.config(text=f'🔁 Rotado {ang}°')

    # ===== RECORTE INTERACTIVO (con mouse) =====
    
    def toggle_crop_mode(self):
        # Activa/desactiva el modo recorte interactivo
        if not self.img:
            return
        self.crop_mode = not self.crop_mode
        
        if self.crop_mode:
            # Activa modo: muestra instrucción y vincula eventos del mouse
            self.crop_mode_label.config(text='🖱️ Arrastra para recortar', foreground='red')
            self.canvas.config(cursor='crosshair')
            self.canvas.bind('<Button-1>', self.on_crop_start)
            self.canvas.bind('<B1-Motion>', self.on_crop_drag)
            self.canvas.bind('<ButtonRelease-1>', self.on_crop_end)
        else:
            # Desactiva modo: limpia todo
            self.crop_mode_label.config(text='')
            self.canvas.config(cursor='arrow')
            self.canvas.unbind('<Button-1>')
            self.canvas.unbind('<B1-Motion>')
            self.canvas.unbind('<ButtonRelease-1>')
            self.crop_start = None
            self.crop_end = None
            if self.crop_rect:
                self.canvas.delete(self.crop_rect)
                self.crop_rect = None
            self.show_image(self.img)

    def on_crop_start(self, event):
        # Marca el punto inicial del arrastre
        self.crop_start = (event.x, event.y)

    def on_crop_drag(self, event):
        # Dibuja un rectángulo punteado mientras se arrastra
        # Lo borra y redibuja cada movimiento para dar sensación fluida
        self.crop_end = (event.x, event.y)
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        
        x1, y1 = self.crop_start
        x2, y2 = self.crop_end
        
        # Rectángulo punteado rojo = vista previa del recorte
        self.crop_rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline='red',
            width=2,
            dash=(4, 4)
        )

    def on_crop_end(self, event):
        # Guarda punto final y avisa que confirme el recorte
        self.crop_end = (event.x, event.y)
        self.crop_mode_label.config(text='📌 Presiona el botón "Aplicar recorte" para confirmar', foreground='blue')

    def apply_crop_selected(self):
        # Convierte las coordenadas del canvas (visualización) a coordenadas de imagen (original)
        # porque el canvas puede estar ampliado/reducido por zoom visual
        if self.crop_start is None or self.crop_end is None:
            messagebox.showwarning('Aviso', 'Primero haz el recorte con el mouse')
            return
        
        # Obtiene tamaño de la imagen original
        w, h = self.original.size
        canv_w = self.canvas.winfo_width()
        canv_h = self.canvas.winfo_height()
        
        # Calcula el factor de escala usado en visualización
        scale = self.display_scale * min(1.0, canv_w / w, canv_h / h)
        
        # Convierte coordenadas canvas → imagen real
        x1 = int(self.crop_start[0] / scale)
        y1 = int(self.crop_start[1] / scale)
        x2 = int(self.crop_end[0] / scale)
        y2 = int(self.crop_end[1] / scale)
        
        # Asegura orden correcto (left < right, top < bottom)
        box = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        
        # Agrega a operaciones (reemplaza recorte anterior si existe)
        self.operations = [op for op in self.operations if op[0] != 'crop']
        self.operations.append(('crop', {'box': box}))
        self.apply_operations()
        
        # Desactiva modo recorte
        self.toggle_crop_mode()
        self.status.config(text='✂️ Recortado')

    # ===== ZOOM INTERACTIVO (con mouse) =====
    
    def toggle_zoom_mode(self):
        # Activa/desactiva el modo zoom interactivo
        if not self.img:
            return
        self.zoom_mode = not self.zoom_mode
        
        if self.zoom_mode:
            # Activa modo: cursor cambia a cruz, vincula eventos
            self.zoom_mode_label.config(text='🔍 Click para zoom | Doble click para deshacer', foreground='green')
            self.canvas.config(cursor='crosshair')
            self.canvas.bind('<Button-1>', self.on_zoom_click)
            self.canvas.bind('<Double-Button-1>', self.on_zoom_undo)
        else:
            # Desactiva modo
            self.zoom_mode_label.config(text='')
            self.canvas.config(cursor='arrow')
            self.canvas.unbind('<Button-1>')
            self.canvas.unbind('<Double-Button-1>')
            self.zoom_point = None

    def on_zoom_click(self, event):
        # Click simple: planea aplicar zoom después de un pequeño delay
        # (para evitar confundir con doble click)
        if event.num == 1 and not self._is_double_click(event):
            self.root.after(200, lambda: self._apply_zoom_at_point(event.x, event.y))

    def _is_double_click(self, event):
        # Los dobles clicks se manejan en on_zoom_undo(), no aquí
        return False

    def _apply_zoom_at_point(self, canv_x, canv_y):
        # Solo cambia el display_scale, no modifica la imagen
        if not self.crop_mode and self.zoom_mode:
            # Aumenta el zoom visual 2x
            self.display_scale *= self.zoom_factor
            self.show_image(self.img)
            self.zoom_mode_label.config(text='🔍 Zoom aplicado | Doble click para deshacer', foreground='blue')
            self.status.config(text='🔍 Zoom aplicado')

    def on_zoom_undo(self, event):
        # Doble click vuelve al zoom normal (1.0)
        self.display_scale = 1.0
        self.show_image(self.img)
        self.zoom_mode_label.config(text='🔍 Click para zoom | Doble click para deshacer', foreground='green')
        self.status.config(text='↩️ Zoom deshecho')

    # ===== TRANSFORMACIONES: CANALES Y COLOR =====
    
    def apply_negative(self):
        # Invierte todos los colores
        if not self.original:
            return
        self.operations = [op for op in self.operations if op[0] != 'negative']
        self.operations.append(('negative', {}))
        self.apply_operations()
        self.status.config(text='🪞 Negativo')

    def apply_gray(self):
        # Convierte a escala de grises
        if not self.original:
            return
        self.operations = [op for op in self.operations if op[0] != 'gray']
        self.operations.append(('gray', {}))
        self.apply_operations()
        self.status.config(text='⚪ Grises')

    def apply_binarize(self):
        # Convierte a blanco y negro puro (umbral ajustable)
        if not self.original:
            return
        t = self.thresh_scale.get()
        self.operations = [op for op in self.operations if op[0] != 'binarize']
        self.operations.append(('binarize', {'threshold': t}))
        self.apply_operations()
        self.status.config(text=f'⚫ Binarizado umbral={t}')

    # ===== TRANSFORMACIONES: FUSIÓN =====
    
    def apply_fuse(self):
        # Mezcla dos imágenes: imagen1*alpha + imagen2*(1-alpha)
        if not self.original or not self.second_img:
            messagebox.showwarning('Aviso', 'Abra ambas imágenes')
            return
        try:
            a = float(self.alpha_entry.get())
        except:
            a = 0.5
        self.operations = [op for op in self.operations if op[0] != 'fuse']
        self.operations.append(('fuse', {'alpha': a}))
        self.apply_operations()
        self.status.config(text=f'🔀 Fusión alpha={a}')

    def apply_fuse_eq(self):
        # Mezcla pero primero iguala histogramas (mejor resultado si hay diferencias de luz)
        if not self.original or not self.second_img:
            messagebox.showwarning('Aviso', 'Abra ambas imágenes')
            return
        try:
            a = float(self.alpha_entry.get())
        except:
            a = 0.5
        self.operations = [op for op in self.operations if op[0] != 'fuse_eq']
        self.operations.append(('fuse_eq', {'alpha': a}))
        self.apply_operations()
        self.status.config(text=f'✨ Fusión ecualizada alpha={a}')

    # ===== ANÁLISIS: HISTOGRAMA =====
    
    def show_histogram(self):
        # Abre ventana con gráfico del histograma RGB
        if not self.img:
            return
        r, g, b = ip.histogram(self.img)
        
        # Crea figura de matplotlib
        fig = plt.Figure(figsize=(5, 3))
        ax = fig.add_subplot(111)
        
        # Dibuja tres líneas (una por cada canal)
        ax.plot(r, label='R', color='red')
        ax.plot(g, label='G', color='green')
        ax.plot(b, label='B', color='blue')
        ax.set_title('📊 Histograma')
        ax.legend()
        
        # Crea ventana nueva para mostrar el gráfico
        win = tk.Toplevel(self.root)
        win.title('📊 Histograma')
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        canvas.draw()

    # ===== EXTRACCIÓN DE CANALES =====
    
    def extract_rgb(self):
        # Muestra los canales R, G, B por separado en ventana nueva
        # Cada uno tintado con su color real
        if not self.img:
            return
        r, g, b = ip.extract_rgb_layers(self.img)
        
        win = tk.Toplevel(self.root)
        win.title('🔴🟢🔵 Canales R, G, B')
        
        # Dibuja los 3 canales lado a lado
        for idx, ch in enumerate((r, g, b), start=1):
            w = tk.Canvas(win, width=220, height=200, bg='black', highlightthickness=0)
            w.grid(row=0, column=idx-1, padx=6, pady=6)
            img_disp = ch.convert('RGB')
            photo = ImageTk.PhotoImage(img_disp.resize((220, 200), Image.LANCZOS))
            w.image = photo  # Guarda referencia para evitar que el garbage collector lo borre
            w.create_image(0, 0, anchor='nw', image=photo)
        
        self.status.config(text='🔎 RGB mostrados')

    def extract_cmyk(self):
        # Similar a RGB pero muestra canales CMYK
        if not self.img:
            return
        c, m, y, k = ip.extract_cmyk_layers(self.img)
        
        win = tk.Toplevel(self.root)
        win.title('🟦🟨🟩🖤 Canales C, M, Y, K')
        
        # Dibuja los 4 canales
        for idx, ch in enumerate((c, m, y, k)):
            w = tk.Canvas(win, width=220, height=200, bg='black', highlightthickness=0)
            w.grid(row=0, column=idx, padx=6, pady=6)
            img_disp = ImageTk.PhotoImage(ch.resize((220, 200), Image.LANCZOS))
            w.image = img_disp
            w.create_image(0, 0, anchor='nw', image=img_disp)
        
        self.status.config(text='🔎 CMYK mostrados')


    # ===== GESTIÓN DE OPERACIONES =====
    
    def apply_operations(self):
        # Recalcula la imagen desde cero aplicando TODAS las operaciones en orden
        # Esta es la clave del sistema: no acumula efectos, siempre parte de original
        if self.original is None:
            return
        
        result = self.original.copy()
        
        # Aplica cada operación guardada en secuencia
        for op_type, params in self.operations:
            if op_type == 'brightness':
                result = ip.adjust_brightness_global(result, params['value'])
            elif op_type == 'brightness_channels':
                result = ip.adjust_brightness_channel(result, params['r'], params['g'], params['b'])
            elif op_type == 'log':
                result = ip.contrast_logarithmic(result, params['c'])
            elif op_type == 'gamma':
                result = ip.contrast_exponential(result, params['gamma'])
            elif op_type == 'rotate':
                result = ip.rotate_image(result, params['angle'])
            elif op_type == 'crop':
                result = ip.crop_image(result, params['box'])
            elif op_type == 'zoom':
                result = ip.zoom_image(result, params['box'], params['scale'])
            elif op_type == 'negative':
                result = ip.negative(result)
            elif op_type == 'gray':
                result = ip.to_grayscale(result).convert('RGB')
            elif op_type == 'binarize':
                result = ip.binarize(result, threshold=params['threshold']).convert('RGB')
            elif op_type == 'fuse':
                result = ip.fuse_images(result, self.second_img, alpha=params['alpha'])
            elif op_type == 'fuse_eq':
                result = ip.fuse_equalized(result, self.second_img, alpha=params['alpha'])
        
        # Guarda resultado y muestra
        self.img = result
        self.show_image(self.img)

    def undo_last_operation(self):
        # Elimina la última operación de la lista
        if not self.operations:
            messagebox.showinfo('Deshacer', 'No hay operaciones para deshacer')
            return
        
        removed = self.operations.pop()
        self.apply_operations()
        self.status.config(text=f'↩️ Deshecha: {removed[0]}')

    def show_operations(self):
        # Muestra ventana con todas las operaciones activas
        if not self.operations:
            messagebox.showinfo('Operaciones', 'No hay operaciones aplicadas')
            return
        
        msg = '📋 Operaciones aplicadas:\n\n'
        for i, (op_type, params) in enumerate(self.operations, 1):
            msg += f'{i}. {op_type}: {params}\n'
        messagebox.showinfo('Operaciones', msg)

    def clear_operations(self):
        # Limpia todas las operaciones (vuelve a imagen original)
        if not self.operations:
            messagebox.showinfo('Limpiar', 'No hay operaciones')
            return
        
        self.operations = []
        self.img = self.original.copy()
        self.show_image(self.img)
        self.status.config(text='🗑️ Todas las operaciones eliminadas')

    # ===== TEMA: CLARO/OSCURO =====
    
    def toggle_mode(self):
        # Alterna entre tema claro (rosa) y oscuro
        current = self.root.cget('bg')
        
        if current == self.pink_bg:
            # Cambiar a oscuro
            self.root.configure(bg=self.dark_bg)
            self.canvas.configure(bg=self.dark_panel)
            self.status.configure(bg=self.dark_panel, fg=self.text_light)
            self.style.configure('Pink.TFrame', background=self.dark_bg)
            self.style.configure('Pink.TLabel', background=self.dark_bg, foreground=self.text_light)
            self.style.configure('PinkBold.TLabel', background=self.dark_bg, foreground=self.text_light)
            self.style.configure('Pink.TNotebook.Tab', background=self.dark_panel)
            self.mode_btn.config(text='☀️ Modo claro')
            self.status.config(text='🌙 Modo oscuro')
        else:
            # Cambiar a claro
            self.root.configure(bg=self.pink_bg)
            self.canvas.configure(bg='black')
            self.status.configure(bg=self.pink_button, fg=self.text_dark)
            self.style.configure('Pink.TFrame', background=self.pink_bg)
            self.style.configure('Pink.TLabel', background=self.pink_bg, foreground=self.text_dark)
            self.style.configure('PinkBold.TLabel', background=self.pink_bg, foreground=self.text_dark)
            self.style.configure('Pink.TNotebook.Tab', background=self.pink_panel)
            self.mode_btn.config(text='🌙 Modo oscuro')
            self.status.config(text='✨ Modo claro')


if __name__ == '__main__':
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()
