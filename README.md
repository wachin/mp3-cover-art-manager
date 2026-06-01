# Cover Finder

Una aplicación gráfica para buscar y agregar carátulas (album art) a archivos MP3. Utiliza las APIs de iTunes y Deezer para encontrar automáticamente las portadas de tus canciones.

## Características

- **Arrastrar y soltar**: Simplemente arrastra tus archivos MP3 a la aplicación
- **Búsqueda automática**: Busca carátulas usando iTunes y Deezer APIs
- **Previsualización**: Muestra las carátulas encontradas antes de guardarlas
- **Detección de carátulas existentes**: Detecta si un MP3 ya tiene carátula y la muestra
- **Selección inteligente**: Los archivos con carátula existente aparecen desmarcados por defecto
- **Filas de altura dinámica**: Las filas se ajustan al tamaño de las carátulas para una mejor visualización

## Requisitos

- Python 3.6 o superior
- PyQt6
- requests
- mutagen

## Instalación

### Linux

#### Método 1: Ejecutar directamente (recomendado)

1. Asegúrate de tener Python 3 y las dependencias instaladas:
```bash
sudo apt update
sudo apt install python3 python3-pip
pip3 install PyQt6 requests mutagen
```

2. Ejecuta la aplicación:
```bash
python3 cover_finder.py
```

#### Método 2: Usar pip (para desarrolladores)

1. Instala las dependencias:
```bash
pip install PyQt6 requests mutagen
```

2. Ejecuta la aplicación:
```bash
python cover_finder.py
```

### Windows

1. Asegúrate de tener Python instalado y en el PATH. Descárgalo desde [python.org](https://www.python.org/downloads/)

2. Abre una terminal (CMD o PowerShell) y navega al directorio donde está `cover_finder.py`

3. Instala las dependencias:
```bash
pip install PyQt6 requests mutagen
```

4. Ejecuta la aplicación:
```bash
python cover_finder.py
```

O si tienes Python 3 específicamente:
```bash
py cover_finder.py
```

### macOS

1. Asegúrate de tener Python 3 instalado. Puedes instalarlo con Homebrew:
```bash
brew install python3
```

2. Instala las dependencias:
```bash
pip3 install PyQt6 requests mutagen
```

3. Ejecuta la aplicación:
```bash
python3 cover_finder.py
```

## Uso

1. **Agregar archivos MP3**:
   - Arrastra y suelta archivos MP3 en la zona designada
   - O haz clic en el botón "⬆ Add MP3 files" para seleccionar archivos

2. **Ver carátulas existentes**:
   - Los archivos que ya tienen carátula se muestran con la imagen y un borde verde
   - Estos archivos aparecen con el checkbox desmarcado por defecto

3. **Buscar carátulas**:
   - Haz clic en el botón "🔍 Search Covers" para buscar carátulas automáticamente
   - El programa buscará en iTunes y Deezer las mejores coincidencias
   - Las carátulas encontradas se mostrarán en la columna "Cover Preview"

4. **Seleccionar qué guardar**:
   - Marca o desmarca los checkboxes según las carátulas que quieras guardar
   - Usa los botones "Select all" o "Unselect all" para marcar/desmarcar todo

5. **Guardar carátulas**:
   - Haz clic en "💾 Save Selected Covers" para guardar las carátulas seleccionadas en los archivos MP3

## Notas

- El programa usa un sistema de puntuación para encontrar las mejores coincidencias de carátulas
- Las filas de la tabla se ajustan automáticamente al tamaño de las carátulas para una mejor visualización
- Puedes redimensionar la columna "Cover Preview" arrastrando su borde
- La aplicación se abre maximizada para aprovechar el espacio de pantalla

## Licencia

Este proyecto es de código abierto y está disponible para uso personal.

## Créditos

Desarrollado por Washington Indacochea Delgado
