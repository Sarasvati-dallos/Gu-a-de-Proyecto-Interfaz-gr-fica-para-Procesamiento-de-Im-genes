"""
Libreria: image_processing_lib.py
Funciones de procesamiento de imagenes usadas por la GUI.
Dependencias: Pillow (PIL), numpy
Instalacion: pip install pillow numpy
"""

from PIL import Image, ImageOps, ImageEnhance
import numpy as np

# ---------- Utilities ----------

def load_image(path):
    """Carga una imagen y la devuelve en modo RGB (PIL Image)."""
    img = Image.open(path).convert('RGB')
    return img


def save_image(img, path):
    """Guarda una imagen PIL en disco."""
    img.save(path)


def pil_to_np(img):
    return np.array(img).astype(np.float32)


def np_to_pil(arr):
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

# ---------- Transformaciones ----------

def adjust_brightness_global(img, value):
    """value: int o float, suma a cada canal (positivo aumenta, negativo disminuye)"""
    a = pil_to_np(img)
    a += value
    return np_to_pil(a)


def adjust_brightness_channel(img, r=0, g=0, b=0):
    a = pil_to_np(img)
    a[...,0] += r
    a[...,1] += g
    a[...,2] += b
    return np_to_pil(a)


def contrast_logarithmic(img, c=1.0):
    """Aplicacion de contraste logaritmico: c * log(1 + I)
    c controla la intensidad (float>0)
    """
    a = pil_to_np(img)
    a = c * np.log1p(a)
    # normalizar a rango 0-255
    a = a / np.log1p(255) * 255
    return np_to_pil(a)


def contrast_exponential(img, gamma=1.0):
    """Contraste exponencial / gamma correction.
    gamma <1 aclarar, gamma>1 oscurecer.
    """
    a = pil_to_np(img) / 255.0
    a = 255.0 * (a ** gamma)
    return np_to_pil(a)


def crop_image(img, box):
    """box = (left, upper, right, lower)"""
    return img.crop(box)


def zoom_image(img, box, scale=2):
    """Recorta el area box y la escala por 'scale'"""
    cropped = img.crop(box)
    w,h = cropped.size
    return cropped.resize((int(w*scale), int(h*scale)), Image.LANCZOS)


def rotate_image(img, angle, expand=True):
    return img.rotate(angle, expand=expand)


def histogram(img):
    """Devuelve histograma por canal como arrays (r,g,b)."""
    a = np.array(img.convert('RGB'))
    r = np.histogram(a[...,0], bins=256, range=(0,255))[0]
    g = np.histogram(a[...,1], bins=256, range=(0,255))[0]
    b = np.histogram(a[...,2], bins=256, range=(0,255))[0]
    return r, g, b


def fuse_images(img1, img2, alpha=0.5):
    """Fusion simple por alpha (img1*alpha + img2*(1-alpha)).
    Las imagenes se redimensionan al tamaño comun (el menor)."""
    # Convertir a RGB
    i1 = img1.convert('RGBA')
    i2 = img2.convert('RGBA')
    # redimensionar al menor
    w = min(i1.width, i2.width)
    h = min(i1.height, i2.height)
    i1s = i1.resize((w,h), Image.LANCZOS)
    i2s = i2.resize((w,h), Image.LANCZOS)
    arr1 = pil_to_np(i1s.convert('RGB'))
    arr2 = pil_to_np(i2s.convert('RGB'))
    fused = arr1 * alpha + arr2 * (1 - alpha)
    return np_to_pil(fused)


def equalize_histogram(img):
    """Ecualizacion global usando PIL (por canal)."""
    # Convertir a YCbCr y ecualizar la componente Y para preservar color
    ycb = img.convert('YCbCr')
    y, cb, cr = ycb.split()
    y_eq = ImageOps.equalize(y)
    ycb_eq = Image.merge('YCbCr', (y_eq, cb, cr))
    return ycb_eq.convert('RGB')


def fuse_equalized(img1, img2, alpha=0.5):
    e1 = equalize_histogram(img1)
    e2 = equalize_histogram(img2)
    return fuse_images(e1, e2, alpha)


def extract_rgb_layers(img):
    """Extrae las capas RGB y las devuelve tintadas con su color real."""
    img = img.convert('RGB')
    r, g, b = img.split()

    red = Image.merge("RGB", (r, Image.new("L", r.size, 0), Image.new("L", r.size, 0)))
    green = Image.merge("RGB", (Image.new("L", g.size, 0), g, Image.new("L", g.size, 0)))
    blue = Image.merge("RGB", (Image.new("L", b.size, 0), Image.new("L", b.size, 0), b))

    return red, green, blue



def extract_cmyk_layers(img):
    """Convierte a CMYK y devuelve las capas tintadas (C, M, Y, K)."""
    cmyk = img.convert('CMYK')
    c, m, y, k = cmyk.split()

    cyan = Image.merge("RGB", (Image.new("L", c.size, 0), c, c))
    magenta = Image.merge("RGB", (m, Image.new("L", m.size, 0), m))
    yellow = Image.merge("RGB", (y, y, Image.new("L", y.size, 0)))
    black = Image.merge("RGB", (k, k, k))

    return cyan, magenta, yellow, black


def negative(img):
    return ImageOps.invert(img.convert('RGB'))


def to_grayscale(img):
    return img.convert('L')


def binarize(img, threshold=128):
    gray = img.convert('L')
    arr = np.array(gray)
    bw = (arr >= threshold) * 255
    return Image.fromarray(bw.astype(np.uint8))