# Backend Directorio - Instrucciones para reproducir el proyecto

## Autores (Equipo 6):
* Aram Baruch González Pérez
* Pedro Hernández Oregel
* Roberto Martínez Román


## 1. Clonar el repositorio

```bash
git clone https://github.com/CLA-CADI-2026/backend-directorio.git
cd backend-directorio
```

## 2. Levantar MySQL con Docker

Ejecuta MySQL en un contenedor con los mismos valores que usa la aplicacion por defecto:

```bash
docker run --name mysql-directorio \
  -e MYSQL_ROOT_PASSWORD=contrasena \
  -e MYSQL_DATABASE=directorio \
  -p 3306:3306 \
  -d mysql:8
```

Verifica que el contenedor este en ejecucion:

```bash
docker ps
```

## 3. Crear las tablas y datos iniciales

Importa el script SQL incluido en el repositorio:

```bash
docker exec -i mysql-directorio mysql -uroot -pcontrasena < basedatos.sql
```

## 4. Instalar dependencias de Python (sin entorno virtual)

No usamos entorno virtual en este proyecto. Instala dependencias de forma global en tu entorno actual:

```bash
pip3 install flask flask-cors mysql-connector-python
```

## 5. Configurar variables de entorno (opcional)

La API ya trae valores por defecto:
- `DB_HOST=localhost`
- `DB_USER=root`
- `DB_PASSWORD=contrasena`
- `DB_NAME=directorio`

Si necesitas cambiarlos:

```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=contrasena
export DB_NAME=directorio
```

## 6. Ejecutar la API

```bash
python3 main.py
```

La API queda disponible en:
- `http://localhost:3000/api/v1`

## 7. Probar endpoints rapido con curl

### Materias

```bash
curl http://localhost:3000/api/v1/materias
```

### Docentes

```bash
curl http://localhost:3000/api/v1/docentes
```

## 8. Detener y limpiar (opcional)

```bash
docker stop mysql-directorio
docker rm mysql-directorio
```
