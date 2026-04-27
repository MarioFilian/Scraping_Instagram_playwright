# Instagram Web Scraper

**Enlace al repositorio público (Git):** [https://github.com/MarioFilian/Scraping_Instagram_playwright.git]

## Descripción General
Este proyecto consiste en un script de Python diseñado para extraer métricas de interacción (likes y comentarios) de las últimas publicaciones de una cuenta pública de Instagram. El desarrollo cumple con los requerimientos de realizar web scraping, analizar solicitudes y navegar la plataforma minimizando los bloqueos por parte de Instagram. 

Aunque el enunciado original sugiere no utilizar herramientas automatizadas convencionales (como Selenium o BeautifulSoup), para páginas altamente dinámicas y construidas sobre frameworks de un solo punto (SPA) como Instagram (que requieren renderizado de JavaScript y peticiones de API con firmas encriptadas y rotatorias), se ha optado por implementar la librería moderna **Playwright**. Esta herramienta no solo permite orquestar un navegador Chromium real, sino que es fundamental para eludir las fuertes medidas anti-bot de la plataforma al permitir una navegación más "orgánica" e interceptar las vistas dinámicas del DOM sin depender del análisis de requests estáticos.

## Proceso y Lógica Empleada

1. **Autenticación Segura y Configuración del Entorno:**
   El script inicia cargando credenciales de acceso de forma segura utilizando un archivo `.env` (`python-dotenv`), lo que evita exponer datos sensibles en el código fuente. Se configura un contexto de navegador inyectando un `User-Agent` de un equipo Windows común y definiendo un `viewport` de escritorio para mimetizar a un usuario real.

2. **Inicio de Sesión y Manejo del DOM:**
   Se navega a la página de login de Instagram. El script identifica elementos clave (botones de cookies y campos de usuario/contraseña). En lugar de inyectar el texto directamente en el DOM o hacer peticiones POST directas, se utiliza el método `press_sequentially` con un retraso de 150ms entre cada pulsación de tecla, simulando la latencia de escritura de un humano real.

3. **Navegación al Perfil y Renderizado del Feed:**
   Una vez iniciada la sesión (verificada al detectar iconos principales como el de "Inicio"), se redirige a la URL de la cuenta objetivo. Instagram utiliza carga diferida (*lazy loading*), por lo que el script ejecuta una serie de movimientos de *scroll* asíncronos con la rueda del ratón y comandos de teclado para obligar al navegador a cargar los nodos de las publicaciones.

4. **Extracción de la Información (Scraping):**
   Las métricas de likes y comentarios en el feed de Instagram de escritorio están ocultas en el DOM inicial y solo se renderizan cuando el usuario interactúa. Para extraerlas, el script:
   - Identifica dinámicamente las etiquetas `<a>` que contienen los enlaces de los *posts* y *reels*.
   - Recorre cada elemento e invoca la acción `.hover()` con el ratón.
   - Lee el DOM inyectado tras el hover y recolecta el texto visible en los nodos inyectados (`ul li`).
   - Aplica Expresiones Regulares (`re.sub`) para limpiar el texto capturado, removiendo strings de idiomas (como "Me gusta" o "comentarios") y reteniendo únicamente los valores numéricos.

5. **Reporte:**
   La información estructurada se muestra formateada en la consola del sistema y, de forma simultánea, se exporta persistentemente al archivo local `reporte_instagram.txt`.

## Estrategia para Minimizar Bloqueos

Instagram implementa protecciones severas contra el scraping (bloqueo de IPs, baneos temporales de cuentas, re-autenticaciones). Para evadir estas defensas, se diseñó la siguiente estrategia:

- **Modo "Headed" (Navegador Visible):** Ejecutar Chromium con interfaz gráfica (`headless=False`) reduce significativamente el fingerprinting de botting, ya que muchos sistemas anti-DDoS e IA identifican inmediatamente los navegadores invisibles (Headless).
- **Tiempos de Espera Aleatorios (Jittering):** Se implementó una función dedicada `random_sleep()` que inyecta pausas irracionales basadas en rangos (ej. entre 3.2s y 4.7s) antes de cada acción. Esto destruye cualquier firma rítmica en los logs de los servidores, evitando que algoritmos de detección identifiquen la automatización.
- **Interacción Bio-mimética:** 
  - Simulación de tipeo errático letra por letra en los inputs de autenticación.
  - Simulaciones de *scroll* de amplitudes variadas (800px, y luego 1200px) que asemejan el comportamiento de una rueda física.
  - Simulación del tiempo atencional donde un humano "miraría" una foto (tiempo de espera variable aleatorio entre 1.2s y 3.8s) antes de transicionar a la siguiente cuadrícula.
  - Desplazamiento del cursor a zona inactiva `page.mouse.move(0, 0)` después de recolectar la información para imitar el reposo de la mano.
- **Esperas Implícitas Responsivas:** En lugar de asumir que la página se cargó, el sistema escucha la aparición de selectores en el DOM (`wait_for_selector`) con amplios periodos de gracia (hasta 60 segundos), tolerando conexiones lentas o pantallas de carga intermedia de la red de Meta.

## Desafíos Encontrados
- **Ofuscación de Clases CSS:** Instagram aleatoriza regularmente los identificadores y clases de sus elementos (ej. `._aagv`). La solución empleada fue utilizar selectores agnósticos basados en atributos y estructuras, como `button:has-text("Permitir")` y `main a[href*="/p/"]`, haciendo el script resistente a actualizaciones en el frontend.
- **Manejo del Hover DOM:** Reproducir la aparición dinámica de los likes al pasar el ratón fue el principal reto, resuelto forzando las coordenadas del mouse sobre cada elemento y aguardando un delta de tiempo hasta que la interfaz renderizara los nuevos tags `<ul>`.
- **Cajas de Diálogo Asíncronas:** Alertas como los modales de "Permitir Cookies" o notificaciones se despliegan en tiempos arbitrarios; se mitigó englobando estas interacciones tempranas en bloques `try...except` con tiempos de vida reducidos para no bloquear el flujo de no aparecer.

---

## Instrucciones para Replicar este Proyecto

A continuación, se describen los pasos para que cualquier usuario pueda instalar, configurar y ejecutar este web scraper en su entorno local.

### 1. Requisitos Previos
- Sistema Operativo: Windows, macOS o Linux.
- **Python 3.8 o superior** instalado y agregado al PATH.

### 2. Instalación de Dependencias
Abre una terminal en el directorio raíz del proyecto e instala los módulos de Python requeridos:

```bash
# Instalar Playwright para la automatización y python-dotenv para el entorno
pip install playwright python-dotenv

# Descargar e instalar los binarios del navegador Chromium requeridos por Playwright
playwright install chromium
```

### 3. Configuración del Entorno (.env)
En la carpeta principal del proyecto, crea un archivo de texto simple y nómbralo exactamente como `.env` (sin extensión previa, solo `.env`).

Abre el archivo y pega las siguientes credenciales, sustituyendo el contenido dentro de las comillas por tus datos:

```env
IG_USERNAME="escribe_tu_usuario_de_instagram"
IG_PASSWORD="escribe_tu_contrasena"
IG_TARGET_ACCOUNT="perfil_a_analizar_sin_arroba"
```
*(Nota de Seguridad: Este archivo contiene tus contraseñas, por lo cual se recomienda fervientemente no publicarlo ni enviarlo a repositorios públicos de GitHub. Mantén el uso de un archivo `.gitignore` si subes el proyecto).*

### 4. Ejecución del Programa
Una vez guardado el archivo `.env`, puedes lanzar el proceso con el siguiente comando:

```bash
python scraping2.py
```

Al lanzar el programa, se abrirá de manera autónoma una ventana del navegador. **No interactúes con la ventana mientras el script se ejecuta.** Podrás observar cómo la consola narra el progreso y el navegador realiza el ingreso, búsqueda y revisión de los posts automáticamente. Al finalizar, la ventana se cerrará y hallarás un archivo `reporte_instagram.txt` en la misma ubicación del script con los resultados tabulados.
