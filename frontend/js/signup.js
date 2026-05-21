async function signup() {

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const confirm_password = document.getElementById("confirm_password").value;
    const role = document.getElementById("role").value;

    document.getElementById("error").innerText = "";
    document.getElementById("success").innerText = "";

    if (!username || !password || !confirm_password || !role) {
        document.getElementById("error").innerText = "All fields are required";
        return;
    }

    const response = await fetch("/auth/signup", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username,
            password,
            confirm_password,
            role
        })
    });

    const data = await response.json();

    if (response.ok) {
        const sessionId = "session_" + Date.now() + "_" + Math.random();
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("sessionId", sessionId);

        document.getElementById("success").innerText = "Account created successfully! Redirecting to dashboard...";

        setTimeout(() => {
            window.location.href = "/static/dashboard.html?t=" + sessionId;
        }, 1500);

    } else {

        document.getElementById("error").innerText =
            data.detail || "Signup failed";
    }
}
