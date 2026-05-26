// Service Worker de la extensión Instagram Cookies Extractor

console.log('✅ Background Service Worker cargado');

// Escuchar la instalación de la extensión
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('✅ Instagram Cookies Extractor instalado');
    } else if (details.reason === 'update') {
        console.log('✅ Instagram Cookies Extractor actualizado a la nueva versión');
    }
});

// Escuchar mensajes desde otros scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    // Manejo de solicitudes de cookies
    if (request.action === 'getCookies') {
        chrome.cookies.getAll({ domain: '.instagram.com' }, (cookies) => {
            sendResponse({ cookies: cookies });
        });
        return true; // Indica que la respuesta es asincrónica
    }

    // Manejo de solicitudes de descarga
    if (request.action === 'downloadFile') {
        const { filename, content } = request;

        // Crear un blob con el contenido
        const blob = new Blob([content], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        // Usar la API de descarga
        chrome.downloads.download({
            url: url,
            filename: filename,
            saveAs: true
        }, (downloadId) => {
            sendResponse({ success: true, downloadId: downloadId });
        });

        return true; // Indica que la respuesta es asincrónica
    }

    // Manejo de cualquier otro mensaje
    if (request.action === 'getStatus') {
        sendResponse({ status: 'ready' });
    }
});

// Escuchar cambios en las cookies (opcional, para logging)
chrome.cookies.onChanged.addListener((changeInfo) => {
    if (changeInfo.cookie.domain.includes('instagram.com')) {
        console.log('🍪 Cambio en cookie de Instagram detectado:', changeInfo.cookie.name);
    }
});

console.log('✅ Background Service Worker listo');
