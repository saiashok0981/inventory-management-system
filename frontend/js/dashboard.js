const token = localStorage.getItem("token");
const sessionId = localStorage.getItem("sessionId");
const urlParams = new URLSearchParams(window.location.search);
const sessionFromUrl = urlParams.get("t");

function validateAndPreventCache() {
    if (!token || !sessionId) {
        localStorage.clear();
        sessionStorage.clear();
        window.location.href = "/?t=" + Date.now();
        return false;
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

let allProjects = [];

function parseJwt(token) {
    return JSON.parse(atob(token.split('.')[1]));
}

const payload = parseJwt(token);
const userRole = payload.role;
document.getElementById("userRole").innerText = `Role: ${userRole}`;

// Update navbar links with sessionId
document.querySelectorAll('a[href*="/static/"]').forEach(link => {
    if (link.href.includes('logout') || link.onclick) return;
    const href = link.getAttribute('href');
    if (!href.includes('?')) {
        link.href = href + '?t=' + sessionId;
    }
});

// Update deleted logs link visibility
const deletedLogsLink = document.getElementById("deletedLogsLink");
if (userRole === 'admin' || userRole === 'super-admin') {
    deletedLogsLink.style.display = "inline";
    deletedLogsLink.href = '/static/deleted-logs.html?t=' + sessionId;
}

window.addEventListener('pageshow', function(event) {
    validateAndPreventCache();
});

async function loadProjects() {

    const response = await fetch("/projects", {
        headers: { "Authorization": `Bearer ${token}` }
    });

    if (response.status === 401) {
        logout();
        return;
    }

    allProjects = await response.json();

    updateStats();

    const table = document.getElementById("projectTable");
    table.innerHTML = "";

    allProjects.forEach(project => {
        let actionButtons = '';
        
        if (userRole === 'super-admin' || userRole === 'admin') {
            actionButtons = `<button onclick="viewHistory(${project.id})">History</button>`;
        }
        
        if (userRole === 'super-admin') {
            actionButtons += `<button onclick="editProject(${project.id})">Edit</button>`;
            actionButtons += `<button class="danger-btn" onclick="deleteProject(${project.id})">Delete</button>`;
        }

        table.innerHTML += `
            <tr>
                <td>${project.display_id}</td>
                <td>${project.asset}</td>
                <td>${project.serial_no}</td>
                <td>${project.location || '-'}</td>
                <td>${project.assigned_to || '-'}</td>
                <td>${project.room_no || '-'}</td>
                <td>${project.division}</td>
                <td>${project.asset_owner}</td>
                <td>${project.model}</td>
                <td>
                    <span class="status-pill status-${project.network_on.replace('-', '')}">
                        ${project.network_on}
                    </span>
                </td>
                <td>${project.status}</td>
                <td>
                    <div class="action-buttons">
                        ${actionButtons}
                    </div>
                </td>
            </tr>
        `;
    });
}

function updateStats() {
    document.getElementById("totalProjects").innerText =
        allProjects.length;

    document.getElementById("activeProjects").innerText =
        allProjects.filter(p => p.network_on === "DRONA").length;

    document.getElementById("completedProjects").innerText =
        allProjects.filter(p => p.network_on === "internet").length;

    document.getElementById("archivedProjects").innerText =
        allProjects.filter(p => p.network_on === "stand-alone").length;
}

function filterProjects() {
    const value = document.getElementById("searchInput").value.toLowerCase();
    const rows  = document.querySelectorAll("#projectTable tr");
    rows.forEach(row => {
        row.style.display =
            row.innerText.toLowerCase().includes(value) ? "" : "none";
    });
}

function editProject(id) {
    window.location.href = `/static/edit.html?id=${id}&t=${sessionId}`;
}

function viewHistory(id) {
    window.location.href = `/static/history.html?id=${id}&t=${sessionId}`;
}

async function deleteProject(id) {
    if (!confirm("Are you sure you want to delete this record?")) return;

    const response = await fetch(`/projects/${id}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
    });

    if (response.ok) {
        alert("Record deleted successfully");
        loadProjects();
    } else {
        alert("Delete failed");
    }
}

function logout() {
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = "/?t=" + Date.now();
}

loadProjects();