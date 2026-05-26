// Variables para almacenar datos
let instagramData = {
    username: 'No disponible',
    userId: 'No disponible',
    cookies: []
};

// Esperar a que el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    initializePopup();
});

// Función de inicialización
function initializePopup() {
    const copyBtn = document.getElementById('copyBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const messageDiv = document.getElementById('message');

    // Agregar event listeners a los botones
    copyBtn.addEventListener('click', copyToClipboard);
    downloadBtn.addEventListener('click', downloadJSON);

    // Verificar que estamos en Instagram y extraer datos
    checkAndExtractData();
}

// Función para verificar si estamos en Instagram y extraer datos
function checkAndExtractData() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const currentTab = tabs[0];

        // Verificar si la URL es de Instagram
        if (!currentTab.url.includes('instagram.com')) {
            showMessage('⚠️ Por favor abre Instagram para usar esta extensión', 'error');
            disableButtons();
            updateStatus('No estás en Instagram', 'Detectando...', 'Detectando...');
            return;
        }

        // Actualizar estado a "Extrayendo datos..."
        updateStatus('Extrayendo datos...', 'Detectando...', 'Detectando...');

        // Primero, obtener las cookies
        chrome.cookies.getAll({ domain: '.instagram.com' }, (cookies) => {
            if (cookies.length === 0) {
                showMessage('⚠️ No se encontraron cookies. Asegúrate de estar logueado en Instagram', 'error');
                updateStatus('Sin cookies', 'No disponible', 'No disponible');
                return;
            }

            instagramData.cookies = cookies;
            const cookiesJson = JSON.stringify(cookies, null, 2);
            document.getElementById('cookiesJson').value = cookiesJson;
            document.getElementById('cookiesCountStatus').textContent = cookies.length;

            // Ahora obtener información adicional del content script
            chrome.tabs.sendMessage(currentTab.id, { action: 'getInstagramData' }, (response) => {
                if (chrome.runtime.lastError) {
                    console.log('No se pudo obtener datos del content script:', chrome.runtime.lastError);
                    // Intentar extraer el username de las cookies
                    extractDataFromCookies();
                } else if (response) {
                    instagramData.username = response.username || 'No disponible';
                    instagramData.userId = response.userId || 'No disponible';
                    updateUIWithData();
                }
            });
        });
    });
}

// Función para extraer datos de las cookies
function extractDataFromCookies() {
    // Buscar la cookie 'ds_user_id' que contiene el User ID
    const dsUserIdCookie = instagramData.cookies.find(cookie => cookie.name === 'ds_user_id');
    if (dsUserIdCookie) {
        instagramData.userId = dsUserIdCookie.value;
    }

    updateUIWithData();
}

// Función para actualizar la UI con los datos
function updateUIWithData() {
    document.getElementById('username').value = instagramData.username;
    document.getElementById('userId').value = instagramData.userId;

    updateStatus('✅ Datos extraídos correctamente', instagramData.username, instagramData.userId);

    // Mostrar mensaje de éxito solo si no se mostró error
    if (instagramData.cookies.length > 0) {
        showMessage(`✅ Datos extraídos: ${instagramData.cookies.length} cookies encontradas`, 'success');
    }
}

// Función para actualizar el estado visual
function updateStatus(status, username, userId) {
    document.getElementById('statusText').textContent = status;
    document.getElementById('usernameStatus').textContent = username;
    document.getElementById('userIdStatus').textContent = userId;

    // Ocultar spinner si los datos están completos
    if (status.includes('✅') || status.includes('Sin cookies')) {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
}

// Función para copiar al portapapeles
function copyToClipboard() {
    const cookiesJson = document.getElementById('cookiesJson').value;

    if (!cookiesJson || cookiesJson.trim() === '') {
        showMessage('❌ No hay datos para copiar', 'error');
        return;
    }

    // Usar la API del navegador para copiar
    navigator.clipboard.writeText(cookiesJson).then(() => {
        showMessage('✅ JSON copiado al portapapeles', 'success');

        // Cambiar el texto del botón temporalmente
        const copyBtn = document.getElementById('copyBtn');
        const originalText = copyBtn.textContent;
        copyBtn.textContent = '✓ ¡Copiado!';

        setTimeout(() => {
            copyBtn.textContent = originalText;
        }, 2000);
    }).catch((err) => {
        console.error('Error al copiar:', err);
        showMessage('❌ Error al copiar al portapapeles', 'error');
    });
}

// Función para descargar el archivo JSON
function downloadJSON() {
    const cookiesJson = document.getElementById('cookiesJson').value;
    const username = document.getElementById('username').value || 'instagram_data';

    if (!cookiesJson || cookiesJson.trim() === '') {
        showMessage('❌ No hay datos para descargar', 'error');
        return;
    }

    try {
        // Crear un objeto con toda la información
        const dataToDownload = {
            username: instagramData.username,
            userId: instagramData.userId,
            cookieCount: instagramData.cookies.length,
            extractedAt: new Date().toISOString(),
            cookies: instagramData.cookies
        };

        const jsonString = JSON.stringify(dataToDownload, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        // Crear nombre del archivo con timestamp
        const timestamp = new Date().toISOString().split('T')[0];
        const filename = `instagram_cookies_${username}_${timestamp}.json`;

        // Crear un elemento <a> temporal para descargar
        const downloadLink = document.createElement('a');
        downloadLink.href = url;
        downloadLink.download = filename;
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);

        // Limpiar la URL del blob
        URL.revokeObjectURL(url);

        showMessage(`✅ Archivo descargado: ${filename}`, 'success');
    } catch (err) {
        console.error('Error al descargar:', err);
        showMessage('❌ Error al descargar el archivo', 'error');
    }
}

// Función para mostrar mensajes
function showMessage(text, type = 'info') {
    const messageDiv = document.getElementById('message');
    const warningText = document.getElementById('warningText');

    messageDiv.textContent = text;
    messageDiv.className = `message show ${type}`;

    // Mostrar advertencia si no hay datos
    if (type === 'error' && !instagramData.cookies.length) {
        warningText.classList.add('show');
    }

    // Auto-ocultar después de 5 segundos (excepto errores)
    if (type !== 'error') {
        setTimeout(() => {
            messageDiv.classList.remove('show');
        }, 5000);
    }
}

// Función para desabilitar botones
function disableButtons() {
    document.getElementById('copyBtn').disabled = true;
    document.getElementById('downloadBtn').disabled = true;
}
