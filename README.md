# Respect+

Plataforma gamer con Next.js, FastAPI y MongoDB: perfiles públicos, equipos, sponsors, comunidad, torneos individuales y por equipos, estadísticas por juego y moderación.

## Arranque con Docker

Desde la raíz, con Docker Desktop activo:

```powershell
respect-backend/venv/Scripts/python scripts/prepare_admin_env.py
docker compose --env-file Docker/.env -f Docker/docker-compose.yml up --build -d --wait
```

El helper conserva la configuración existente y prepara una contraseña administradora aleatoria de 32 caracteres en `Docker/.env`, archivo excluido del control de versiones. Para mostrar explícitamente las credenciales locales usa `--print-credentials`. No existe una contraseña inicial pública en el código.

- Frontend: http://localhost:3000
- Administración: http://localhost:3000/admin
- Documentación de la API: http://localhost:8000/docs
- Estado: http://localhost:8000/api/health

```powershell
docker compose --env-file Docker/.env -f Docker/docker-compose.yml ps
docker compose --env-file Docker/.env -f Docker/docker-compose.yml logs -f backend frontend
docker compose --env-file Docker/.env -f Docker/docker-compose.yml down
```

MongoDB conserva los datos en `mongo_data`. La aplicación ya no incluye seeding de demos, jugadores, equipos ni torneos. En una base nueva solo se crea el primer administrador a partir de `BOOTSTRAP_ADMIN_*`. Si ya existe un administrador, reiniciar no cambia su contraseña ni crea otro.

El registro público permite elegir **Jugador** o **Empresa / sponsor**. Un jugador solo necesita nombre o alias, usuario, correo y contraseña; pertenecer a un equipo es opcional. Una empresa tiene sus propias credenciales y su perfil de organización se crea al registrarse, sin exigir equipos vinculados ni completar todos sus datos en ese momento. Ambas cuentas inician sesión con usuario o correo. El tipo se guarda en `account_type`; los permisos de administración se gestionan por separado y no se pueden solicitar en el registro.

Las empresas publican con su propia identidad, pueden editar su presentación, vincular equipos y organizar torneos. No aparecen en el directorio de jugadores ni se inscriben como jugadores en plantillas o torneos. Sus publicaciones y torneos figuran en su perfil. Las cuentas existentes conservan su acceso; los perfiles de sponsor anteriores siguen siendo editables por su propietario. Los nuevos sponsors se crean desde el registro de empresa.

Solo una sesión administradora puede crear otros administradores desde el panel o `POST /api/admin/admins`. Sus contraseñas requieren al menos 20 caracteres y diversidad de caracteres. Las contraseñas se derivan con scrypt y las sesiones usan cookies HttpOnly.

## Perfiles y rangos

- Los juegos preferidos aparecen juntos en un bloque por juego, con su rango actual y el pico cuando el proveedor lo entrega.
- Los rangos no se pueden editar manualmente ni enviar como parte del perfil.
- En equipos, el juego de competencia define qué rango se muestra para cada integrante. El selector de la plantilla permite consultar los otros juegos del equipo.
- Los filtros de rango consultan el rango del juego seleccionado.
- Desde **Mi perfil → Cuentas de juego** se declara una cuenta, se autoriza la consulta y se sincronizan sus estadísticas. Esto no verifica la propiedad de la cuenta mediante OAuth.
- Si la consulta falla se conserva el último dato de esa misma cuenta y cola, marcado como anterior; cambiar de cuenta o cola no reutiliza el rango previo.

| Juego | Fuente implementada | Rango actual y pico |
| --- | --- | --- |
| League of Legends | Riot Account-V1 y League-V4 | Actual por Solo/Duo o Flex; la respuesta no contiene pico histórico. Requiere `RIOT_API_KEY`. |
| Valorant | HenrikDev MMR v3 | Actual y pico del proveedor. Requiere `HENRIK_API_KEY`; cuota compartida de 30 consultas/minuto. Es independiente de Riot. |
| Counter-Strike 2 | Steam Web API o FACEIT | Steam permite consultar la cuenta, pero no publica rango Premier. FACEIT entrega su propio nivel y Elo con `FACEIT_API_KEY`; no es Premier. |
| Fortnite | Osirion | Actual y máximo de la temporada vigente, por Battle Royale o Cero construcción. No requiere iniciar sesión en Epic durante la beta pública. |
| Rocket League | Pendiente de proveedor autorizado | Se indica la ausencia de una fuente de rangos configurada. |
| EA Sports FC | Pendiente de acceso de partner | Se indica la ausencia de una fuente de rangos configurada. |

Las claves se configuran únicamente en `Docker/.env` y se pasan al backend; nunca se usan variables `NEXT_PUBLIC_*`. La clave de Riot tiene un limitador compartido de 20 peticiones/segundo y 100/2 minutos; HenrikDev admite un máximo compartido de 30/minuto. Además cada jugador puede actualizar un juego una vez por minuto. Los errores del proveedor se muestran sin revelar claves. Puedes comprobar el acceso de Valorant con `respect-backend/venv/Scripts/python scripts/check_provider_access.py --provider henrik` y el de LoL con `--provider riot`, sin consultar perfiles de jugadores.

La clave suministrada para `https://prod.api-fortnite.com/api/v1/profile/ranked` queda en `FORTNITE_API_KEY`, disponible únicamente en el backend. Este proveedor documenta el encabezado `x-api-key`, no `Authorization`. La comprobación con ese encabezado respondió `401 / Invalid or inactive API key`; hace falta activar o sustituir la clave antes de validar sus respuestas de rangos. El conector activo sigue usando Osirion. Ejecuta `respect-backend/venv/Scripts/python scripts/check_fortnite_access.py` para volver a comprobar el acceso sin mostrar la credencial. Consulta [fuentes y requisitos](docs/rank-integrations.md).

## Reportes y administración

Los jugadores pueden reportar perfiles de jugadores, equipos y empresas, y también publicaciones. Los capitanes y administradores de sponsors pueden publicar como sus entidades, por lo que sus publicaciones se reportan a la entidad correspondiente.

Cada reporte guarda categoría, razón, fecha y una copia del contenido reportado. Se permite un reporte pendiente por usuario y perfil; no se permite reportarse a uno mismo ni a una entidad propia. La identidad de quien reporta solo está disponible para administradores.

El panel presenta perfiles con **más de 5 reportes pendientes**, es decir, al menos 6 de usuarios diferentes. Un administrador puede:

1. Revisar razones y evidencia de cada publicación.
2. Suspender al jugador, equipo o empresa con una justificación.
3. Descartar los reportes revisados cuando no corresponda una suspensión.
4. Restablecer el acceso tras una revisión posterior.
5. Consultar el historial de decisiones y crear otras cuentas administradoras.

La suspensión de un jugador invalida sus sesiones y bloquea nuevos accesos. Los perfiles suspendidos y sus publicaciones dejan de aparecer públicamente. Suspender una empresa con cuenta propia también revoca sus sesiones y bloquea su acceso hasta que se restablezca. Una suspensión de equipo o de un sponsor anterior administrado por un jugador afecta a la entidad y conserva el acceso personal de su propietario. La evidencia permanece disponible en administración.

## Limpieza explícita

La entrega se deja con una sola cuenta administradora y sin datos de ejemplo o pruebas. El comando de mantenimiento siguiente borra los datos de la aplicación y vuelve a crear únicamente el administrador configurado; no elimina usuarios internos de MongoDB ni el volumen:

```powershell
docker compose --env-file Docker/.env -f Docker/docker-compose.yml exec -T backend python scripts/reset_to_admin.py --apply
```

Este comando se ejecuta solo de forma explícita. No ocurre al reiniciar. Antes de borrar, valida que la contraseña administradora sea segura y que la base sea `respectdb`.

## Arquitectura

`main.py` compone la aplicación. Cada módulo conserva el esqueleto `controller`, `services`, `repository` y sus esquemas de validación:

```text
respect-backend/
  core/                    configuración, autorización y arranque inicial
  store.py                 adaptador compartido MongoDB / SQLite
  modules/
    auth/                  registro, sesiones y credenciales
    players/               perfiles y conexiones
    teams/                 plantillas, capitanes y solicitudes
    sponsors/              organizaciones y equipos vinculados
    publications/          publicaciones, autores, comentarios y reacciones
    tournaments/           cupos, inscripciones, llaves y resultados
    game_accounts/         proveedores externos y estadísticas por juego
    reports/               reportes y evidencia
    admins/                permisos, decisiones y auditoría
```

La API usa un proceso/worker para serializar cambios compartidos. Antes de escalar a varias réplicas, esas operaciones deben convertirse en transacciones o actualizaciones condicionales de MongoDB. Las partidas y premios se coordinan fuera de Respect+; no se procesan pagos.

## Desarrollo y comprobación

Sin MongoDB configurado, la API usa SQLite persistente en `respect-backend/data/respect.db`. Para desarrollo configura las variables `BOOTSTRAP_ADMIN_*` en el entorno antes de ejecutar Uvicorn. El frontend usa `BACKEND_URL=http://127.0.0.1:8000` por defecto.

```powershell
cd respect-backend
./venv/Scripts/python -m pip install -r requirements.txt
./venv/Scripts/python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

```powershell
cd respect-frontend
npm ci
npm run dev
```

```powershell
cd respect-backend
./venv/Scripts/python -m unittest discover -s tests -v
```

```powershell
cd respect-frontend
npm run build
npx tsc --noEmit
```

Las pruebas de backend crean bases temporales y las eliminan al finalizar. Después de compilar el frontend, ejecuta desde la raíz `respect-backend/venv/Scripts/python scripts/run_isolated_e2e.py` para las pruebas de navegador: el helper arranca servidores en puertos independientes, crea una base temporal sin claves de terceros y elimina esa base al detenerlos. También puedes preparar una instancia aislada nueva y ejecutar `npm run test:e2e` con `E2E_BASE_URL` y `E2E_ADMIN_PASSWORD`. En Windows usan Chrome instalado. Las capturas quedan en `tmp/qa/`.
