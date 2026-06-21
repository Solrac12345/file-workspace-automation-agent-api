# 🤖 File & Workspace Automation Agent - Backend API

API RESTful construida con **FastAPI**, **MongoDB** y **Docker** para gestionar la automatización de archivos y espacios de trabajo. Este backend es el núcleo del proyecto "File & Workspace Automation Agent" desarrollado para el SENA.

##  Problema y Solución

### ⚠️ El Problema
En los entornos digitales actuales, la gestión manual de archivos y documentos en los espacios de trabajo es ineficiente, propensa a errores y consume mucho tiempo. Los usuarios suelen enfrentar dificultades para organizar, clasificar y localizar archivos (PDFs, imágenes, hojas de cálculo) entre múltiples carpetas, lo que resulta en espacios de trabajo desordenados, pérdida de información y una disminución significativa en la productividad.

### 💡 La Solución
**File & Workspace Automation Agent** es una solución integral que automatiza la gestión de archivos mediante reglas personalizables. A través de una API RESTful robusta y una interfaz web intuitiva, el sistema permite a los usuarios definir reglas de automatización (por ejemplo: *"Mover todos los PDFs a la carpeta de Contabilidad"* o *"Clasificar imágenes por fecha"*). El agente se encarga de organizar, clasificar y administrar los archivos de manera automática, garantizando un espacio de trabajo ordenado, optimizando el tiempo de los usuarios y eliminando la carga de las tareas repetitivas.


## ️ Tecnologías Utilizadas

- **Lenguaje:** Python 3.12
- **Framework Web:** FastAPI 0.115
- **Base de Datos:** MongoDB Atlas (NoSQL)
- **Driver Async:** Motor 3.6.0
- **Validación de Datos:** Pydantic v2
- **Contenedorización:** Docker & Docker Compose
- **Testing:** Pytest + httpx
- **Autenticación:** Passlib (Bcrypt) + Tokens en memoria

## 📁 Estructura del Proyecto

```text
file-workspace-automation-agent/
├── backend/
│   ├── app/
│   │   ├── controllers/       # Lógica de negocio (OOP)
│   │   ├── database/          # Conexión a MongoDB
│   │   ├── models/            # Modelos Pydantic
│   │   ├── routers/           # Endpoints REST
│   │   ├── config.py          # Configuración de entorno
│   │   └── main.py            # Punto de entrada
│   ├── tests/                 # Tests unitarios con Pytest
│   ├── .env                   # Variables de entorno (no subir a Git)
│   ├── Dockerfile             # Configuración de Docker
│   └── requirements.txt       # Dependencias de Python
└── frontend/                  # Interfaz web (HTML/CSS/JS)

## Clonar el repositorio
git clone <URL_DE_TU_REPOSITORIO>
cd file-workspace-automation-agent/backend

## Configurar variables de entorno
env 
    MONGODB_URI=mongodb+srv://<usuario>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
    DB_NAME=automation_agent
    SECRET_KEY=tu_clave_secreta_super_larga

## Crear y activar entorno virtual
# Windows (Git Bash)
python -m venv venv
source venv/Scripts/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

## Ejecutar el Proyecto
```bash 
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Usando Docker
docker build -t automation-agent-api .
docker run -d -p 8000:8000 --env-file .env --name automation-agent automation-agent-api

## Ejecutar Tests
```bash
    pytest tests/ -v

License: MIT