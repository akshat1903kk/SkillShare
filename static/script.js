document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "http://localhost:8000"; // Update this to match your FastAPI backend
    const jobList = document.getElementById("jobList");
    const searchBar = document.getElementById("searchBar");
    const createJobBtn = document.getElementById("createJobBtn");
    const logoutBtn = document.getElementById("logoutBtn");

    const token = localStorage.getItem("token");

    // Redirect to login if token is missing
    if (!token) {
        window.location.href = "/login.html"; // Change this if your login page has a different path
    }

    // Fetch and display jobs from the backend
    async function fetchJobs(location = "") {
        let url = `${API_URL}/jobs/`;
        if (location) {
            url = `${API_URL}/jobs/apply/${location}`; // API route for location-based search
        }

        try {
            const response = await fetch(url, {
                headers: { "Authorization": `Bearer ${token}` }
            });

            if (response.status === 401) {
                alert("Session expired. Please log in again.");
                logout();
            }

            const jobs = await response.json();
            displayJobs(jobs);
        } catch (error) {
            console.error("Error fetching jobs:", error);
        }
    }

    // Render jobs in the UI
    function displayJobs(jobs) {
        jobList.innerHTML = ""; // Clear previous jobs

        if (jobs.length === 0) {
            jobList.innerHTML = "<p>No jobs found.</p>";
            return;
        }

        jobs.forEach(job => {
            const jobCard = document.createElement("div");
            jobCard.classList.add("job-card");
            jobCard.innerHTML = `
                <h3>${job.title}</h3>
                <p>${job.description}</p>
                <p><strong>Location:</strong> ${job.location}</p>
                <button class="applyBtn" data-id="${job.id}">Apply</button>
            `;
            jobList.appendChild(jobCard);
        });

        // Attach event listeners to apply buttons
        document.querySelectorAll(".applyBtn").forEach(button => {
            button.addEventListener("click", applyForJob);
        });
    }

    // Apply for a job
    async function applyForJob(event) {
        const jobId = event.target.dataset.id;

        try {
            const response = await fetch(`${API_URL}/jobs/apply/${jobId}`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ applied_at: new Date().toISOString() }) // Send timestamp
            });

            const result = await response.json();
            alert(result.message);
            fetchJobs(); // Refresh job list
        } catch (error) {
            console.error("Error applying for job:", error);
        }
    }

    // Search jobs by location
    searchBar.addEventListener("input", () => {
        const query = searchBar.value.trim();
        fetchJobs(query); // Fetch jobs based on location search
    });

    // Logout function
    function logout() {
        localStorage.removeItem("token"); // Remove token
        window.location.href = "/login.html"; // Redirect to login page
    }

    // Handle logout button click
    logoutBtn.addEventListener("click", logout);

    // Create a new job
    createJobBtn.addEventListener("click", async () => {
        const title = prompt("Enter job title:");
        const description = prompt("Enter job description:");
        const location = prompt("Enter job location:");
        const openings = prompt("Enter number of openings:");

        if (!title || !description || !location || !openings) {
            alert("All fields are required.");
            return;
        }

        try {
            const response = await fetch(`${API_URL}/jobs/`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    title,
                    description,
                    location,
                    openings: parseInt(openings) // Convert openings to integer
                })
            });

            const result = await response.json();
            alert(result.message);
            fetchJobs(); // Refresh job list
        } catch (error) {
            console.error("Error creating job:", error);
        }
    });

    // Load jobs on page load
    fetchJobs();
});
