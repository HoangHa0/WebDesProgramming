async function handleLogin() {
    try {
        const response = await fetch("http://127.0.0.1:8000/login", {
            method: "POST",
            credentials: "include",
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error logging in:", error);
    }
}

async function fetchUsers() {
    try {
        const response = await fetch("http://127.0.0.1:8000/admin/items", {
            credentials: "include",
        });
        if (!response.ok) {
            throw new Error(`Request failed: ${response.status}`);
        }
        const items = await response.json();
        return items;
    } catch (error) {
        console.error("Error fetching users:", error);
        return [];
    } 
}

async function renderUsers() {
    const data = await fetchUsers();

    let tableBody = document.querySelector("#user-table-body");
    tableBody.textContent = ""; // Clear existing table rows

    data.forEach((user) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${user.id}</td>
            <td>${user.name}</td>
            <td>${user.price}</td>
        `;
        tableBody.appendChild(row);
    });
}
