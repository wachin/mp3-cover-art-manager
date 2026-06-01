# ROADMAP - Cover Finder

Este documento describe el historial de desarrollo y las futuras mejoras planificadas para Cover Finder, una aplicación gráfica para buscar y agregar carátulas a archivos MP3.

## Logros Completados

### Fase 1: Desarrollo Inicial del Script de Línea de Comandos

- [x] Creación del script `agregar_caratulas.py` para buscar y agregar carátulas automáticamente
  - Implementación de búsqueda usando iTunes Search API
  - Extracción de título y artista del nombre del archivo
  - Descarga y embedding de carátulas en archivos MP3
  - Procesamiento por lotes de múltiples archivos

- [x] Creación del script `recuperar_portadas.py` con sistema avanzado de búsqueda
  - Implementación de búsqueda en iTunes y Deezer APIs
  - Sistema de puntuación (scoring) para encontrar mejores coincidencias
  - Normalización de texto para mejorar coincidencias
  - Generación de reportes CSV y JSON
  - Soporte para umbrales de confianza configurables
  - Opción para incrustar carátulas automáticamente

### Fase 2: Desarrollo de Interfaz Gráfica (GUI)

- [x] Creación de interfaz gráfica usando PyQt6
  - Diseño basado en `txt-to-chordpro-converter-main` como referencia
  - Implementación de DropZoneWidget para arrastrar y soltar archivos MP3
  - Botón para cargar archivos mediante diálogo de selección
  - Tabla con columnas: Checkbox, Archivo, Artista, Título, Previsualización de carátula

- [x] Implementación de funcionalidad de búsqueda de carátulas
  - Integración de lógica de búsqueda de `recuperar_portadas.py`
  - Búsqueda en segundo plano usando QThread para no bloquear la interfaz
  - Barra de progreso durante la búsqueda
  - Previsualización de carátulas encontradas

- [x] Implementación de funcionalidad de guardado de carátulas
  - Selección de archivos mediante checkboxes
  - Botones para seleccionar/deseleccionar todos
  - Guardado de carátulas seleccionadas en archivos MP3
  - Manejo de errores con mensajes informativos

### Fase 3: Detección de Carátulas Existentes

- [x] Implementación de detección de carátulas existentes en MP3
  - Función `has_cover()` para verificar si un archivo ya tiene carátula
  - Función `extract_cover()` para extraer carátulas existentes
  - Visualización de carátulas existentes con borde verde
  - Checkboxes desmarcados por defecto para archivos con carátula existente

### Fase 4: Mejoras de Interfaz y Usabilidad

- [x] Aumento del tamaño de la columna de previsualización
  - Cambio de ancho de 120px a 200px
  - Modo de redimensionamiento interactivo para ajuste manual
  - Aumento del tamaño de imágenes de 100x100 a 180x180

- [x] Implementación de filas de altura dinámica
  - Configuración de verticalHeader con ResizeToContents
  - Eliminación de tamaño fijo de imágenes
  - Uso de resizeRowToContents() para ajuste automático
  - Imágenes escaladas a máximo 200x300 manteniendo aspect ratio
  - Aplicación se abre maximizada para aprovechar espacio

### Fase 5: Documentación y Branding

- [x] Creación de README.md con instrucciones completas
  - Instrucciones para Linux (método directo y pip)
  - Instrucciones para Windows (Python en PATH)
  - Instrucciones para macOS (Homebrew/Python 3)
  - Descripción de características y uso del programa

- [x] Creación de icono SVG personalizado
  - Diseño con carátula de álbum, nota musical y lupa
  - Colores consistentes con la interfaz (#2bbfa4)
  - Representación visual del propósito del programa

- [x] Implementación de ventana "Acerca de"
  - Botón "About..." en la interfaz
  - Diseño de dos columnas: icono grande a la izquierda, texto a la derecha
  - Información del desarrollador con correo clickeable
  - Copyright, licencia y tecnologías usadas
  - Descripción del programa

## Tareas Futuras

### Fase 6: Internacionalización

- [ ] Pasar el programa al inglés
  - Traducir todos los textos de la interfaz al inglés
  - Reemplazar textos en español con llamadas a tr()
  - Asegurar que el código base esté en inglés

- [ ] Crear archivos de internacionalización con Qt Linguist
  - Extraer cadenas traducibles usando pylupdate6
  - Crear archivo .ts base para inglés
  - Crear archivo .ts para español
  - Permitir futuros idiomas

- [ ] Integrar sistema de traducción en la aplicación
  - Cargar traducciones según el locale del sistema
  - Implementar cambio de idioma en tiempo de ejecución
  - Probar traducciones en diferentes idiomas

### Fase 7: Empaquetado para Debian

- [ ] Crear estructura de paquete Debian
  - Crear directorio debian/ con archivos de control
  - debian/control: metadatos del paquete
  - debian/rules: reglas de construcción
  - debian/changelog: registro de cambios
  - debian/copyright: información de licencia
  - debian/install: archivos a instalar

- [ ] Configurar dependencias del paquete
  - Especificar dependencias de Python (python3, python3-pyqt6, python3-requests, python3-mutagen)
  - Configurar scripts de post-instalación
  - Crear entrada de escritorio .desktop
  - Instalar icono en ubicaciones apropiadas

- [ ] Pasar normas y políticas de Debian
  - Revisar Debian Policy Manual
  - Asegurar cumplimiento de estándares de calidad
  - Implementar lintian checks
  - Preparar para revisión por Debian maintainers

- [ ] Publicar en packages.debian.org
  - Crear cuenta en Debian Mentors
  - Subir paquete para revisión
  - Responder feedback de maintainers
  - Seguir proceso de aceptación

### Fase 8: Automatización con GitHub Actions

- [ ] Configurar GitHub Actions para Linux AppImage
  - Crear workflow para Linux
  - Configurar dependencias de construcción
  - Usar linuxdeploy o appimage-builder
  - Generar AppImage con todas las dependencias
  - Subir artifact a releases

- [ ] Configurar GitHub Actions para Windows
  - Crear workflow para Windows 10 y 11
  - Configurar entorno de construcción Windows
  - Usar pyinstaller o cx_Freeze para crear .exe
  - Crear instalador con NSIS o Inno Setup
  - Subir artifact a releases

- [ ] Configurar GitHub Actions para macOS
  - Crear workflow para macOS
  - Configurar entorno de construcción macOS
  - Usar py2app o pyinstaller para crear .app
  - Firmar y notarizar aplicación (si es posible)
  - Crear DMG para distribución
  - Subir artifact a releases

- [ ] Configurar releases automáticas
  - Automatizar creación de releases en GitHub
  - Generar changelog desde commits
  - Publicar instaladores en cada release
  - Configurar versionado semántico

## Notas para Desarrolladores

### Estructura del Proyecto

```
cover_finder/
├── cover_finder.py          # Aplicación principal (GUI)
├── agregar_caratulas.py     # Script original de línea de comandos
├── recuperar_portadas.py     # Script avanzado con scoring
├── cover_finder.svg         # Icono de la aplicación
├── README.md                # Documentación para usuarios
├── ROADMAP.md               # Este archivo
└── Imagenes-de-error/       # Capturas de error (temporal)
```

### Dependencias

- Python 3.6+
- PyQt6
- requests
- mutagen

### Tecnologías Utilizadas

- **GUI Framework**: PyQt6
- **APIs de búsqueda**: iTunes Search API, Deezer API
- **Manipulación de MP3**: mutagen
- **HTTP requests**: requests
- **Threading**: QThread para operaciones en segundo plano

### Licencia

GPL3 - Copyright © 2026 Washington Indacochea Delgado

### Contacto

- Desarrollador: Washington Indacochea Delgado
- Correo: linuxfrontier@proton.me

## Historial de Versiones

### v1.0.0 (Actual)
- Interfaz gráfica completa con PyQt6
- Búsqueda de carátulas en iTunes y Deezer
- Detección de carátulas existentes
- Filas de altura dinámica
- Ventana "Acerca de" con información del desarrollador
- Icono personalizado SVG
- Documentación completa
