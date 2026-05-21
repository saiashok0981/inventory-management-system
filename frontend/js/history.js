const token = localStorage.getItem("token");
const sessionId = localStorage.getItem("sessionId");
const urlParams = new URLSearchParams(window.location.search);
let sessionFromUrl = urlParams.get("t");
const projectId = urlParams.get("id");

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
        window.history.replaceState({}, '', window.location.pathname + '?t=' + sessionId + (projectId ? '&id=' + projectId : ''));
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

window.addEventListener('pageshow', function(event) {
    validateAndPreventCache();
});

async function loadHistory() {

    const response = await fetch(
        `/projects/${projectId}/history`,
        {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        }
    );

    if (!response.ok) {

        alert("Failed to load history");

        return;
    }

    const logs = await response.json();

    const table =
        document.getElementById("historyTable");

    table.innerHTML = "";

    if (logs.length === 0) {

        table.innerHTML = `
            <tr>
                <td colspan="5">
                    No audit history found
                </td>
            </tr>
        `;

        return;
    }

    logs.forEach(log => {

        table.innerHTML += `

            <tr>

                <td>
                    ${log.field_name}
                </td>

                <td>
                    ${log.old_value ?? "-"}
                </td>

                <td>
                    ${log.new_value ?? "-"}
                </td>

                <td>
                    ${log.changed_by ?? "-"}
                </td>

                <td>
                    ${new Date(
                        log.changed_at
                    ).toLocaleString()}
                </td>

            </tr>
        `;
    });
}

loadHistory();