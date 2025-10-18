# 🌸 – Manual de Usuario

## Descripción General

**Image Studio** es una aplicación de procesamiento de imágenes con interfaz gráfica intuitiva. Permite aplicar múltiples transformaciones a imágenes de forma interactiva, viendo los cambios en tiempo real.

### Características principales:
- ✨ Ajustes de brillo y contraste
- 📐 Operaciones geométricas (rotación, recorte, zoom)
- 🧩 Manipulación de canales de color
- 🔀 Fusión de imágenes
- 📊 Visualización de histogramas
- 🎞️ Modo presentación
- 🌙 Tema claro/oscuro
- **Múltiples transformaciones simultáneas** sin acumulación de efectos

---

## Instalación

### Requisitos:
- Python 3.7 o superior
- Tkinter (incluido en la mayoría de instalaciones de Python)

### Dependencias:
```bash
pip install pillow numpy matplotlib
```

### Estructura de archivos:
```
project/
├── image_processing_lib.py
├── main_gui.py
└── (tus imágenes)
```

### Ejecutar:
```bash
python main_gui.py
```

---

## Interfaz Principal

La ventana se divide en dos áreas:

**Izquierda:** Canvas donde se visualiza la imagen (con zoom visual ajustable)
**Derecha:** Panel de controles organizado en 6 pestañas

```
┌─────────────────────────────────┬──────────────┐
│                                 │   📁 Archivo │
│                                 │   🎨 Ajustes │
│          IMAGEN                 │   📐 Geometría
│          (Canvas)               │   🧩 Canales │
│                                 │   🔀 Fusión  │
│                                 │   📊 Histogr.│
└─────────────────────────────────┴──────────────┘
```

---

## Funcionamiento del Sistema de Operaciones

### ⚡ Concepto clave: Operaciones sin acumulación

A diferencia de editores tradicionales, **cada transformación siempre parte de la imagen original**, no de la anterior.

**Ejemplo:**
1. Cargas una imagen
2. Aplicas Brillo +50 → se guarda como operación
3. Aplicas Gamma 1.5 → se agrega a la lista
4. Cambias Brillo a +30 → se **reemplaza** la operación anterior (no se suma)
5. Resultado final = Original + Brillo(+30) + Gamma(1.5)

Si cambiaras Brillo de +30 a +100, automáticamente se recalcula todo desde cero.

### 📋 Gestión de operaciones

- **Una sola instancia por tipo:** No puedes tener dos "Brillo" activos. Al aplicar uno nuevo, reemplaza el anterior.
- **Orden de ejecución:** Las operaciones se aplican en el orden que las agregaste.
- **Ver operaciones:** Botón "📋 Ver operaciones aplicadas" muestra la lista completa.
- **Deshacer última:** Botón "↩️ Deshacer última operación" elimina la última que agregaste.
- **Limpiar todo:** Botón "🗑️ Limpiar todas las operaciones" vuelve a la imagen original.
- **Restaurar original:** Limpia todo y vuelve al estado inicial (sin cerrar la imagen).

---

## Pestañas y Controles

### 📁 Archivo
- **📁 Abrir imagen:** Carga una imagen (PNG, JPG, BMP, TIFF)
- **🖼️ Abrir segunda imagen:** Carga otra imagen para fusión
- **💾 Guardar resultado:** Exporta la imagen con todas las transformaciones aplicadas
- **🔁 Restaurar original:** Borra todas las operaciones
- **↩️ Deshacer última operación:** Elimina la última transformación
- **📋 Ver operaciones aplicadas:** Muestra lista de transformaciones activas
- **🗑️ Limpiar todas las operaciones:** Vuelve a imagen original
- **🎞️ Iniciar presentación:** Cicla entre imágenes cargadas
- **🌙 Modo oscuro:** Alterna tema claro/oscuro

### 🎨 Ajustes
**Brillo Global (-255 a 255):**
- Slider para ajustar brillo general
- Valores positivos = más claro
- Valores negativos = más oscuro

**Brillo por canal (R, G, B):**
- Ajusta independientemente cada canal de color
- Útil para correcciones de color

**Contraste Logarítmico:**
- Parámetro `c` (valores > 0)
- Comprime rangos dinámicos

**Contraste Exponencial / Gamma:**
- `gamma < 1` = aclara imagen
- `gamma > 1` = oscurece imagen

### 📐 Geometría

**Rotación:**
- Ingresa ángulos en grados (ej: 45, -90, 180)

**Recorte con Mouse 🖱️:**
1. Click en "✂️ Modo recorte (mouse)"
2. Cursor cambia a cruz
3. Arrastra en la imagen → aparece rectángulo rojo punteado
4. Suelta → instrucción para confirmar
5. Click en "✅ Aplicar recorte seleccionado"
6. El recorte se aplica

**Recorte Manual:**
- Ingresa coordenadas: `left,upper,right,lower`
- Ejemplo: `100,50,400,300`

**Zoom con Mouse 🔍:**
1. Click en "🔍 Modo zoom (mouse)"
2. **Click simple:** Aplica zoom 2x centrado en ese punto
3. **Doble click:** Deshace el zoom
4. Click nuevamente para desactivar modo

**Zoom Visual (solo visualización):**
- Slider para ver la imagen a diferentes escalas
- No modifica la imagen, solo la visualización

### 🧩 Canales / Color

- **🔴🟢🔵 Extraer R,G,B:** Abre ventana mostrando canales por separado
- **🟦🟨🟩🖤 Extraer C,M,Y,K:** Muestra canales CMYK (Cyan, Magenta, Yellow, Black)
- **🪞 Negativo:** Invierte todos los colores
- **⚪ Convertir a grises:** Convierte a escala de grises
- **⚫ Binarizar:** Convierte a blanco y negro con umbral ajustable (0-255)

### 🔀 Fusión

Fusiona dos imágenes cargadas:

- **Alpha (0-1):** 
  - 0 = solo segunda imagen
  - 0.5 = mezcla al 50%
  - 1 = solo primera imagen

- **🔀 Fusionar:** Mezcla simple por blending
- **✨ Fusionar ecualizadas:** Iguala histogramas antes de mezclar (mejor resultado en imágenes con diferentes iluminaciones)

### 📊 Histograma / Export

- **📈 Mostrar histograma:** Abre gráfico con distribución de valores RGB

---

## Ejemplo de Uso Completo

### Escenario: Mejorar foto oscura

1. **Abrir imagen:**
   - Click "📁 Abrir imagen"
   - Selecciona `foto_oscura.jpg`

2. **Ajustar brillo:**
   - Pestaña "🎨 Ajustes"
   - Slider "Brillo global" → +80
   - Click "✨ Aplicar brillo"
   - ✅ Se ve más clara

3. **Aumentar contraste:**
   - "⚡ Contraste exponencial"
   - Ingresa Gamma: `0.8`
   - Click "✨ Aplicar gamma"
   - ✅ Mejora detalles oscuros

4. **Rotar si es necesario:**
   - Pestaña "📐 Geometría"
   - Rotación: `-90` (rotar 90° contrareloj)
   - Click "🔁 Rotar"
   - ✅ Imagen orientada correctamente

5. **Recortar área interesante:**
   - Click "✂️ Modo recorte (mouse)"
   - Arrastra rectángulo alrededor del sujeto principal
   - Click "✅ Aplicar recorte seleccionado"
   - ✅ Imagen enfocada

6. **Ver operaciones:**
   - Click "📋 Ver operaciones aplicadas"
   - Ves: Brillo, Gamma, Rotación, Recorte

7. **Guardar resultado:**
   - Click "💾 Guardar resultado"
   - Selecciona ubicación: `foto_mejorada.png`
   - ✅ Guardada con todos los cambios

8. **Si quieres deshacer algo:**
   - Click "↩️ Deshacer última operación" (elimina recorte)
   - Recorte desaparece, pero brillo + gamma siguen

---

## Ejemplo 2: Fusión de dos imágenes

1. **Cargar primera imagen:**
   - "📁 Abrir imagen" → `paisaje.jpg`

2. **Cargar segunda imagen:**
   - "🖼️ Abrir segunda imagen" → `efecto.png`

3. **Ir a pestaña "🔀 Fusión"**

4. **Ajustar alpha:**
   - Ingresa: `0.6` (60% primera imagen, 40% segunda)

5. **Click "🔀 Fusionar"**
   - ✅ Se mezclan ambas imágenes

6. **Opcional - Ecualizadas:**
   - Si una está más clara que otra, usa "✨ Fusionar ecualizadas"

---

## Atajos y Tips

### 🎯 Consejos útiles:

1. **Orden de operaciones importa:**
   - Recorta antes de aplicar efectos (más rápido)
   - Ajusta colores antes de binarizar

2. **Usar "Ver operaciones" frecuentemente:**
   - Evita acumular transformaciones innecesarias

3. **Zoom visual para ver detalles:**
   - Usa el slider de zoom antes de operaciones precisas

4. **Guardar en diferentes formatos:**
   - PNG = mejor calidad, archivo más grande
   - JPG = comprimido, archivo pequeño, pérdida leve

5. **Deshacer vs Limpiar:**
   - "Deshacer última" = quita solo la última operación
   - "Limpiar todas" = vuelve completamente al original

### ⚡ Atajos de mouse:

| Acción | Efecto |
|--------|--------|
| Click en "Modo recorte" + arrastrar | Dibuja rectángulo de recorte |
| Click en "Modo zoom" + click | Aplica zoom 2x |
| Click en "Modo zoom" + doble click | Deshace zoom |
| Slider "Zoom visual" | Solo visualización (no modifica) |

---

## Requisitos de Sistema

- **OS:** Windows, macOS, Linux
- **RAM:** 512 MB (1 GB recomendado)
- **Formatos soportados:** PNG, JPG, JPEG, BMP, TIFF
- **Resolución mínima:** 800x600 (1200x760 recomendado)

---

## Solución de Problemas

### ❌ "Error: tkinter no está disponible"
**Solución:**
- **Linux (Debian/Ubuntu):** `sudo apt-get install python3-tk`
- **Windows:** Reinstala Python y marca la opción "Tcl/Tk"
- **macOS:** Instala desde `python.org` o usa Homebrew

### ❌ Imagen se ve pixelada
**Solución:** Usa "Zoom visual" para ver en escala 1:1 real

### ❌ Operaciones se ven "acumuladas"
**Solución:** Esto es normal. Cada operación recalcula desde la original. Si ves cambios raros, usa "↩️ Deshacer última operación"

### ❌ Recorte no funciona con mouse
**Solución:** Asegúrate de hacer click en "✂️ Modo recorte" primero y confirmar con "✅ Aplicar recorte"

---

## Más Información

- **Autores:** Sarasvati Dallos Velez, Yeison Betancur Delgado
- **Versión:** 1.0
- **Licencia:** Open Source
- **Dependencias:** Pillow, NumPy, Matplotlib, Tkinter
