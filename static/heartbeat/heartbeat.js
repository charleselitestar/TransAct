// Set the time interval for the heartbeat check (in milliseconds)
const HEARTBEAT_INTERVAL = 5000; // 5 seconds

// Set the inactivity threshold (in milliseconds) to consider the user as inactive
const INACTIVITY_THRESHOLD = 90000; // 90 seconds

let lastActivityTimestamp = Date.now();

// Function to handle user activity
function handleUserActivity() {
  lastActivityTimestamp = Date.now();
  // You can perform additional tasks here if needed
}

// Function to check for inactivity and log out the user
function checkInactivity() {
  const currentTime = Date.now();
  const timeSinceLastActivity = currentTime - lastActivityTimestamp;

  if (timeSinceLastActivity > INACTIVITY_THRESHOLD) {
    // User has been inactive for too long, log them out
    // Perform a request to the Flask logout route
    fetch("/logout", {
      method: "GET", // Adjust the method based on your Flask route
      headers: {
        "Content-Type": "application/json",
        // Add any additional headers if required
      },
      // Add any additional data if required
      // body: JSON.stringify({}),
    })
      .then((response) => {
        // Handle the response as needed
        // For example, you might want to redirect to the login page
        if (response.ok) {
          window.location.href = "/login"; // Adjust the login route
        } else {
          console.error("Logout failed:", response.statusText);
        }
      })
      .catch((error) => {
        console.error("Error during logout request:", error);
      });
  }
}

// Set up the heartbeat interval
setInterval(checkInactivity, HEARTBEAT_INTERVAL);

// Attach event listeners for user activity
document.addEventListener("mousemove", handleUserActivity);
document.addEventListener("keydown", handleUserActivity);
