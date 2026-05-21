async function login() {

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const response = await fetch("/auth/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username,
            password
        })
    });

    const data = await response.json();

    if (response.ok) {
        const sessionId = "session_" + Date.now() + "_" + Math.random();
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("sessionId", sessionId);

        window.location.href = "/static/dashboard.html?t=" + sessionId;

    } else {

        document.getElementById("error").innerText =
            data.detail || "Login failed";
    }
}