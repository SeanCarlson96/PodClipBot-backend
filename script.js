const trimForm = document.getElementById("trim-form");
const trimButton = document.getElementById("trim-button");

trimButton.addEventListener("click", (event) => {
	event.preventDefault();

	// Get the video file and timestamps from the form
	const videoFile = document.getElementById("video-file").files[0];
	const startTime = document.getElementById("start-time").value;
	const endTime = document.getElementById("end-time").value;

	// Check that the user has entered valid timestamps
	if (isNaN(startTime) || isNaN(endTime)) {
		alert("Please enter valid start and end times.");
		return;
	}

	// Create a new FormData object and append the video file and timestamps
	const formData = new FormData();
	formData.append("videoFile", videoFile);
	formData.append("startTime", startTime);
	formData.append("endTime", endTime);

	// Send an AJAX request to the server to trim the video
	const xhr = new XMLHttpRequest();
	xhr.open("POST", "/trim");
	xhr.onload = () => {
		if (xhr.status === 200) {
			alert("Video trimmed successfully.");
		} else {
			alert("Error trimming video.");
		}
	};
	xhr.send(formData);
});
