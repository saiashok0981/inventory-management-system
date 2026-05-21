const token = localStorage.getItem("token");
const sessionId = localStorage.getItem("sessionId");
const urlParams = new URLSearchParams(window.location.search);
let sessionFromUrl = urlParams.get("t");

function validateAndPreventCache() {
    if (!token || !sessionId) {
        localStorage.clear();
        sessionStorage.clear();
        window.location.href = "/?t=" + Date.now();
        return false;
    }
    
    // If sessionId is missing from URL, use the stored one (allows navigation without URL params)
    if (!sessionFromUrl) {
        sessionFromUrl = sessionId;
        // Update URL to include sessionId for consistency
        window.history.replaceState({}, '', window.location.pathname + '?t=' + sessionId);
    }
    
    if (sessionFromUrl !== sessionId) {
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

if (!validateAndPreventCache()) {
    document.documentElement.innerHTML = "";
    throw new Error("Session invalid");
}

let allDeletions = [];

function parseJwt(token) {
    return JSON.parse(atob(token.split('.')[1]));
}

const payload = parseJwt(token);
const userRole = payload.role;
document.getElementById("userRole").innerText = `Role: ${userRole}`;

if (userRole !== 'admin' && userRole !== 'super-admin') {
    alert("You don't have permission to view deletion logs");
    window.location.href = "/static/dashboard.html?t=" + sessionId;
}

// Update navbar links with sessionId
document.querySelectorAll('a[href*="/static/"]').forEach(link => {
    if (link.href.includes('logout') || link.onclick) return;
    const href = link.getAttribute('href');
    if (!href.includes('?')) {
        link.href = href + '?t=' + sessionId;
    }
});

window.addEventListener('pageshow', function(event) {
    validateAndPreventCache();
});

async function loadDeletionLogs() {

    const response = await fetch("/projects/admin/deletion-logs", {
        headers: { "Authorization": `Bearer ${token}` }
    });

    if (response.status === 401) {
        logout();
        return;
    }

    if (response.status === 403) {
        alert("You don't have permission to view deletion logs");
        window.location.href = "/static/dashboard.html?t=" + sessionId;
        return;
    }

    allDeletions = await response.json();

    const table = document.getElementById("deletionTable");
    table.innerHTML = "";

    if (allDeletions.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="10" style="text-align: center; padding: 20px;">
                    No deletion records found
                </td>
            </tr>
        `;
        return;
    }

    allDeletions.forEach(log => {
        table.innerHTML += `
            <tr>
                <td>${log.id}</td>
                <td>${log.asset}</td>
                <td>${log.serial_no}</td>
                <td>${log.location || '-'}</td>
                <td>${log.assigned_to || '-'}</td>
                <td>${log.room_no || '-'}</td>
                <td>${log.division}</td>
                <td>${log.asset_owner}</td>
                <td>${log.model}</td>
                <td>
                    <span class="status-pill status-${log.network_on.replace('-', '')}">
                        ${log.network_on}
                    </span>
                </td>
                <td>${log.status}</td>
                <td>${log.deleted_by}</td>
                <td>${new Date(log.deleted_at).toLocaleString()}</td>
            </tr>
        `;
    });
}

function filterLogs() {
    const value = document.getElementById("searchInput").value.toLowerCase();
    const rows = document.querySelectorAll("#deletionTable tr");
    rows.forEach(row => {
        row.style.display =
            row.innerText.toLowerCase().includes(value) ? "" : "none";
    });
}

function logout() {
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = "/?t=" + Date.now();
}

loadDeletionLogs();
