const token = localStorage.getItem("token");
const sessionId = localStorage.getItem("sessionId");
const urlParams = new URLSearchParams(window.location.search);
let sessionFromUrl = urlParams.get("t");
const projectId = urlParams.get("id");

function parseJwt(token) {
    return JSON.parse(atob(token.split('.')[1]));
}

const payload = parseJwt(token);
const userRole = payload.role;
const isEditMode = !!projectId;

// Ensure sessionId is present in URL for consistency
if (sessionId && !sessionFromUrl) {
    sessionFromUrl = sessionId;
    window.history.replaceState({}, '', window.location.pathname + '?t=' + sessionId + (projectId ? '&id=' + projectId : ''));
}

// Only super-admin can edit existing records; all authenticated users can create new ones
if (isEditMode && userRole !== 'super-admin') {
    alert("You don't have permission to edit records");
    window.location.href = "/static/dashboard.html?t=" + sessionId;
}

window.addEventListener('pageshow', function(event) {
    validateAndPreventCache();
});

// Update page title based on mode
document.addEventListener('DOMContentLoaded', function() {
    const titleEl = document.getElementById('pageTitle');
    if (isEditMode) {
        titleEl.innerText = 'Edit Asset';
    } else {
        titleEl.innerText = 'Add Asset';
    }
});

async function loadProject() {

    if (!projectId) return;

    const response = await fetch(`/projects/${projectId}`, {
        headers: { "Authorization": `Bearer ${token}` }
    });

    if (!response.ok) {
        alert("Failed to load record");
        return;
    }

    const project = await response.json();

    document.getElementById("asset").value         = project.asset;
    document.getElementById("serial_no").value     = project.serial_no;
    document.getElementById("location").value      = project.location      || "";
    document.getElementById("assigned_to").value   = project.assigned_to   || "";
    document.getElementById("room_no").value       = project.room_no       || "";
    document.getElementById("division").value      = project.division;
    document.getElementById("asset_owner").value   = project.asset_owner;
    document.getElementById("model").value         = project.model;
    document.getElementById("network_on").value    = project.network_on;
    document.getElementById("status").value        = project.status;
    document.getElementById("procurement").value   = project.procurement   || "";
}

async function saveProject() {
    const serialNo = document.getElementById("serial_no").value.trim();
    const message = document.getElementById("message");

    if (!serialNo) {
        message.className = "error-message";
        message.innerText = "Serial number is required";
        return;
    }

    const payload = {
        asset:       document.getElementById("asset").value,
        serial_no:   serialNo,
        location:    document.getElementById("location").value      || null,
        assigned_to: document.getElementById("assigned_to").value   || null,
        room_no:     document.getElementById("room_no").value       || null,
        division:    document.getElementById("division").value,
        asset_owner: document.getElementById("asset_owner").value,
        model:       document.getElementById("model").value,
        network_on:  document.getElementById("network_on").value,
        status:      document.getElementById("status").value,
        procurement: document.getElementById("procurement").value   || null
    };

    let response;

    if (projectId) {
        response = await fetch(`/projects/${projectId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });
    } else {
        response = await fetch("/projects", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });
    }

    if (response.ok) {
        message.className  = "success-message";
        message.innerText  = "Saved successfully";
        setTimeout(() => {
            window.location.href = "/static/dashboard.html?t=" + sessionId;
        }, 1200);
    } else {
        const error       = await response.json();
        message.className = "error-message";
        message.innerText = error.detail || "Operation failed";
    }
}

loadProject();