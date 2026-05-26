// Script que se inyecta en Instagram para extraer información adicional

console.log('✅ Instagram Cookies Extractor - Content script cargado');

// Escuchar mensajes desde el popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getInstagramData') {
        const instagramData = extractInstagramData();
        sendResponse(instagramData);
    }
});

// Función para extraer datos de Instagram
function extractInstagramData() {
    const data = {
        username: extractUsername(),
        userId: extractUserId()
    };

    console.log('📊 Datos extraídos de Instagram:', data);
    return data;
}

// Función para extraer el username
function extractUsername() {
    // Intento 1: Buscar en el meta tag og:url
    const ogUrl = document.querySelector('meta[property="og:url"]');
    if (ogUrl) {
        const url = ogUrl.getAttribute('content');
        if (url) {
            const match = url.match(/instagram\.com\/([^/?]+)/);
            if (match && match[1] && match[1] !== 'p' && match[1] !== 'stories') {
                return match[1];
            }
        }
    }

    // Intento 2: Buscar en el meta tag profile URL
    const profileUrl = document.querySelector('meta[property="profile:username"]');
    if (profileUrl) {
        return profileUrl.getAttribute('content');
    }

    // Intento 3: Buscar en los datos de la ventana (window.__data)
    if (window.__data && window.__data.user) {
        return window.__data.user.username;
    }

    // Intento 4: Buscar en los enlaces de perfil
    const profileLinks = document.querySelectorAll('a[href*="/accounts/edit/"]');
    for (let link of profileLinks) {
        const href = link.getAttribute('href');
        if (href) {
            const match = href.match(/\/([^/?]+)/);
            if (match && match[1]) {
                return match[1];
            }
        }
    }

    // Intento 5: Buscar en localStorage
    try {
        const authData = localStorage.getItem('ig_nrcb');
        if (authData) {
            const parsed = JSON.parse(authData);
            if (parsed && parsed.user && parsed.user.username) {
                return parsed.user.username;
            }
        }
    } catch (e) {
        console.log('No se pudo acceder a localStorage');
    }

    return 'No disponible';
}

// Función para extraer el User ID
function extractUserId() {
    // Intento 1: Buscar en sessionStorage
    try {
        const sessionData = sessionStorage.getItem('instagram_user_id');
        if (sessionData) {
            return sessionData;
        }
    } catch (e) {
        console.log('No se pudo acceder a sessionStorage');
    }

    // Intento 2: Buscar en window.__data
    if (window.__data && window.__data.user && window.__data.user.id) {
        return window.__data.user.id;
    }

    // Intento 3: Buscar en los scripts inline de la página
    const scripts = document.querySelectorAll('script');
    for (let script of scripts) {
        if (script.textContent) {
            const match = script.textContent.match(/"id":"(\d+)"/);
            if (match && match[1]) {
                return match[1];
            }
        }
    }

    // Intento 4: Buscar en fetch/XHR (si es posible)
    // Esto es un fallback más débil
    const links = document.querySelectorAll('a[href*="/" + extractUsername() + "/?"]');
    for (let link of links) {
        const href = link.getAttribute('href');
        if (href && href.includes('modal=FOLLOW_LIST')) {
            // En este punto, necesitaríamos hacer una solicitud
            // Para evitar complicaciones, lo dejamos aquí
        }
    }

    return 'No disponible';
}

console.log('✅ Content script listo para extraer datos');
