const token = localStorage.getItem("token");
const sessionId = localStorage.getItem("sessionId");
const urlParams = new URLSearchParams(window.location.search);
let sessionFromUrl = urlParams.get("t");
const projectId = urlParams.get("id");

// Ensure sessionId is present in URL for consistency
if (sessionId && !sessionFromUrl) {
    sessionFromUrl = sessionId;
    window.history.replaceState({}, '', window.location.pathname + '?t=' + sessionId + (projectId ? '&id=' + projectId : ''));
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