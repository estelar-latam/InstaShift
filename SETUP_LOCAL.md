# 🚀 Guía de Ejecución Local de InstaShift

## ✅ Problema Solucionado

El error `IndentationError` en `bot/database.py` **ya ha sido corregido**. La indentación ahora es correcta (4 espacios por nivel).

---

## 📋 Requisitos previos

- **Python 3.10+** → Descargar desde [python.org](https://www.python.org/downloads/)
- **Git** → Descargar desde [git-scm.com](https://git-scm.com/)
- **Token de Discord** → Crear en [discord.com/developers/applications](https://discord.com/developers/applications)
- **Credenciales de Instagram** → Tu usuario y contraseña (cuenta pública recomendada)

---

## 🔧 Instalación en Windows

### Opción 1: Automática (run.sh)

```bash
# 1. Abre PowerShell o CMD en este directorio
# 2. Ejecuta:
bash run.sh
```

Esto automáticamente:
- ✅ Crea un virtual environment
- ✅ Instala dependencias
- ✅ Inicia el bot

### Opción 2: Manual (recomendado para desarrollo)

```bash
# 1. Crear virtual environment
python -m venv .venv

# 2. Activar el ambiente virtual
# En PowerShell:
.\.venv\Scripts\Activate.ps1
# En CMD:
.venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear archivo .env
copy .env.example .env

# 5. Editar .env con tus datos (ver sección abajo)
# Abre .env con tu editor favorito y completa los valores

# 6. Ejecutar el bot
python -m bot.main
```

---

## 🔐 Configuración de .env

### 1. **Discord Token**

```
DISCORD_TOKEN=tu_token_aqui
```

**Cómo obtenerlo:**
1. Ve a https://discord.com/developers/applications
2. Crea una nueva aplicación (o abre una existente)
3. Ve a **Bot** → **Add Bot**
4. Copia el Token bajo **TOKEN**
5. Pégalo en `.env`

### 2. **Guild ID (Opcional, para desarrollo)**

```
GUILD_ID=123456789
```

Deja en blanco para producción. Para desarrollo local, puedes usar el ID de tu servidor de prueba para que los comandos slash aparezcan al instante.

**Cómo obtenerlo:**
- Habilita "Developer Mode" en Discord (User Settings → Advanced → Developer Mode)
- Click derecho en tu servidor → Copy Server ID

### 3. **Credenciales de Instagram**

```
IG_USERNAME=tu_usuario
IG_PASSWORD=tu_contraseña
```

**⚠️ Importante:**
- Usa una **cuenta pública**
- Si tienes autenticación de dos factores, deshabilítala temporalmente
- Las credenciales se guardan en `ig_session.json` (git-ignorado)

### 4. **Database** (para local)

Para desarrollo local, puedes dejar las variables de MySQL en blanco. El bot usará SQLite:

```
DB_PATH=instashift.db
SESSION_PATH=ig_session.json
```

### 5. **Logging**

```
LOG_LEVEL=INFO    # DEBUG, INFO, WARNING, ERROR
CHECK_INTERVAL=10 # Minutos entre verificaciones
```

---

## 🤖 Configuración del Bot en Discord

### Permisos necesarios

1. Ve a https://discord.com/developers/applications
2. Selecciona tu bot
3. En **Bot** → activa:
   - ✅ **Message Content Intent** (para leer mensajes)
   - ✅ **Server Members Intent** (para gestionar roles)
4. En **OAuth2 → URL Generator**:
   - ✅ Selecciona `bot` + `applications.commands`
   - ✅ Selecciona permisos:
     - Send Messages
     - Embed Links
     - Attach Files
     - Read Message History

### Invitar el bot al servidor

1. Usa la URL generada en OAuth2 → URL Generator
2. Selecciona tu servidor de prueba
3. Autoriza permisos

---

## ✅ Verificación

Una vez ejecutes el bot, deberías ver en la consola:

```
[INFO] Bot conectado como: MiBot#1234
[INFO] Versión del bot: X.X.X
[DB] MySQL listo. Pool creado (min=1, max=5).
[INFO] Esperando eventos...
```

En Discord, deberías poder ver:
- Comandos slash disponibles (`/follow`, `/list`, `/preview`, etc.)
- El bot online en tu servidor

---

## 🐛 Solución de problemas

### Error: "No module named 'discord'"

```bash
pip install -r requirements.txt
```

### Error: "DISCORD_TOKEN not found"

Verifica que:
1. Existe el archivo `.env` (no `.env.example`)
2. `DISCORD_TOKEN` está configurado correctamente
3. El archivo `.env` está en el directorio raíz (al lado de `README.md`)

### Error: "IndentationError"

✅ **YA SOLUCIONADO** - El archivo `bot/database.py` ya tiene la indentación correcta.

### Error: "Instagram login failed"

- Verifica credenciales en `.env`
- Desactiva autenticación de dos factores
- Prueba login manual en Instagram en navegador

### Error: "Database connection refused"

Para local, deja las variables MySQL en blanco y usa SQLite.
Si necesitas MySQL, verifica que el servidor esté corriendo.

---

## 🚀 Deployar a Railway

Una vez que funciona localmente:

```bash
# 1. Haz commit y push
git add .
git commit -m "feat: add database fix and local setup"
git push origin main

# 2. En Railway:
#    - Conecta tu repo GitHub
#    - Agrega variables de entorno en el panel
#    - Railway detecta el Dockerfile automáticamente
```

---

## 📞 Ayuda

Si tienes problemas:

1. **Revisa los logs** en la consola
2. **Verifica el `.env`** - es la causa más común
3. **Reinstala dependencias**: `pip install --upgrade -r requirements.txt`
4. **Crea un issue** en GitHub: https://github.com/estelar-latam/InstaShift/issues

---

**¡Listo!** El bot debería estar corriendo. 🎉
