# WebM to MP4 Converter

Programa para Windows que convierte archivos de video WebM a MP4 usando FFmpeg.

![Renombrador](https://github.com/fabiomb/WebMToMP4/blob/main/img/webmtomp4.png)

## Características

- ✅ Exploración de carpetas para identificar archivos WebM
- ✅ Visualización de archivos con nombre, extensión, tamaño y fecha
- ✅ Selección individual o múltiple de archivos
- ✅ Validación automática de dimensiones (píxeles pares)
- ✅ Conversión con FFmpeg
- ✅ Barra de progreso y log detallado
- ✅ Log colapsable para ver/ocultar detalles
- ✅ Interfaz gráfica intuitiva con Tkinter

## Requisitos previos

### FFmpeg

Este programa requiere que **FFmpeg** esté instalado y disponible en el PATH del sistema.

#### Instalación de FFmpeg en Windows:

1. **Opción A - Usando Chocolatey (recomendado):**
   ```bash
   choco install ffmpeg
   ```

2. **Opción B - Descarga manual:**
   - Descarga FFmpeg desde: https://ffmpeg.org/download.html
   - Extrae el archivo ZIP
   - Agrega la carpeta `bin` al PATH del sistema
   - Verifica la instalación: `ffmpeg -version`

3. **Opción C - Usando winget:**
   ```bash
   winget install ffmpeg
   ```

## Instalación

### Opción 1: Ejecutar desde Python

```bash
# Instalar Python 3.8 o superior
# No se requieren dependencias adicionales, solo bibliotecas estándar

# Ejecutar el programa
python webm_to_mp4.py
```

### Opción 2: Crear ejecutable (.exe)

```bash
# Instalar PyInstaller
pip install pyinstaller

# Ejecutar el script de compilación
build_exe.bat

# El ejecutable estará en: dist\WebmToMP4Converter.exe
```

## Uso

1. **Seleccionar carpeta origen**: Haz clic en "Explorar..." junto a "Carpeta origen" y selecciona la carpeta que contiene los archivos WebM

2. **Seleccionar carpeta destino**: Haz clic en "Explorar..." junto a "Carpeta destino" y selecciona dónde guardar los archivos MP4

3. **Cargar archivos**: Haz clic en "Cargar archivos WebM" para escanear la carpeta origen

4. **Seleccionar archivos**: Haz clic en la casilla de cada archivo para seleccionar/deseleccionar. También puedes usar:
   - "Seleccionar todos"
   - "Deseleccionar todos"

5. **Convertir**: Haz clic en "Convertir seleccionados" para iniciar el proceso

6. **Monitorear progreso**: 
   - La barra de progreso muestra el avance general
   - El log muestra detalles de cada conversión
   - Puedes colapsar/expandir el log con el botón "▼ Mostrar/Ocultar Log"

## Detalles técnicos

### Validación de dimensiones

El formato MP4 requiere que las dimensiones del video (ancho y alto) sean números pares. El programa:
- Detecta automáticamente las dimensiones del video original
- Ajusta las dimensiones si son impares (resta 1 píxel)
- Aplica el filtro de escala necesario en FFmpeg

### Parámetros de conversión FFmpeg

```bash
ffmpeg -i input.webm \
  -vf scale=WIDTH:HEIGHT \  # Solo si se necesita ajuste
  -c:v libx264 \             # Códec de video H.264
  -preset medium \           # Velocidad de codificación
  -crf 23 \                  # Calidad (18-28, menor = mejor)
  -c:a aac \                 # Códec de audio AAC
  -b:a 128k \                # Bitrate de audio
  -movflags +faststart \     # Optimización para streaming
  output.mp4
```

## Estructura del proyecto

```
WebmToMP4/
├── webm_to_mp4.py      # Programa principal
├── requirements.txt     # Dependencias
├── build_exe.bat       # Script para crear ejecutable
└── README.md           # Este archivo
```

## Características implementadas

✅ **Requisito 1**: Tomar información de una carpeta  
✅ **Requisito 2**: Identificar videos WebM con propiedades  
✅ **Requisito 3**: Seleccionar carpeta destino  
✅ **Requisito 4**: Seleccionar archivos del listado  
✅ **Requisito 5**: Botón de conversión  
✅ **Requisito 6**: Validación de píxeles pares  
✅ **Requisito 7**: Preparación de comandos FFmpeg  
✅ **Requisito 8**: Ejecución de conversión  
✅ **Requisito 9**: Barra de progreso y log colapsable  
✅ **Requisito 10**: FFmpeg desde PATH  

## Solución de problemas

### "FFmpeg no está disponible en el PATH"
- Verifica que FFmpeg esté instalado: `ffmpeg -version`
- Agrega FFmpeg al PATH del sistema
- Reinicia el programa después de configurar el PATH

### "No se pudieron obtener dimensiones"
- Verifica que el archivo WebM no esté corrupto
- Asegúrate de que FFprobe (incluido con FFmpeg) esté disponible

### El ejecutable no funciona
- Verifica que FFmpeg esté en el PATH del sistema
- Ejecuta el .exe desde la línea de comandos para ver errores
- Asegúrate de tener permisos de escritura en la carpeta destino

## Licencia

Código libre para uso personal y comercial - GPL 3

## Créditos

- Desarrollado por Fabio Baccaglioni - 2025
- Desarrollado con Python y Tkinter
- Software libre bajo licencia GPL 3
