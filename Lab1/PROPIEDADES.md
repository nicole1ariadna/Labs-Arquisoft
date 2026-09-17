# Gestor de Calificaciones — Propiedades del Sistema

A continuación se identifican y justifican cinco (5) propiedades (atributos de calidad)
del sistema, con base en las decisiones de diseño reflejadas en `ARQUITECTURA.md` y en
el código del proyecto.

---

## 1. Modificabilidad (Modifiability)

**Descripción:** capacidad de introducir cambios en una parte del sistema con el mínimo
impacto posible sobre las demás.

**Cómo se logra:** la arquitectura en capas (`controllers → services → repositories →
models`) impone una regla de dependencia estricta: cada capa solo conoce a la
inmediatamente inferior. Esto permite, por ejemplo, cambiar la lógica de negocio en
`grade_service.py` sin tocar `grade_controller.py`, o cambiar el motor de persistencia
sin modificar la capa de servicio, siempre que el `repository` mantenga su contrato
(`get_all`, `add`, `delete_by_id`).

**Evidencia concreta:** el proyecto ya demuestra esta propiedad al soportar dos motores
de base de datos (MySQL en producción/Docker y SQLite como fallback local) cambiando
únicamente `config.py`, sin alterar modelos, repositorios ni servicios.

---

## 2. Desplegabilidad (Deployability)

**Descripción:** facilidad con la que el sistema puede pasar de código fuente a una
instancia en ejecución en un entorno dado.

**Cómo se logra:** el sistema se empaqueta en dos contenedores Docker orquestados con
`docker-compose.yml` (`swarch-mo` para la aplicación Flask y `swarch-db` para MySQL).
Toda la configuración de conexión se inyecta por variable de entorno
(`DATABASE_URL`), y el `healthcheck` de `swarch-db` con
`depends_on: condition: service_healthy` garantiza que la aplicación no intente
conectarse a la base de datos hasta que esta esté realmente lista.

**Trade-off:** el volumen `.:/app` es ideal para desarrollo (hot-reload), pero para un
despliegue productivo debería retirarse, ya que acopla el contenido del contenedor al
sistema de archivos del host.

---

## 3. Portabilidad (Portability)

**Descripción:** capacidad del sistema de ejecutarse en distintos entornos con un
esfuerzo de adaptación mínimo.

**Cómo se logra:** la containerización con Docker aísla al sistema de las diferencias
del sistema operativo anfitrión (dependencias del sistema como `gcc` o
`default-libmysqlclient-dev` se instalan dentro de la imagen, no en el host). Además,
el fallback a SQLite en `config.py` permite ejecutar la aplicación incluso sin
Docker/MySQL disponibles, útil para pruebas rápidas o entornos restringidos.

---

## 4. Testabilidad (Testability)

**Descripción:** facilidad con la que se pueden diseñar y ejecutar pruebas que
detecten fallos en el sistema.

**Cómo se logra:** al separar la lógica de negocio (`services`) del acceso a datos
(`repositories`) y de la capa web (`controllers`), cada capa se puede probar de forma
aislada: los servicios se pueden probar con un repositorio simulado (mock), y los
repositorios se pueden probar contra una base de datos SQLite en memoria sin necesidad
de levantar Flask ni Docker. El uso del patrón *Application Factory* (`create_app()`
en `app.py`) refuerza esto, porque permite instanciar la aplicación con una
configuración de pruebas distinta a la de producción.

---

## 5. Disponibilidad (Availability)

**Descripción:** proporción de tiempo en que el sistema está operativo y responde
correctamente a las solicitudes.

**Cómo se logra parcialmente:** el `healthcheck` de MySQL (`mysqladmin ping`, cada 5s,
hasta 12 reintentos) evita que la aplicación arranque en un estado inconsistente por
no encontrar la base de datos disponible, reduciendo fallos al iniciar el sistema.

**Limitación identificada:** el sistema actual es monolítico y de una sola instancia;
no hay réplicas ni política de reinicio automático (`restart: on-failure` o similar)
en `docker-compose.yml`, por lo que si el contenedor `swarch-mo` falla, el sistema
completo queda no disponible hasta una intervención manual. Esto es esperado para un
laboratorio introductorio y sería uno de los primeros puntos a mejorar en una
arquitectura más robusta.
