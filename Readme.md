# WebScraping Dashboard

Aplicación web para analizar páginas públicas y visualizar información de su estructura HTML, estilos CSS, diseño, componentes y SEO mediante un dashboard interactivo.

El proyecto utiliza Python, FastAPI y Playwright en el backend, junto con HTML, CSS y JavaScript en el frontend.

Los resultados se devuelven en formato JSON y se muestran en el dashboard. No utiliza una base de datos ni guarda los resultados de forma persistente.

---

## 1. Características

- Analizar una página web a partir de su URL.
- Inspeccionar elementos HTML visibles.
- Analizar colores y tipografías.

---

## 2. Tecnologías utilizadas

### Backend

- Python
- FastAPI
- Uvicorn
- Playwright
- Chromium
- BeautifulSoup4
- HTTPX

### Frontend

- HTML5
- CSS3
- JavaScript

---

## 3. Estructura del proyecto

```text
WebScraping/
├── .venv/
├── backend/
│   └── main.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── requirements.txt
└── README.md
```

La carpeta .venv/ se crea localmente al configurar el entorno virtual y no debe subirse al repositorio.

### Descripción de los archivos

- backend/main.py: contiene la API y la lógica de análisis web.
- frontend/index.html: define la estructura del dashboard.
- frontend/styles.css: contiene los estilos visuales.
- frontend/app.js: gestiona las interacciones y las peticiones al backend.
- requirements.txt: lista las dependencias de Python.
- README.md: contiene la documentación del proyecto.

---

## 4. Requisitos previos

Antes de instalar el proyecto se necesita:

- Git.
- Python instalado.
- PowerShell en Windows.

### Versión de Python

Se recomienda probar con Python 3.12 o 3.13 para reducir posibles problemas de compatibilidad con Playwright y los subprocesos en Windows.

Para comprobar las versiones instaladas:

    python --version
    py --version
    py -0p

El comando py -0p permite consultar las versiones de Python disponibles mediante el lanzador de Windows.

---

## 5. Dependencias del proyecto

El archivo requirements.txt contiene:

    fastapi
    uvicorn[standard]
    playwright
    beautifulsoup4
    httpx

### Función de las dependencias

- fastapi: permite crear los endpoints de la API.
- uvicorn[standard]: ejecuta el servidor ASGI.
- playwright: automatiza el navegador para inspeccionar páginas web.
- beautifulsoup4: permite procesar y consultar el HTML.
- httpx: permite realizar peticiones HTTP desde Python.

Chromium se instala por separado mediante Playwright.

---

## 6. Configuración inicial del proyecto

Estos son los pasos utilizados para configurar el proyecto en Windows.

### 6.1. Crear la carpeta del proyecto

    mkdir C:\WebScraping
    cd C:\WebScraping

Si la carpeta ya existe, solo hay que ingresar a ella:

    cd C:\WebScraping

### 6.2. Crear requirements.txt

Crear el archivo requirements.txt en la raíz del proyecto con el siguiente contenido:

    fastapi
    uvicorn[standard]
    playwright
    beautifulsoup4
    httpx

### 6.3. Crear el entorno virtual

Desde la raíz del proyecto:

    py -m venv .venv

Este comando crea un entorno virtual aislado para las dependencias de Python.

### 6.4. Activar el entorno virtual

Ejecutar:

    .\.venv\Scripts\Activate.ps1

Si se activa correctamente, la terminal mostrará algo similar a:

    (.venv) PS C:\WebScraping>

Si PowerShell bloquea la ejecución del script, se puede permitir temporalmente para la sesión actual:

    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

### 6.5. Instalar las dependencias

Con el entorno virtual activado:

    py -m pip install -r requirements.txt
    py -m pip install playwright
    py -m playwright install chromium
    py -m pip install uvicorn
    py -m pip install -r requirements.txt
    py -m pip install beautifulsoup4
    py -m pip install fastapi

Para usar el proyecto se tiene que tener corriendo (con el entorno virtual activado)

    py -m uvicorn main:app --app-dir backend

## 7. Cómo clonar y configurar el proyecto desde cero

Estos son los pasos que debe seguir otra persona para utilizar el proyecto desde un repositorio Git.

### 7.1. Clonar el repositorio

    git clone

### 7.2. Crear el entorno virtual

    py -m venv .venv

### 7.3. Activar el entorno virtual

    .\.venv\Scripts\Activate.ps1

### 7.4. Iniciar el backend

Desde la raíz del proyecto, arrancar el servidor:

    py -m uvicorn main:app --app-dir backend

Si todo funciona correctamente, Uvicorn mostrará un mensaje similar a:

    INFO: Uvicorn running on http://127.0.0.1:8000
    INFO: Application startup complete.

La API estará disponible en:

    http://127.0.0.1:8000

### Backend

Desde la raíz del proyecto:

    cd C:\WebScraping
    .\.venv\Scripts\Activate.ps1
    py -m uvicorn main:app --app-dir backend

Para activar la recarga automática durante el desarrollo:

    python -m uvicorn main:app --app-dir backend --reload

Si Playwright presenta errores relacionados con asyncio o la creación de procesos, probar primero sin --reload.

---

## 9. Endpoints del backend

El frontend está preparado para comunicarse con los siguientes endpoints.

### Comprobar el estado de la API

    GET /api/health

Permite comprobar si el backend está disponible.

---

## 10. Consideraciones de seguridad y uso

- Analizar únicamente páginas públicas que se tenga autorización para consultar.
- Respetar los términos de uso y las políticas de acceso de los sitios analizados.
- Validar las URL recibidas por el backend para reducir riesgos de SSRF.
- El análisis se realiza en memoria y no requiere persistencia de resultados en una base de datos.