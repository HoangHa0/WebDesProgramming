// fetch("https://jsonplaceholder.typicode.com/users")
// .then(function(response) {
//     return response.json();
// })
// .then(function(users) {
//     console.log("Fetch Users:", users); // parsed array of users
// })
// .catch(function(error) {
//     console.error("Something went wrong: ", error);
// });


// async function fetchUsers() {
// 	return "Hello!";
// }

// async function fetchUsers() {
// 	try {
// 		const reponse = await fetch("https://jsonplaceholder.typicode.com/users");
// 		const users = await reponse.json();
// 		// console.log("Fetch Users:", users); // parsed array of users
// 		return users;
// 	}
// 	catch (error) {
// 		console.error("Something went wrong: ", error);
// 	}
// }

// let userData = fetchUsers();
// console.log("User Data:", userData); // Promise { <pending> }

// fetchUsers().then((data) => console.log("User Data:", data)); // parsed array of users

async function loadUsers() {
    try {
        const response = await fetch("https://jsonplaceholder.typicode.com/users");
        const users = await response.json();
        
        const tbody = document.querySelector("#user-table-body");
        users.forEach((user) => {
            const row = document.createElement("tr");
            
            row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.name}</td>
                <td>${user.address.street}, ${user.address.city}</td>
                <td>${user.email}</td>
                <td>${user.phone}</td>
            `;
            
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

loadUsers();