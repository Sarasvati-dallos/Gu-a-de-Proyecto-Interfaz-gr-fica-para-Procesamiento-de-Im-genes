"""
🌸 Image Studio – Procesamiento de Imágenes
Interfaz gráfica usando Tkinter con pestañas.

CAMBIO IMPORTANTE:
- Cada transformación parte de la imagen ORIGINAL
- Se crea una copia y se modifica
- Si aplico otro cambio DIFERENTE, vuelvo a partir de la original
- Esto evita acumulación de cambios
"""

import sys
import os
from PIL import Image, ImageTk
import image_processing_lib as ip
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except Exception as e:
    print('Error: tkinter no está disponible')
    sys.exit(1)


class ImageApp:
    def __init__(self, root):
        self.root = root
        root.title('🌸 Image Studio – Procesamiento de Imágenes')
        
        # Estado
        self.original = None          # imagen original (nunca se modifica)
        self.img = None               # imagen actual a mostrar
        self.img_tk = None
        self.img_path = None
        self.second_img = None
        self.last_operation = None    # tipo de última operación aplicada
        
        self.display_scale = 1.0
        self.presentation_running = False
        self.presentation_interval_ms = 2000
        self.presentation_items = []
        self.presentation_index = 0

        # Estilos
        self.pink_bg = '#FFF0F6'
        self.pink_panel = '#FFD6E8'
        self.pink_accent = '#FFB6C1'
        self.pink_button = '#FFE8F1'
        self.text_dark = '#2b2b2b'
        self.text_light = '#f6f6f6'
        self.dark_bg = '#2b2b35'
        self.dark_panel = '#3a3942'
        self.dark_accent = '#6f4a7a'
        self.crop_mode = False
        self.crop_start = None
        self.crop_end = None
        self.crop_rect = None
        self.zoom_mode = False
        self.zoom_point = None
        self.zoom_factor = 2.0  # factor de zoom (puede ajustarse)

        self.operations = []  # Lista de (tipo, parámetros)


        
        root.configure(bg=self.pink_bg)
        self.style = ttk.Style()
        
        try:
            self.style.theme_use('clam')
        except:
            pass

        self.style.configure('Pink.TFrame', background=self.pink_bg)
        self.style.configure('Pink.TLabel', background=self.pink_bg, foreground=self.text_dark, font=('Segoe UI', 10))
        self.style.configure('PinkBold.TLabel', background=self.pink_bg, foreground=self.text_dark, font=('Segoe UI', 10, 'bold'))
        self.style.configure('Pink.TButton', background=self.pink_button, foreground=self.text_dark, borderwidth=0, focusthickness=3, padding=6)
        self.style.map('Pink.TButton', background=[('active', self.pink_accent)])
        self.style.configure('Pink.TNotebook', background=self.pink_bg)
        self.style.configure('Pink.TNotebook.Tab', background=self.pink_panel, padding=[10, 6], font=('Segoe UI', 9))
        self.style.map('Pink.TNotebook.Tab', background=[('selected', self.pink_accent)])

        # Menú
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='📁 Abrir imagen', command=self.open_image)
        filemenu.add_command(label='🖼️ Abrir segunda imagen', command=self.open_second_image)
        filemenu.add_command(label='💾 Guardar resultado', command=self.save_image)
        filemenu.add_separator()
        filemenu.add_command(label='❌ Salir', command=root.quit)
        menubar.add_cascade(label='Archivo', menu=filemenu)
        root.config(menu=menubar)

        # Layout principal
        left = tk.Frame(root, bg=self.pink_bg)
        left.pack(side='left', fill='both', expand=True)
        right = tk.Frame(root, width=380, bg=self.pink_bg)
        right.pack(side='right', fill='y')

        self.canvas = tk.Canvas(left, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        self.status = tk.Label(root, text='✨ Listo', bd=1, relief='sunken', anchor='w', bg=self.pink_button)
        self.status.pack(side='bottom', fill='x')

        # Notebook (pestañas)
        notebook = ttk.Notebook(right, style='Pink.TNotebook')
        notebook.pack(fill='both', expand=True, padx=8, pady=8)

        file_tab = ttk.Frame(notebook, style='Pink.TFrame')
        adjust_tab = ttk.Frame(notebook, style='Pink.TFrame')
        geom_tab = ttk.Frame(notebook, style='Pink.TFrame')
        channels_tab = ttk.Frame(notebook, style='Pink.TFrame')
        fusion_tab = ttk.Frame(notebook, style='Pink.TFrame')
        hist_tab = ttk.Frame(notebook, style='Pink.TFrame')

        notebook.add(file_tab, text='📁 Archivo')
        notebook.add(adjust_tab, text='🎨 Ajustes')
        notebook.add(geom_tab, text='📐 Geometría')
        notebook.add(channels_tab, text='🧩 Canales / Color')
        notebook.add(fusion_tab, text='🔀 Fusión')
        notebook.add(hist_tab, text='📊 Histograma / Export')

        # --- File Tab ---
        ttk.Label(file_tab, text='📂 Controles de archivo', style='PinkBold.TLabel').pack(pady=6)
        ttk.Button(file_tab, text='📁 Abrir imagen', style='Pink.TButton', command=self.open_image).pack(fill='x', padx=6, pady=4)
        ttk.Button(file_tab, text='🖼️ Abrir segunda imagen', style='Pink.TButton', command=self.open_second_image).pack(fill='x', padx=6, pady=4)
        ttk.Button(file_tab, text='💾 Guardar resultado', style='Pink.TButton', command=self.save_image).pack(fill='x', padx=6, pady=4)
        ttk.Separator(file_tab).pack(fill='x', pady=8)
        ttk.Button(file_tab, text='🔁 Restaurar original', style='Pink.TButton', command=self.restore_original).pack(fill='x', padx=6, pady=4)
        ttk.Separator(file_tab).pack(fill='x', pady=6)
        pres_frame = ttk.Frame(file_tab, style='Pink.TFrame')
        pres_frame.pack(fill='x', padx=6)
        self.pres_btn = ttk.Button(pres_frame, text='🎞️ Iniciar presentación', style='Pink.TButton', command=self.toggle_presentation)
        self.pres_btn.pack(side='left', fill='x', expand=True, pady=4)
        ttk.Separator(file_tab).pack(fill='x', pady=6)
        self.mode_btn = ttk.Button(file_tab, text='🌙 Modo oscuro', style='Pink.TButton', command=self.toggle_mode)
        self.mode_btn.pack(fill='x', padx=6, pady=4)
        ttk.Separator(file_tab).pack(fill='x', pady=6)
        ttk.Button(file_tab, text='📋 Ver operaciones aplicadas', style='Pink.TButton', command=self.show_operations).pack(fill='x', padx=6, pady=4)
        ttk.Button(file_tab, text='↩️ Deshacer última operación', style='Pink.TButton', command=self.undo_last_operation).pack(fill='x', padx=6, pady=4)
        ttk.Button(file_tab, text='🗑️ Limpiar todas las operaciones', style='Pink.TButton', command=self.clear_operations).pack(fill='x', padx=6, pady=4)

        # --- Adjust Tab ---
        ttk.Label(adjust_tab, text='🌈 Brillo y Contraste', style='PinkBold.TLabel').pack(pady=6)
        ttk.Label(adjust_tab, text='Brillo global (-255 a 255)', style='Pink.TLabel').pack()
        self.brightness_scale = tk.Scale(adjust_tab, from_=-255, to=255, orient='horizontal', bg=self.pink_bg, highlightthickness=0)
        self.brightness_scale.set(0)
        self.brightness_scale.pack(fill='x', padx=6)
        ttk.Button(adjust_tab, text='✨ Aplicar brillo', style='Pink.TButton', command=self.apply_brightness).pack(fill='x', padx=6, pady=6)

        ttk.Label(adjust_tab, text='🔴🟢🔵 Brillo por canal (R,G,B)', style='Pink.TLabel').pack(pady=(6,0))
        self.br_r = tk.Scale(adjust_tab, from_=-255, to=255, orient='horizontal', bg=self.pink_bg, highlightthickness=0)
        self.br_g = tk.Scale(adjust_tab, from_=-255, to=255, orient='horizontal', bg=self.pink_bg, highlightthickness=0)
        self.br_b = tk.Scale(adjust_tab, from_=-255, to=255, orient='horizontal', bg=self.pink_bg, highlightthickness=0)
        self.br_r.pack(fill='x', padx=6)
        self.br_g.pack(fill='x', padx=6)
        self.br_b.pack(fill='x', padx=6)
        ttk.Button(adjust_tab, text='✨ Aplicar brillo por canal', style='Pink.TButton', command=self.apply_brightness_channels).pack(fill='x', padx=6, pady=6)

        ttk.Label(adjust_tab, text='🔎 Contraste logarítmico (c)', style='Pink.TLabel').pack(pady=(6,0))
        self.log_c = tk.Entry(adjust_tab); self.log_c.insert(0,'1.0'); self.log_c.pack(fill='x', padx=6)
        ttk.Button(adjust_tab, text='✨ Aplicar log', style='Pink.TButton', command=self.apply_log).pack(fill='x', padx=6, pady=6)

        ttk.Label(adjust_tab, text='⚡ Contraste exponencial / gamma', style='Pink.TLabel').pack(pady=(4,0))
        self.gamma_e = tk.Entry(adjust_tab); self.gamma_e.insert(0,'1.0'); self.gamma_e.pack(fill='x', padx=6)
        ttk.Button(adjust_tab, text='✨ Aplicar gamma', style='Pink.TButton', command=self.apply_gamma).pack(fill='x', padx=6, pady=6)

        # --- Geometría Tab ---
        ttk.Label(geom_tab, text='📐 Operaciones geométricas', style='PinkBold.TLabel').pack(pady=6)
        ttk.Label(geom_tab, text='Rotación (grados)', style='Pink.TLabel').pack()
        self.rotate_entry = tk.Entry(geom_tab); self.rotate_entry.insert(0,'0'); self.rotate_entry.pack(fill='x', padx=6)
        ttk.Button(geom_tab, text='🔁 Rotar', style='Pink.TButton', command=self.apply_rotate).pack(fill='x', padx=6, pady=6)


        ttk.Button(geom_tab, text='✂️ Modo recorte (mouse)', style='Pink.TButton', command=self.toggle_crop_mode).pack(fill='x', padx=6, pady=6)
        self.crop_mode_label = ttk.Label(geom_tab, text='', style='Pink.TLabel')
        self.crop_mode_label.pack(pady=4)

        ttk.Button(geom_tab, text='✅ Aplicar recorte seleccionado', style='Pink.TButton', command=self.apply_crop_selected).pack(fill='x', padx=6, pady=6)


        ttk.Button(geom_tab, text='🔍 Modo zoom (mouse)', style='Pink.TButton', command=self.toggle_zoom_mode).pack(fill='x', padx=6, pady=6)
        self.zoom_mode_label = ttk.Label(geom_tab, text='', style='Pink.TLabel')
        self.zoom_mode_label.pack(pady=4)

        ttk.Label(geom_tab, text='🔎 Zoom visual (solo visualizar)', style='Pink.TLabel').pack(pady=(6,0))
        self.visual_zoom = tk.Scale(geom_tab, from_=0.2, to=3.0, resolution=0.1, orient='horizontal', command=self.on_visual_zoom, sliderlength=14)
        self.visual_zoom.set(1.0)
        self.visual_zoom.pack(fill='x', padx=6, pady=(0,8))

        # --- Canales Tab ---
        ttk.Label(channels_tab, text='🧩 Extracción y conversiones', style='PinkBold.TLabel').pack(pady=6)
        ttk.Button(channels_tab, text='🔴🟢🔵 Extraer R,G,B', style='Pink.TButton', command=self.extract_rgb).pack(fill='x', padx=6, pady=4)
        ttk.Button(channels_tab, text='🟦🟨🟩🖤 Extraer C,M,Y,K', style='Pink.TButton', command=self.extract_cmyk).pack(fill='x', padx=6, pady=4)
        ttk.Button(channels_tab, text='🪞 Negativo', style='Pink.TButton', command=self.apply_negative).pack(fill='x', padx=6, pady=4)
        ttk.Button(channels_tab, text='⚪ Convertir a grises', style='Pink.TButton', command=self.apply_gray).pack(fill='x', padx=6, pady=4)

        ttk.Label(channels_tab, text='⚫ Binarizar (umbral)', style='Pink.TLabel').pack(pady=(6,0))
        self.thresh_scale = tk.Scale(channels_tab, from_=0, to=255, orient='horizontal', bg=self.pink_bg, highlightthickness=0)
        self.thresh_scale.set(128)
        self.thresh_scale.pack(fill='x', padx=6)
        ttk.Button(channels_tab, text='⚫ Binarizar', style='Pink.TButton', command=self.apply_binarize).pack(fill='x', padx=6, pady=6)

        # --- Fusión Tab ---
        ttk.Label(fusion_tab, text='🔀 Fusión de imágenes', style='PinkBold.TLabel').pack(pady=6)
        ttk.Label(fusion_tab, text='Alpha (0-1)', style='Pink.TLabel').pack()
        self.alpha_entry = tk.Entry(fusion_tab); self.alpha_entry.insert(0,'0.5'); self.alpha_entry.pack(fill='x', padx=6)
        ttk.Button(fusion_tab, text='🔀 Fusionar', style='Pink.TButton', command=self.apply_fuse).pack(fill='x', padx=6, pady=6)
        ttk.Button(fusion_tab, text='✨ Fusionar ecualizadas', style='Pink.TButton', command=self.apply_fuse_eq).pack(fill='x', padx=6, pady=6)

        # --- Histograma Tab ---
        ttk.Label(hist_tab, text='📊 Histograma', style='PinkBold.TLabel').pack(pady=6)
        ttk.Button(hist_tab, text='📈 Mostrar histograma', style='Pink.TButton', command=self.show_histogram).pack(fill='x', padx=6, pady=6)

        root.geometry('1200x760')
        root.bind('<Configure>', self.on_root_configure)

    # --- Helpers ---
    def open_image(self):
        p = filedialog.askopenfilename(filetypes=[('Images','*.png;*.jpg;*.jpeg;*.bmp;*.tiff')])
        if p:
            self.original = ip.load_image(p)
            self.img = self.original.copy()
            self.img_path = p
            self.last_operation = None
            self.show_image(self.img)
            self.status.config(text=f'🖼️ Abierta: {os.path.basename(p)}')
            if self.img not in self.presentation_items:
                self.presentation_items.append(self.img)

    def open_second_image(self):
        p = filedialog.askopenfilename(filetypes=[('Images','*.png;*.jpg;*.jpeg;*.bmp;*.tiff')])
        if p:
            self.second_img = ip.load_image(p)
            self.status.config(text=f'🖼️ Segunda imagen: {os.path.basename(p)}')

    def save_image(self):
        if self.img is None:
            messagebox.showwarning('Aviso','No hay imagen para guardar')
            return
        p = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG','*.png'),('JPEG','*.jpg')])
        if p:
            ip.save_image(self.img, p)
            self.status.config(text=f'💾 Guardada: {os.path.basename(p)}')

    def restore_original(self):
        if self.original is None:
            messagebox.showinfo('Restaurar','No hay imagen original')
            return
        self.operations = []
        self.img = self.original.copy()
        self.show_image(self.img)
        self.status.config(text='🔁 Restaurado a original')

    def show_image(self, img):
        if img is None:
            return
        w, h = img.size
        canv_w = max(200, int(self.canvas.winfo_width() or 800))
        canv_h = max(200, int(self.canvas.winfo_height() or 600))
        scale = self.display_scale * min(1.0, canv_w / w, canv_h / h)
        if scale < 1.0 or abs(scale - 1.0) > 1e-6:
            disp = img.resize((max(1, int(w*scale)), max(1, int(h*scale))), Image.LANCZOS)
        else:
            disp = img.copy()
        self.img_tk = ImageTk.PhotoImage(disp)
        self.canvas.delete('all')
        self.canvas.create_image(0, 0, anchor='nw', image=self.img_tk)

    def on_visual_zoom(self, val):
        try:
            self.display_scale = float(val)
            if self.img:
                self.show_image(self.img)
        except:
            pass

    def on_root_configure(self, event):
        if self.img:
            self.show_image(self.img)

    # --- Transformaciones ---
    def apply_brightness(self):
        if not self.original:
            return
        val = self.brightness_scale.get()
        self.operations = [op for op in self.operations if op[0] != 'brightness']
        self.operations.append(('brightness', {'value': val}))
        self.apply_operations()
        self.status.config(text=f'✨ Brillo: {val}')

    def apply_brightness_channels(self):
        if not self.original:
            return
        r, g, b = self.br_r.get(), self.br_g.get(), self.br_b.get()
        self.operations = [op for op in self.operations if op[0] != 'brightness_channels']
        self.operations.append(('brightness_channels', {'r': r, 'g': g, 'b': b}))
        self.apply_operations()
        self.status.config(text=f'✨ Brillo RGB: {r},{g},{b}')

    def apply_log(self):
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

    def toggle_crop_mode(self):
        if not self.img:
            return
        self.crop_mode = not self.crop_mode
        if self.crop_mode:
            self.crop_mode_label.config(text='🖱️ Arrastra para recortar', foreground='red')
            self.canvas.config(cursor='crosshair')
            self.canvas.bind('<Button-1>', self.on_crop_start)
            self.canvas.bind('<B1-Motion>', self.on_crop_drag)
            self.canvas.bind('<ButtonRelease-1>', self.on_crop_end)
        else:
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
        # Convierte coordenadas del canvas a coordenadas de imagen
        self.crop_start = (event.x, event.y)

    def on_crop_drag(self, event):
        # Dibuja el rectángulo mientras arrastra
        self.crop_end = (event.x, event.y)
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)

        x1, y1 = self.crop_start
        x2, y2 = self.crop_end

        # Dibuja rectángulo punteado rojo
        self.crop_rect = self.canvas.create_rectangle(
            x1, y1, x2, y2, 
            outline='red', 
            width=2, 
            dash=(4, 4)
        )

    def on_crop_end(self, event):
        # Guarda el punto final cuando suelta el mouse
        self.crop_end = (event.x, event.y)
        self.crop_mode_label.config(text='📌 Presiona el botón "Aplicar recorte" para confirmar', foreground='blue')

    def apply_crop_selected(self):
        if self.crop_start is None or self.crop_end is None:
            messagebox.showwarning('Aviso', 'Primero haz el recorte con el mouse')
            return
    
        # Escala las coordenadas del canvas a la imagen original
        w, h = self.original.size
        canv_w = self.canvas.winfo_width()
        canv_h = self.canvas.winfo_height()
        scale = self.display_scale * min(1.0, canv_w / w, canv_h / h)
    
        x1 = int(self.crop_start[0] / scale)
        y1 = int(self.crop_start[1] / scale)
        x2 = int(self.crop_end[0] / scale)
        y2 = int(self.crop_end[1] / scale)
    
        # Asegura que left < right, top < bottom
        box = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
    
        # Agrega la operación a la lista
        self.operations = [op for op in self.operations if op[0] != 'crop']
        self.operations.append(('crop', {'box': box}))
        self.apply_operations()
        
        self.toggle_crop_mode()  # Desactiva modo recorte
        self.status.config(text=f'✂️ Recortado')

    def toggle_zoom_mode(self):
        if not self.img:
            return
        self.zoom_mode = not self.zoom_mode
        if self.zoom_mode:
            self.zoom_mode_label.config(text='🔍 Click para zoom | Doble click para deshacer', foreground='green')
            self.canvas.config(cursor='crosshair')
            self.canvas.bind('<Button-1>', self.on_zoom_click)
            self.canvas.bind('<Double-Button-1>', self.on_zoom_undo)
        else:
            self.zoom_mode_label.config(text='')
            self.canvas.config(cursor='arrow')
            self.canvas.unbind('<Button-1>')
            self.canvas.unbind('<Double-Button-1>')
            self.zoom_point = None

    def on_zoom_click(self, event):
        if event.num == 1 and not self._is_double_click(event):
            # Espera un poco para ver si es doble click
            self.root.after(200, lambda: self._apply_zoom_at_point(event.x, event.y))

    def _is_double_click(self, event):
        # Se maneja con el evento Double-Button-1
        return False

    def _apply_zoom_at_point(self, canv_x, canv_y):
        if not self.crop_mode and self.zoom_mode:
            # Convierte coordenadas canvas a coordenadas de imagen
            w, h = self.original.size
            canv_w = self.canvas.winfo_width()
            canv_h = self.canvas.winfo_height()
            scale = self.display_scale * min(1.0, canv_w / w, canv_h / h)

            img_x = int(canv_x / scale)
            img_y = int(canv_y / scale)

            # Calcula el área a recortar (centrada en el punto de click)
            zoom_w = w / self.zoom_factor
            zoom_h = h / self.zoom_factor

            left = max(0, int(img_x - zoom_w / 2))
            top = max(0, int(img_y - zoom_h / 2))
            right = min(w, int(left + zoom_w))
            bottom = min(h, int(top + zoom_h))

            # Ajusta si se sale del límite
            if right - left < zoom_w:
                left = max(0, int(right - zoom_w))
            if bottom - top < zoom_h:
                top = max(0, int(bottom - zoom_h))

            box = (left, top, right, bottom)
            self.img = ip.crop_image(self.original.copy(), box)
            self.last_operation = 'zoom_click'
            self.show_image(self.img)
            self.zoom_mode_label.config(text='🔍 Zoom aplicado | Doble click para deshacer', foreground='blue')
            self.status.config(text='🔍 Zoom aplicado')

    def on_zoom_undo(self, event):
        # Doble click deshace el zoom
        self.img = self.original.copy()
        self.last_operation = None
        self.show_image(self.img)
        self.zoom_mode_label.config(text='🔍 Click para zoom | Doble click para deshacer', foreground='green')
        self.status.config(text='↩️ Zoom deshecho')

    def apply_negative(self):
        if not self.original:
            return
        self.operations = [op for op in self.operations if op[0] != 'negative']
        self.operations.append(('negative', {}))
        self.apply_operations()
        self.status.config(text='🪞 Negativo')

    def apply_gray(self):
        if not self.original:
            return
        self.operations = [op for op in self.operations if op[0] != 'gray']
        self.operations.append(('gray', {}))
        self.apply_operations()
        self.status.config(text='⚪ Grises')

    def apply_binarize(self):
        if not self.original:
            return
        t = self.thresh_scale.get()
        self.operations = [op for op in self.operations if op[0] != 'binarize']
        self.operations.append(('binarize', {'threshold': t}))
        self.apply_operations()
        self.status.config(text=f'⚫ Binarizado umbral={t}')

    def apply_fuse(self):
        if not self.original or not self.second_img:
            messagebox.showwarning('Aviso','Abra ambas imágenes')
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
        if not self.original or not self.second_img:
            messagebox.showwarning('Aviso','Abra ambas imágenes')
            return
        try:
            a = float(self.alpha_entry.get())
        except:
            a = 0.5
        self.operations = [op for op in self.operations if op[0] != 'fuse_eq']
        self.operations.append(('fuse_eq', {'alpha': a}))
        self.apply_operations()
        self.status.config(text=f'✨ Fusión ecualizada alpha={a}')

    def show_histogram(self):
        if not self.img:
            return
        r, g, b = ip.histogram(self.img)
        fig = plt.Figure(figsize=(5, 3))
        ax = fig.add_subplot(111)
        ax.plot(r, label='R', color='red')
        ax.plot(g, label='G', color='green')
        ax.plot(b, label='B', color='blue')
        ax.set_title('📊 Histograma')
        ax.legend()
        win = tk.Toplevel(self.root)
        win.title('📊 Histograma')
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        canvas.draw()

    def extract_rgb(self):
        if not self.img:
            return
        r, g, b = ip.extract_rgb_layers(self.img)
        win = tk.Toplevel(self.root)
        win.title('🔴🟢🔵 Canales R, G, B')
        for idx, ch in enumerate((r, g, b), start=1):
            w = tk.Canvas(win, width=220, height=200, bg='black', highlightthickness=0)
            w.grid(row=0, column=idx-1, padx=6, pady=6)
            img_disp = ch.convert('RGB')
            photo = ImageTk.PhotoImage(img_disp.resize((220, 200), Image.LANCZOS))
            w.image = photo
            w.create_image(0, 0, anchor='nw', image=photo)
        self.status.config(text='🔎 RGB mostrados')

    def extract_cmyk(self):
        if not self.img:
            return
        c, m, y, k = ip.extract_cmyk_layers(self.img)
        win = tk.Toplevel(self.root)
        win.title('🟦🟨🟩🖤 Canales C, M, Y, K')
        for idx, ch in enumerate((c, m, y, k)):
            w = tk.Canvas(win, width=220, height=200, bg='black', highlightthickness=0)
            w.grid(row=0, column=idx, padx=6, pady=6)
            img_disp = ImageTk.PhotoImage(ch.resize((220, 200), Image.LANCZOS))
            w.image = img_disp
            w.create_image(0, 0, anchor='nw', image=img_disp)
        self.status.config(text='🔎 CMYK mostrados')

    # --- Presentación ---
    def add_current_to_presentation(self):
        if self.img and self.img not in self.presentation_items:
            self.presentation_items.append(self.img)
            self.status.config(text='🎞️ Añadida a presentación')

    def toggle_presentation(self):
        if not self.presentation_running:
            if not self.presentation_items:
                messagebox.showinfo('Presentación','No hay imágenes')
                return
            self.presentation_running = True
            self.pres_btn.config(text='⏸️ Pausar')
            self.presentation_index = 0
            self._run_presentation()
            self.status.config(text='🎞️ Presentación iniciada')
        else:
            self.presentation_running = False
            self.pres_btn.config(text='🎞️ Iniciar')
            self.status.config(text='⏸️ Pausada')

    def _run_presentation(self):
        if not self.presentation_running or not self.presentation_items:
            return
        item = self.presentation_items[self.presentation_index % len(self.presentation_items)]
        self.img = item.copy()
        self.show_image(self.img)
        self.presentation_index += 1
        self.root.after(self.presentation_interval_ms, self._run_presentation)

    def undo_last_operation(self):
        if not self.operations:
            messagebox.showinfo('Deshacer', 'No hay operaciones para deshacer')
            return
        
        # Elimina la última operación
        removed = self.operations.pop()
        self.apply_operations()
        self.status.config(text=f'↩️ Deshecha: {removed[0]}')

    # --- Modo Oscuro/Claro ---
    def toggle_mode(self):
        current = self.root.cget('bg')
        if current == self.pink_bg:
            # Modo oscuro
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
            # Modo claro
            self.root.configure(bg=self.pink_bg)
            self.canvas.configure(bg='black')
            self.status.configure(bg=self.pink_button, fg=self.text_dark)
            self.style.configure('Pink.TFrame', background=self.pink_bg)
            self.style.configure('Pink.TLabel', background=self.pink_bg, foreground=self.text_dark)
            self.style.configure('PinkBold.TLabel', background=self.pink_bg, foreground=self.text_dark)
            self.style.configure('Pink.TNotebook.Tab', background=self.pink_panel)
            self.mode_btn.config(text='🌙 Modo oscuro')
            self.status.config(text='✨ Modo claro')
    
    def apply_operations(self):
        """Recalcula la imagen aplicando todas las operaciones en orden"""
        if self.original is None:
            return

        result = self.original.copy()

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

        self.img = result
        self.show_image(self.img)

    def show_operations(self):
        if not self.operations:
            messagebox.showinfo('Operaciones', 'No hay operaciones aplicadas')
            return

        msg = '📋 Operaciones aplicadas:\n\n'
        for i, (op_type, params) in enumerate(self.operations, 1):
            msg += f'{i}. {op_type}: {params}\n'

        messagebox.showinfo('Operaciones', msg)

    def clear_operations(self):
        if not self.operations:
            messagebox.showinfo('Limpiar', 'No hay operaciones')
            return

        self.operations = []
        self.img = self.original.copy()
        self.show_image(self.img)
        self.status.config(text='🗑️ Todas las operaciones eliminadas')


if __name__ == '__main__':
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()