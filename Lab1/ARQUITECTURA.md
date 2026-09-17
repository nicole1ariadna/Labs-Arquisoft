# Gestor de Calificaciones — Representación de la Arquitectura

Aplicación web construida con **Flask** siguiendo una **arquitectura en capas**
(Layered Architecture), persistencia con **SQLAlchemy** y despliegue mediante
**Docker Compose** contra una base de datos **MySQL 8.0**.

---

## 1. Vista de despliegue (Docker Compose)

Muestra los contenedores, sus puertos y cómo se comunican.

```mermaid
flowchart LR
    User(["👤 Usuario<br/>(Navegador)"])

    subgraph host["Host / Docker Compose"]
        subgraph web["Contenedor: swarch-mo"]
            flask["App Flask<br/>(python app.py)<br/>escucha :5000"]
        end
        subgraph dbc["Contenedor: swarch-db"]
            mysql[("MySQL 8.0<br/>DB: swarch-db")]
        end
    end

    User -- "HTTP :8080 → :5000" --> flask
    flask -- "DATABASE_URL<br/>mysql://root:***@swarch-db" --> mysql
    web -. "depends_on: service_healthy" .-> dbc
```

**Notas de despliegue**
- Puerto publicado: `8080` (host) → `5000` (contenedor).
- Volumen `.:/app` monta el código dentro del contenedor (hot-reload en desarrollo).
- `swarch-mo` espera a que `swarch-db` esté *healthy* (healthcheck con `mysqladmin ping`).
- Conexión a la BD vía variable de entorno `DATABASE_URL`.

---

## 2. Vista de capas (Layered Architecture)

Flujo de una petición HTTP a través de las capas del sistema.

```mermaid
flowchart TD
    subgraph P["Capa de Presentación"]
        T["Plantillas Jinja2<br/>base.html · grade_list.html"]
        C["Controller<br/>grade_controller.py<br/>Blueprint grade_bp"]
    end

    subgraph B["Capa de Negocio"]
        S["Service<br/>grade_service.py<br/>list / create / delete_grade"]
    end

    subgraph D["Capa de Acceso a Datos"]
        R["Repository<br/>grade_repository.py<br/>get_all / add / delete_by_id"]
        M["Model<br/>grade.py — Grade(db.Model)"]
    end

    subgraph I["Infraestructura"]
        DB[("Base de datos<br/>MySQL / SQLite")]
        CFG["config.py<br/>DB_CONFIG"]
        APP["app.py<br/>create_app() · Factory"]
    end

    T <--> C
    C --> S
    S --> R
    R --> M
    M --> DB
    APP -. init .-> C
    APP -. init .-> M
    CFG -. config .-> APP
```

**Regla de dependencia:** cada capa solo conoce a la inmediatamente inferior
(Controller → Service → Repository → Model → DB). La presentación nunca accede
directamente a los datos.

---

## 3. Diagrama de componentes / módulos

```mermaid
flowchart LR
    app["app.py<br/>Application Factory"]
    config["config.py"]
    ctrl["controllers/<br/>grade_controller.py"]
    svc["services/<br/>grade_service.py"]
    repo["repositories/<br/>grade_repository.py"]
    model["models/<br/>grade.py"]
    tmpl["templates/<br/>base.html · grade_list.html"]
    db[("instance/grades.db<br/>o MySQL")]

    app --> config
    app --> model
    app --> ctrl
    ctrl --> svc
    ctrl --> tmpl
    svc --> repo
    repo --> model
    model --> db
```

---

## 4. Modelo de datos

```mermaid
erDiagram
    GRADES {
        int id PK "autoincrement"
        string student_name "NOT NULL, 100"
        string subject "NOT NULL, 100"
        float score "NOT NULL"
    }
```

---

## 5. Flujo de una petición (secuencia)

Ejemplo: agregar una calificación (`POST /add`).

```mermaid
sequenceDiagram
    actor U as Usuario
    participant C as Controller (grade_bp)
    participant S as Service
    participant R as Repository
    participant DB as Base de datos

    U->>C: POST /add (student_name, subject, score)
    C->>S: create_grade(student, subject, score)
    S->>R: add(student_name, subject, score)
    R->>DB: INSERT INTO grades ...
    DB-->>R: commit OK
    R-->>S: return
    S-->>C: return
    C-->>U: redirect 302 → / (index)
    U->>C: GET / 
    C->>S: list_grades()
    S->>R: get_all()
    R->>DB: SELECT * FROM grades
    DB-->>R: filas
    R-->>S: [Grade, ...]
    S-->>C: [Grade, ...]
    C-->>U: HTML (grade_list.html)
```

---

## 6. Endpoints expuestos

| Método | Ruta                 | Controller | Acción                         |
|--------|----------------------|------------|--------------------------------|
| GET    | `/`                  | `index`    | Lista todas las calificaciones |
| POST   | `/add`               | `add`      | Crea una calificación          |
| GET    | `/delete/<grade_id>` | `delete`   | Elimina por id                 |

---

## 7. Stack tecnológico

- **Lenguaje:** Python 3.11
- **Framework web:** Flask 2.3.3
- **ORM:** Flask-SQLAlchemy 3.1.1
- **Driver BD:** mysqlclient 2.2.0
- **Base de datos:** MySQL 8.0 (producción) / SQLite (fallback local)
- **Contenedores:** Docker + Docker Compose
- **Vistas:** Jinja2 (templates HTML)
