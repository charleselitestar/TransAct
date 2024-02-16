function handleResponsiveContent() {
  // Check if it's a mobile device
  if (window.innerWidth <= 767) {
    // Load mobile content
    document.getElementById("desktop-content").style.display = "none";
    document.getElementById("mobile-content").style.display = "block";
  } else {
    // Load desktop content
    document.getElementById("desktop-content").style.display = "block";
    document.getElementById("mobile-content").style.display = "none";
  }
}

// Run the function when the DOM is loaded
document.addEventListener("DOMContentLoaded", handleResponsiveContent);
