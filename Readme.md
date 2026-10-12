# WebScraping Dashboard

Aplicación web para analizar páginas públicas y visualizar información de su estructura HTML, estilos CSS, diseño, componentes y SEO mediante un dashboard interactivo.

El proyecto utiliza Python, FastAPI y Playwright en el backend, junto con HTML, CSS y JavaScript en el frontend.

Los resultados se devuelven en formato JSON y se muestran en el dashboard. No utiliza una base de datos ni guarda los resultados de forma persistente.

---

## 1. Características

- Analizar una página web a partir de su URL.
- Inspeccionar elementos HTML visibles.
- Identificar imágenes, enlaces y botones.
- Analizar colores y tipografías.
- Consultar tamaños de fuente y variables CSS.
- Examinar la estructura de encabezados HTML.
- Obtener información SEO y metadatos Open Graph.
- Identificar imágenes sin atributo alt.
- Detectar indicios de frameworks utilizados.
- Inspeccionar información de diseño responsive y media queries.
- Visualizar los resultados en un dashboard.
- Descargar los resultados del análisis en formato JSON.
- Procesar los resultados en memoria, sin una base de datos.

Nota: los datos obtenidos dependen del sitio analizado y de las técnicas de inspección implementadas en el backend.

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

### Herramientas de desarrollo

- Visual Studio Code
- PowerShell
- Git
- Live Server

---

## 3. Estructura del proyecto

WebScraping/
├── backend/
│   └── main.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── requirements.txt
├── .gitignore
└── README.md

La carpeta .venv/ se crea localmente al configurar el entorno virtual y no debe subirse al repositorio.

### Descripción de los archivos

- backend/main.py: contiene la API y la lógica de análisis web.
- frontend/index.html: define la estructura del dashboard.
- frontend/styles.css: contiene los estilos visuales.
- frontend/app.js: gestiona las interacciones y las peticiones al backend.
- requirements.txt: lista las dependencias de Python.
- .gitignore: excluye archivos locales y temporales.
- README.md: contiene la documentación del proyecto.

---

## 4. Requisitos previos

Antes de instalar el proyecto se necesita:

- Git.
- Python instalado.
- PowerShell en Windows.
- Un navegador web.
- Visual Studio Code y Live Server, recomendados para el frontend.

### Versión de Python

Se recomienda probar con Python 3.12 o 3.13 para reducir posibles problemas de compatibilidad con Playwright y los subprocesos en Windows.

El proyecto se configuró inicialmente con Python 3.15, pero apareció un NotImplementedError relacionado con asyncio y la creación de procesos de Chromium.

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

Después, volver a ejecutar el comando de activación.

### 6.5. Instalar las dependencias

Con el entorno virtual activado:

    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

No es necesario instalar los paquetes individualmente si todos se encuentran declarados correctamente en requirements.txt.

### 6.6. Instalar Chromium

Ejecutar:

    python -m playwright install chromium

Este comando descarga Chromium, el navegador que Playwright utilizará para analizar las páginas web.

Importante: instalar el paquete playwright no instala automáticamente Chromium. Ambos pasos son necesarios.

---

## 7. Cómo clonar y configurar el proyecto desde cero

Estos son los pasos que debe seguir otra persona para utilizar el proyecto desde un repositorio Git.

### 7.1. Clonar el repositorio

Reemplazar la URL de ejemplo por la dirección real del repositorio:

    git clone https://github.com/USUARIO/REPOSITORIO.git

Ingresar a la carpeta:

    cd REPOSITORIO

### 7.2. Crear el entorno virtual

    py -m venv .venv

### 7.3. Activar el entorno virtual

    .\.venv\Scripts\Activate.ps1

### 7.4. Instalar las dependencias

    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

### 7.5. Instalar Chromium

    python -m playwright install chromium

### 7.6. Iniciar el backend

Desde la raíz del proyecto:

    python -m uvicorn main:app --app-dir backend

Si todo funciona correctamente, Uvicorn mostrará un mensaje similar a:

    INFO: Uvicorn running on http://127.0.0.1:8000
    INFO: Application startup complete.

La API estará disponible en:

    http://127.0.0.1:8000

La documentación interactiva de FastAPI normalmente estará disponible en:

    http://127.0.0.1:8000/docs

### 7.7. Abrir el frontend

1. Abrir la carpeta del proyecto en Visual Studio Code.
2. Localizar frontend/index.html.
3. Ejecutar el archivo mediante Live Server.
4. Abrir la dirección local que muestre Live Server.
5. Introducir la URL pública que se desea analizar.

Se recomienda utilizar Live Server en lugar de abrir directamente el archivo mediante file://.

---

## 8. Ejecución diaria

Una vez instaladas las dependencias y Chromium, normalmente solo es necesario iniciar el backend y abrir el frontend.

### Backend

Desde la raíz del proyecto:

    cd C:\WebScraping
    .\.venv\Scripts\Activate.ps1
    python -m uvicorn main:app --app-dir backend

Para activar la recarga automática durante el desarrollo:

    python -m uvicorn main:app --app-dir backend --reload

Si Playwright presenta errores relacionados con asyncio o la creación de procesos, probar primero sin --reload.

### Frontend

Abrir frontend/index.html mediante Live Server desde Visual Studio Code.

Para detener el servidor, presionar Ctrl + C en la terminal donde se ejecuta Uvicorn.

---

## 9. Endpoints del backend

El frontend está preparado para comunicarse con los siguientes endpoints.

### Comprobar el estado de la API

    GET /api/health

Permite comprobar si el backend está disponible.

### Analizar una página web

    POST /api/analyze
    Content-Type: application/json

Ejemplo de solicitud:

    {
      "url": "https://example.com"
    }

El endpoint debe recibir la URL, ejecutar el análisis y devolver los resultados en formato JSON.

El frontend espera que la respuesta incluya una propiedad success con valor true cuando el análisis se completa correctamente.

También utiliza campos como summary, design, structure, seo, responsive, requestedUrl y finalUrl.

La estructura exacta de la respuesta depende de la implementación de backend/main.py.

---

## 10. Configuración de CORS

Si el frontend y el backend se ejecutan en puertos diferentes, el navegador puede bloquear las solicitudes por las políticas de origen cruzado (CORS).

En ese caso, configurar el middleware de CORS en FastAPI.

Ejemplo para desarrollo local:

    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5500",
            "http://localhost:5500",
            "http://127.0.0.1:5501",
            "http://localhost:5501",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

Este código debe colocarse después de crear la instancia app = FastAPI().

Si Live Server utiliza otro puerto, agregar el origen correspondiente.

Esta configuración está pensada para desarrollo local. En producción se deben permitir únicamente los orígenes autorizados.

---

## 11. Errores comunes

### ModuleNotFoundError

Indica que Python no encuentra un paquete necesario.

Solución:

    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt

### Error: Executable doesn't exist

Playwright no encuentra el navegador requerido.

Solución:

    python -m playwright install chromium

### Error: Attribute "app" not found in module "main"

Uvicorn no encuentra una variable app dentro del módulo main.

Verificar que backend/main.py contenga una instancia de FastAPI, por ejemplo:

    from fastapi import FastAPI

    app = FastAPI()

Este ejemplo es solo la declaración mínima y no reemplaza los endpoints del proyecto.

### Error: NotImplementedError al iniciar Chromium

Si aparece un traceback que incluye:

    asyncio.create_subprocess_exec
    NotImplementedError

El problema está relacionado con la creación de procesos para iniciar Chromium.

Pasos recomendados:

1. Detener Uvicorn con Ctrl + C.
2. Iniciar el servidor sin --reload:

       python -m uvicorn main:app --app-dir backend

3. Comprobar las versiones instaladas:

       python --version
       python -m pip show playwright uvicorn fastapi

4. Si el error persiste, probar con Python 3.12 o 3.13 en un entorno virtual nuevo.
5. Revisar cómo se inicia Playwright en backend/main.py y qué bucle de eventos utiliza la aplicación.

No es recomendable reinstalar repetidamente todas las dependencias sin revisar primero el entorno y el traceback.

### Error: 502 Bad Gateway en /api/analyze

Puede indicar que el endpoint no pudo completar el análisis.

Si aparece junto con un error de Playwright, solucionar primero el problema del navegador o de su ejecución.

### Error de CORS en el navegador

Verificar que:

- El backend esté activo en http://127.0.0.1:8000.
- El frontend utilice la dirección correcta de la API.
- El origen de Live Server esté permitido en la configuración de CORS.
- El backend no esté devolviendo un error interno.

---

## 12. Archivo .gitignore

Se recomienda crear un archivo .gitignore en la raíz con el siguiente contenido:

    # Entorno virtual
    .venv/

    # Python
    __pycache__/
    *.py[cod]
    *.pyo

    # Entornos y secretos
    .env
    .env.*

    # Editores
    .vscode/
    .idea/

    # Logs
    *.log

    # Archivos temporales
    tmp/
    temp/

No se debe subir la carpeta .venv/ al repositorio. Cada persona debe crear su propio entorno virtual e instalar las dependencias.

---

## 13. Consideraciones de seguridad y uso

- Analizar únicamente páginas públicas que se tenga autorización para consultar.
- Respetar los términos de uso y las políticas de acceso de los sitios analizados.
- No utilizar el proyecto para eludir mecanismos de autenticación o controles de acceso.
- Validar las URL recibidas por el backend para reducir riesgos de SSRF.
- Si la API se publica en Internet, restringir los dominios permitidos, los recursos accesibles, los tiempos de espera y el tamaño de las respuestas.
- Evitar exponer la API directamente a Internet sin controles de seguridad.
- El análisis se realiza en memoria y no requiere persistencia de resultados en una base de datos.

---

## 14. Resumen de comandos

Estos son los comandos principales para configurar el proyecto por primera vez en Windows:

    # Crear el entorno virtual
    py -m venv .venv

    # Activar el entorno virtual
    .\.venv\Scripts\Activate.ps1

    # Actualizar pip
    python -m pip install --upgrade pip

    # Instalar las dependencias
    python -m pip install -r requirements.txt

    # Instalar Chromium para Playwright
    python -m playwright install chromium

    # Iniciar el backend
    python -m uvicorn main:app --app-dir backend

Una vez configurado el proyecto, para las siguientes ejecuciones normalmente basta con activar el entorno virtual, iniciar Uvicorn y abrir el frontend con Live Server.

---

## 15. Estado del proyecto

El proyecto está diseñado para analizar páginas web y presentar sus características en un dashboard, sin utilizar una base de datos.

Antes de considerar estable el entorno, se debe verificar que:

- [ ] Las dependencias se instalen correctamente.
- [ ] Chromium se inicie mediante Playwright.
- [ ] El endpoint /api/health responda correctamente.
- [ ] El endpoint /api/analyze complete un análisis de prueba.
- [ ] El frontend pueda comunicarse con el backend.
- [ ] El dashboard muestre los datos devueltos por la API.
- [ ] La descarga del JSON funcione correctamente.

Nota: que Uvicorn arranque correctamente no garantiza por sí solo que Playwright pueda iniciar Chromium. Es necesario probar los endpoints y realizar al menos un análisis real.