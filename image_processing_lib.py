"""
Libreria: image_processing_lib.py
Funciones de procesamiento de imagenes usadas por la GUI.
Dependencias: Pillow (PIL), numpy
Instalacion: pip install pillow numpy
"""

from PIL import Image, ImageOps, ImageEnhance
import numpy as np

# ========== UTILIDADES BÁSICAS ==========
# Estas funciones convierten entre formatos PIL y NumPy,
# ya que PIL es mejor para I/O pero NumPy para cálculos

def load_image(path):
    # Abre el archivo y lo convierte a RGB para asegurar consistencia
    # (algunas imágenes pueden estar en RGBA, modo indexado, etc.)
    img = Image.open(path).convert('RGB')
    return img

def save_image(img, path):
    # Simple: guarda la imagen PIL tal como está
    img.save(path)

def pil_to_np(img):
    # Convierte PIL a array NumPy en punto flotante para operaciones matemáticas
    # Lo dejamos en 32 bits para evitar desbordamientos en cálculos intermedios
    return np.array(img).astype(np.float32)

def np_to_pil(arr):
    # Convierte NumPy de vuelta a PIL
    # Limita valores entre 0-255 y los convierte a enteros (rango válido para imágenes)
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

# ========== AJUSTES DE BRILLO Y CONTRASTE ==========

def adjust_brightness_global(img, value):
    # Suma/resta el mismo valor a todos los píxeles
    # Es lo más simple: brillo +50 significa +50 a cada canal (R, G, B)
    a = pil_to_np(img)
    a += value
    return np_to_pil(a)

def adjust_brightness_channel(img, r=0, g=0, b=0):
    # Permite ajustar cada color por separado
    # Útil para correcciones de color: si la foto está muy roja, baja el canal R
    a = pil_to_np(img)
    a[..., 0] += r  # Canal rojo
    a[..., 1] += g  # Canal verde
    a[..., 2] += b  # Canal azul
    return np_to_pil(a)

def contrast_logarithmic(img, c=1.0):
    # Usa logaritmos para comprimir rangos dinámicos
    # Mantiene detalles en áreas oscuras sin quemar las claras
    # c = intensidad del efecto (valores mayores = más efecto)
    a = pil_to_np(img)
    a = c * np.log1p(a)  # log1p = log(1 + x) para evitar log(0)
    
    # Normaliza el resultado de vuelta al rango 0-255
    a = a / np.log1p(255) * 255
    return np_to_pil(a)

def contrast_exponential(img, gamma=1.0):
    # Aplicación clásica de gamma correction
    # gamma < 1 aclara (levanta las sombras)
    # gamma > 1 oscurece (aprieta los tonos)
    # Muy usado en procesamiento de video
    a = pil_to_np(img) / 255.0  # Normaliza a 0.0-1.0 para el cálculo
    a = 255.0 * (a ** gamma)    # Aplica la potencia
    return np_to_pil(a)

# ========== OPERACIONES GEOMÉTRICAS ==========

def crop_image(img, box):
    # Recorta usando coordenadas (left, upper, right, lower)
    # PIL.crop() es muy eficiente, no copia datos innecesarios
    return img.crop(box)

def zoom_image(img, box, scale=2):
    # Recorta la región especificada y luego la amplía
    # Por ejemplo: recorta un área pequeña y la hace 2x más grande
    cropped = img.crop(box)
    w, h = cropped.size
    # LANCZOS es el mejor interpolador disponible en PIL
    # (conserva bordes y detalles mejor que BILINEAR)
    return cropped.resize((int(w*scale), int(h*scale)), Image.LANCZOS)

def rotate_image(img, angle, expand=True):
    # Rota la imagen por los grados especificados
    # expand=True hace que la canvas se agrande si es necesario (no corta la imagen)
    return img.rotate(angle, expand=expand)

# ========== ANÁLISIS DE IMÁGENES ==========

def histogram(img):
    # Calcula la distribución de valores para cada canal
    # Útil para ver si una foto está subexpuesta, sobreexpuesta, etc.
    a = np.array(img.convert('RGB'))
    
    # np.histogram divide los 256 valores posibles (0-255) en bins
    # y cuenta cuántos píxeles caen en cada rango
    r = np.histogram(a[..., 0], bins=256, range=(0, 255))[0]
    g = np.histogram(a[..., 1], bins=256, range=(0, 255))[0]
    b = np.histogram(a[..., 2], bins=256, range=(0, 255))[0]
    return r, g, b

# ========== FUSIÓN DE IMÁGENES ==========

def fuse_images(img1, img2, alpha=0.5):
    # Mezcla dos imágenes: resultado = img1*alpha + img2*(1-alpha)
    # alpha=1 → 100% primera imagen
    # alpha=0.5 → mezcla al 50%
    # alpha=0 → 100% segunda imagen
    
    # Primero las convierte a RGBA para asegurar que tengan canal alpha
    i1 = img1.convert('RGBA')
    i2 = img2.convert('RGBA')
    
    # Las redimensiona al tamaño menor (para que no haya problemas de tamaño)
    w = min(i1.width, i2.width)
    h = min(i1.height, i2.height)
    i1s = i1.resize((w, h), Image.LANCZOS)
    i2s = i2.resize((w, h), Image.LANCZOS)
    
    # Convierte a arrays NumPy (RGB, descartando alpha si lo hay)
    arr1 = pil_to_np(i1s.convert('RGB'))
    arr2 = pil_to_np(i2s.convert('RGB'))
    
    # Hace el blending por interpolación lineal
    fused = arr1 * alpha + arr2 * (1 - alpha)
    return np_to_pil(fused)

def equalize_histogram(img):
    # Expande el rango de tonos para usar mejor el espectro disponible
    # Mejora el contraste sin cambiar colores demasiado
    
    # Usa YCbCr en lugar de RGB porque así afecta solo la luminancia (Y)
    # y preserva la información de color (Cb, Cr)
    ycb = img.convert('YCbCr')
    y, cb, cr = ycb.split()
    
    # Ecualiza solo el canal Y (brillo)
    y_eq = ImageOps.equalize(y)
    
    # Reconstruye la imagen con Y ecualizado pero Cb,Cr sin cambios
    ycb_eq = Image.merge('YCbCr', (y_eq, cb, cr))
    return ycb_eq.convert('RGB')

def fuse_equalized(img1, img2, alpha=0.5):
    # Primero iguala los histogramas de ambas imágenes
    # Luego las mezcla
    # Útil cuando una foto está más clara/oscura que la otra
    # así el resultado se ve más natural
    e1 = equalize_histogram(img1)
    e2 = equalize_histogram(img2)
    return fuse_images(e1, e2, alpha)

# ========== EXTRACCIÓN DE CANALES ==========

def extract_rgb_layers(img):
    # Separa la imagen en sus componentes R, G, B
    # Pero los devuelve tintados (rojo puro para R, verde puro para G, etc.)
    # así se ven más claros en la visualización
    img = img.convert('RGB')
    r, g, b = img.split()
    
    # Tinta cada canal con su color real
    # Por ejemplo: canal rojo = rojo puro + nada verde + nada azul
    red = Image.merge("RGB", (r, Image.new("L", r.size, 0), Image.new("L", r.size, 0)))
    green = Image.merge("RGB", (Image.new("L", g.size, 0), g, Image.new("L", g.size, 0)))
    blue = Image.merge("RGB", (Image.new("L", b.size, 0), Image.new("L", b.size, 0), b))
    
    return red, green, blue

def extract_cmyk_layers(img):
    # Similar a RGB pero usando CMYK (usado en imprenta)
    # C=Cyan, M=Magenta, Y=Yellow, K=Black
    cmyk = img.convert('CMYK')
    c, m, y, k = cmyk.split()
    
    # Devuelve cada canal tintado con su color real (aproximado)
    cyan = Image.merge("RGB", (Image.new("L", c.size, 0), c, c))
    magenta = Image.merge("RGB", (m, Image.new("L", m.size, 0), m))
    yellow = Image.merge("RGB", (y, y, Image.new("L", y.size, 0)))
    black = Image.merge("RGB", (k, k, k))
    
    return cyan, magenta, yellow, black

# ========== CONVERSIONES Y TRANSFORMACIONES SIMPLES ==========

def negative(img):
    # Invierte todos los valores: 255 → 0, 128 → 127, etc.
    # Usa ImageOps.invert() de PIL que es muy eficiente
    return ImageOps.invert(img.convert('RGB'))

def to_grayscale(img):
    # Convierte a escala de grises
    # PIL usa la fórmula estándar (Y = 0.299*R + 0.587*G + 0.114*B)
    return img.convert('L')

def binarize(img, threshold=128):
    # Convierte a blanco y negro puro
    # Cualquier píxel >= umbral → blanco (255)
    # Cualquier píxel < umbral → negro (0)
    gray = img.convert('L')
    arr = np.array(gray)
    
    # Array booleano: True (1) si >= threshold, False (0) si no
    # Multiplica por 255 para obtener 0 o 255
    bw = (arr >= threshold) * 255
    
    return Image.fromarray(bw.astype(np.uint8))
