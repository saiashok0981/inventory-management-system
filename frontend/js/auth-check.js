/**
 * Central Authentication & Session validation check
 * Shared across frontend files to enforce DRY principles.
 */

function validateAndPreventCache() {
    const token = localStorage.getItem("token");
    const sessionId = localStorage.getItem("sessionId");
    const urlParams = new URLSearchParams(window.location.search);
    const sessionFromUrl = urlParams.get("t");
    
    if (!token || !sessionId) {
        localStorage.clear();
        sessionStorage.clear();
        window.location.href = "/?t=" + Date.now();
        return false;
    }
    
    if (sessionFromUrl && sessionFromUrl !== sessionId) {
        localStorage.clear();
        sessionStorage.clear();
        window.location.href = "/?t=" + Date.now();
        return false;
    }
    
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const currentTime = Math.floor(Date.now() / 1000);
        if (payload.exp < currentTime) {
            localStorage.clear();
            sessionStorage.clear();
            window.location.href = "/?t=" + Date.now();
            return false;
        }
    } catch (e) {
        localStorage.clear();
        sessionStorage.clear();
        window.location.href = "/?t=" + Date.now();
        return false;
    }
    return true;
}

// Execute immediately upon inclusion to prevent flash of unauthenticated content
if (!validateAndPreventCache()) {
    document.documentElement.innerHTML = "";
    throw new Error("Session invalid");
}
