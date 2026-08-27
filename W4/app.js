// alert("Hello from an external JavaScript file!");

// Lab 1
const predictionSamples = [
	{ id: 1, name: "Alice", score: 82 },
	{ id: 2, name: "Ben", score: 67 },
	{ id: 3, name: "Cara", score: 91 },
	{ id: 4, name: "David", score: 74 },
];

const passingSamples = [];

for (const sample of predictionSamples) {
	if (sample.score >= 70) {
		passingSamples.push(sample);
	}
}

function sumField(samples, field) {
	let total = 0;

	for (const sample of samples) {
		total += sample[field];
	}

	return total;
}

function findLargestByField(samples, field) {
	let largest = samples[0];

	for (const sample of samples) {
		if (sample[field] > largest[field]) {
			largest = sample;
		}
	}

	return largest;
}

const sumScores = (samples) => sumField(samples, "score");

console.log("Passing samples:", passingSamples);
console.log("Total score:", sumScores(predictionSamples));
console.log("Largest score:", findLargestByField(predictionSamples, "score"));

// Lab 2
const form = document.querySelector("#contact form");

form.addEventListener("submit", (event) => {
	event.preventDefault();

	const previousMessage = form.querySelector(".form-message");
	previousMessage?.remove();

	const requiredFields = form.querySelectorAll("[required]");
	let errorMessage = "";

	for (const field of requiredFields) {
		if (!field.value.trim()) {
			errorMessage = `${field.name} is required.`;
			break;
		}
	}

	const message = document.createElement("p");
	message.className = "form-message";

	if (errorMessage) {
		message.textContent = errorMessage;
		message.style.color = "red";
	} else {
		message.textContent = "Ready to submit";
		message.style.color = "green";
	}

	form.appendChild(message);
});
