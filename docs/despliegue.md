# Despliegue gratuito de la demo

Repositorio: https://github.com/JuanHuamaniVasquez/Alma

## 1. PostgreSQL en Neon

Crear un proyecto en el plan Free y copiar la conexión PostgreSQL con `sslmode=require`.
Configurar esa conexión como `DATABASE_URL` en Render. No guardarla en GitHub ni en este documento.
La base nueva contendrá solo la demo; no se copia ninguna base local ni autorreporte personal.

## 2. API en Render

Crear un Blueprint desde el repositorio (rama `main`); usa `render.yaml` de la raíz.
El único servicio definido es `alma-api`, plan `free`. Introducir `DATABASE_URL` cuando lo pida.
Render genera `DJANGO_SECRET_KEY` e inyecta su hostname permitido automáticamente.
La raíz del servicio es la raíz del repositorio, no `backend/`: el servidor también lee `src/`, `data/` y `docs/actas/`.

El build instala las dependencias bloqueadas y descarga el registro público 100 de PhysioNet.
Cada archivo debe coincidir con el SHA-256 ya registrado en `src/ingesta/ecg_mitbih.py`.
`.gitattributes` preserva los bytes de actas y datos para no romper sus hashes al clonar en Windows.
El arranque aplica migraciones y ejecuta los tres comandos de siembra idempotentes existentes:
hábitat SIMULADO, cierres SIMULADOS y estados REALES derivados del extracto LifeSnaps versionado.
Este extracto no equivale al dataset completo; no se inventan estados para personas sin datos.
Después arranca Gunicorn. `/healthz/` comprueba que PostgreSQL responde sin mostrar credenciales.

Copiar la URL HTTPS real que asigne Render una vez que el servicio esté sano.
Render Free se suspende por inactividad y puede tardar en responder al despertar.
Su disco es efímero: cachés y nuevas lecturas crudas locales se pierden al reiniciar; los datos PostgreSQL permanecen en Neon.
Para conservar a largo plazo las lecturas crudas nuevas se requiere almacenamiento externo; esta demo no lo configura.

## 3. Interfaz en Vercel

Importar el mismo repositorio, plan Hobby, framework Next.js y **Root Directory = `web`**.
Usar Node 22 y configurar `ALMA_API_URL` con la URL HTTPS real de Render, sin `/api` al final.
Aplicarla a Production y Preview. Esta variable se incorpora al build; cambiarla requiere redesplegar.
`web/vercel.json` y `packageManager` fijan los comandos y pnpm.
La interfaz usa `/api/` en su propio dominio; Next.js la reenvía a Render, sin necesitar CORS.
Vercel asigna una dirección `vercel.app`, sin comprar dominio.

## Verificación tras publicar

- Render: `/healthz/` devuelve `{"status":"ok"}`.
- Vercel: `/api/libro/dias/` devuelve los días de la demo.
- Abrir Medical Module, The Leak y The Vault; comprobar modelos, audio y recibos.
- `/api/ecg/` devuelve el registro REAL con atribución, no una señal simulada.
- No probar la captura de ánimo con datos inventados en la base pública.

Referencias: [Render Django](https://render.com/docs/deploy-django),
[Render Free](https://render.com/docs/free),
[Vercel monorepos](https://vercel.com/docs/monorepos).

## Validación local (2026-11-15)

- Build de Next.js con Node 22: correcto; 6 pruebas unitarias del buscador correctas.
- Suite Python: 459 pruebas correctas, 10 omitidas, 5 fallidas y 3 errores.
  Las 8 incidencias se reproducen en una copia limpia de `4e579c1`: faltan 10 lecturas
  crudas históricas mencionadas en el manifiesto y excluidas de Git. No se modifican
  hashes, manifiestos ni pruebas para ocultar esta falta de datos. El código de despliegue
  y la integridad de las actas pasan las pruebas.
- `manage.py check --deploy` no encuentra errores; quedan los avisos opcionales de
  HSTS para subdominios y preload, que no se activan para un subdominio prestado.
- Publicación pendiente de conectar las cuentas de Vercel, Render y Neon.
- Scripts de build y arranque ejecutados con Python 3.12 y PostgreSQL 17 aislada:
  migraciones, siembras y Gunicorn correctos. HTTP 200 en `/healthz/`, `/api/libro/dias/`,
  `/api/demo-kill/`, `/api/actas/`, `/api/ecg/` y `/api/indicadores/`.
