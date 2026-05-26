# 🍪 Instagram Cookies Extractor

Una extensión de Chrome que extrae automáticamente las cookies de sesión, User ID y username de tu cuenta de Instagram para usar en InstaSwift.

## ✨ Características

- ✅ **Extracción automática de cookies** - Obtiene todas las cookies de sesión de Instagram
- ✅ **Detección de User ID** - Extrae el ID único de tu cuenta
- ✅ **Detección de username** - Identifica automáticamente tu nombre de usuario
- ✅ **Interfaz intuitiva** - Diseño moderno y fácil de usar
- ✅ **Opción de descargar** - Descarga los datos en formato JSON
- ✅ **Opción de copiar** - Copia los datos al portapapeles con un clic
- ✅ **Procesamiento local** - Todo se procesa localmente en tu navegador
- ✅ **Sin servidores externos** - Ningún dato sale de tu computadora
- ✅ **Código abierto** - Puedes revisar todo el código fuente

## 📥 Instalación

### Paso 1: Ubicar la carpeta
La extensión se encuentra en:
```
C:\Users\Douglas Velez\OneDrive\Escritorio\Instaswift\instagram-cookies-extractor
```

### Paso 2: Abrir Chrome
Abre Google Chrome en tu computadora.

### Paso 3: Ir a extensiones
Copia y pega esto en la barra de direcciones:
```
chrome://extensions/
```

O ve a:
1. Menú de Chrome (⋮) → Más herramientas → Extensiones

### Paso 4: Activar Modo de Desarrollador
En la esquina superior derecha, encontrarás un toggle que dice "Modo de desarrollador". 
**Actívalo** (debe estar en azul).

### Paso 5: Cargar extensión sin empaquetar
Haz clic en el botón **"Cargar extensión sin empaquetar"** que aparecerá en la esquina superior izquierda.

### Paso 6: Seleccionar carpeta
Se abrirá una ventana para seleccionar carpeta. Navega a:
```
C:\Users\Douglas Velez\OneDrive\Escritorio\Instaswift\instagram-cookies-extractor
```

Selecciona esa carpeta y haz clic en **"Seleccionar carpeta"**.

### Paso 7: ¡Listo!
La extensión se habrá cargado. Deberías ver el icono 🍪 en la barra de herramientas de Chrome.

## 🚀 Cómo usar

### Paso 1: Abre Instagram
Ve a https://www.instagram.com y asegúrate de que **estés logueado** en tu cuenta.

### Paso 2: Abre la extensión
Haz clic en el icono 🍪 en la barra de herramientas de Chrome (esquina superior derecha).

### Paso 3: Espera a que se extraigan los datos
La extensión buscará automáticamente:
- Tus cookies de sesión
- Tu User ID
- Tu username

Verás el estado actualizado en tiempo real.

### Paso 4: Elige una opción

**Opción A - Copiar JSON:**
- Haz clic en el botón "📋 Copiar JSON"
- El JSON se copiará automáticamente al portapapeles
- Verás un mensaje "✅ Copiado al portapapeles"

**Opción B - Descargar JSON:**
- Haz clic en el botón "⬇️ Descargar JSON"
- Se descargará un archivo JSON con todos tus datos
- El archivo se llamará algo como: `instagram_cookies_tu_usuario_2026-05-26.json`

### Paso 5: Usa en InstaSwift
Ahora puedes usar el JSON descargado o copiado en InstaSwift según sus instrucciones.

## 📁 Estructura de archivos

```
instagram-cookies-extractor/
├── manifest.json          # Configuración de la extensión
├── popup.html            # Interfaz visual del popup
├── popup.js              # Lógica del popup
├── content.js            # Script inyectado en Instagram
├── background.js         # Service Worker de fondo
├── README.md             # Esta documentación
└── icons/               # (Opcional) Iconos de la extensión
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## 🔒 Privacidad y Seguridad

### ✅ Lo que GARANTIZAMOS:
- **Tus cookies NO se envían a servidores externos** - Todo se procesa localmente en tu navegador
- **Los datos se procesan 100% en tu computadora** - Nada sale de aquí
- **Solo funciona en instagram.com** - No puede acceder a otros sitios
- **Código abierto** - Puedes revisar el código fuente en cualquier momento
- **Puedes revocar el acceso en cualquier momento** - Desinstala la extensión cuando quieras

### 🔐 Cómo proteger tus datos:
1. **No compartas el JSON** - El archivo contiene tus cookies de sesión
2. **Mantén el archivo seguro** - Guárdalo en un lugar privado
3. **No lo pegues en sitios desconocidos** - Es como compartir tu contraseña
4. **Regenera tus cookies si algo sale mal** - Cambia tu contraseña de Instagram
5. **Solo usa en plataformas confiables** - InstaSwift debe ser verificado

## ⚠️ Notas Importantes

- **Debes estar logueado en Instagram** para que la extensión funcione
- **Las cookies expiran** - Instagram genera nuevas cookies frecuentemente
- **Tus datos son únicos** - No compartas el JSON con nadie
- **Es solo para uso personal** - No uses esto para acceder a cuentas ajenas
- **Las cookies pueden cambiar** - Si cambias tu contraseña, tendrás que extraerlas de nuevo
- **Guarda tus datos en un lugar seguro** - Estos son datos sensibles

## 🛠️ Solucionar problemas

### ❓ "La extensión no muestra datos"
**Solución:**
1. Asegúrate de estar en https://www.instagram.com (debe decir "Seguro" en la barra)
2. Recarga la página (F5)
3. Asegúrate de estar logueado en Instagram
4. Cierra y vuelve a abrir el popup de la extensión

### ❓ "El icono no aparece"
**Solución:**
1. Verifica que la extensión esté habilitada en `chrome://extensions/`
2. El icono debe estar en la barra de herramientas (esquina superior derecha)
3. Si no ves el icono, busca el icono de extensiones (rompecabezas) y fija la extensión

### ❓ "No puedo descargar el JSON"
**Solución:**
1. Revisa la carpeta de Descargas
2. Asegúrate de tener permisos de escritura en la carpeta
3. Intenta usar "Copiar JSON" en su lugar
4. Reinicia Chrome si persiste el problema

### ❓ "El username dice 'No disponible'"
**Solución:**
1. Recarga Instagram
2. Intenta desde la página de tu perfil
3. Si aún no funciona, puedes escribirlo manualmente
4. Las cookies son lo más importante

### ❓ "Chrome dice que es una extensión no verificada"
**Solución:**
1. Es normal - es una extensión en modo desarrollador
2. Esto solo aparece cuando reinicias Chrome
3. No es un virus ni algo peligroso
4. Simplemente haz clic en el icono para usar la extensión

## 📊 Información Técnica

- **Manifest Version:** 3
- **Compatible con:** Chrome 88+
- **Permisos utilizados:**
  - `cookies` - Para acceder a las cookies
  - `activeTab` - Para detectar la pestaña activa
  - `scripting` - Para inyectar scripts
  - `tabs` - Para información de pestañas
- **Host permissions:**
  - `https://*.instagram.com/*`
  - `https://www.instagram.com/*`

### Archivos incluidos:

1. **manifest.json** - Declaración de permisos y configuración
2. **popup.html** - Interfaz visual (500px de ancho, tema morado)
3. **popup.js** - Lógica de copiar, descargar y gestionar datos
4. **content.js** - Script que extrae datos de Instagram
5. **background.js** - Service Worker para gestionar permisos

## 📝 Formato del JSON descargado

El archivo JSON que descargues tendrá este formato:

```json
{
  "username": "tu_usuario",
  "userId": "123456789",
  "cookieCount": 15,
  "extractedAt": "2026-05-26T14:30:00.000Z",
  "cookies": [
    {
      "name": "sessionid",
      "value": "...",
      "domain": ".instagram.com",
      "path": "/",
      "secure": true,
      "httpOnly": true,
      "sameSite": "Lax",
      "expirationDate": 1234567890
    },
    ...
  ]
}
```

## ❓ Preguntas Frecuentes

**P: ¿Es seguro usar esta extensión?**
R: Sí, es completamente segura. Puedes revisar el código fuente y ver que no hace nada sospechoso.

**P: ¿Se guardan mis datos en la nube?**
R: No, todo se procesa localmente. Nada sale de tu computadora.

**P: ¿Puedo usar esto en múltiples navegadores?**
R: Solo funciona en Chrome. Para Firefox u otros navegadores, necesitarías una versión diferente.

**P: ¿Qué pasa si cambio mi contraseña?**
R: Las cookies se invalidarán y deberás usar la extensión de nuevo para extraerlas.

**P: ¿Puedo usar el mismo JSON en múltiples computadoras?**
R: Técnicamente sí, pero no es recomendado. Es mejor extraer nuevas cookies para cada uso.

**P: ¿Es legal usar esto?**
R: Sí, es legal extraer tus propias cookies. Solo úsalo para tu propia cuenta.

## 🎯 Propósito

Esta extensión fue creada para facilitar la integración entre Instagram e InstaSwift, permitiendo a los usuarios conectar sus cuentas de forma segura y sencilla.

## 📞 Soporte

Si encuentras problemas:
1. Revisa la sección "Solucionar problemas" arriba
2. Asegúrate de seguir los pasos de instalación
3. Verifica que tengas Chrome versión 88 o superior
4. Intenta desinstalar y reinstalar la extensión

## 📄 Licencia

Esta extensión es de código abierto y gratuita. Úsala bajo tu propia responsabilidad.

---

**Última actualización:** 26 de Mayo de 2026

**Versión:** 1.0.0

¡Disfruta! 🚀
