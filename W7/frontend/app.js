async function fetchUsers() {
    try {
        const response = await fetch("/items");
        const items = await response.json();
        return items;
    } catch (error) {
        console.error("Error fetching users:", error);
        return [];
    } 
}

async function renderUsers() {
    const userData = await fetchUsers();

    let tableBody = document.querySelector("#user-table-body");
    tableBody.textContent = ""; // Clear existing table rows

    userData.forEach((user) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${user.id}</td>
            <td>${user.name}</td>
            <td>${user.price}</td>
        `;
        tableBody.appendChild(row);
    });
}
