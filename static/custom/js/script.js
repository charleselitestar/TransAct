// Function to close the flash message after a specified delay
function closeFlashMessage() {
  var flashMessage = document.getElementById("flash-message");
  if (flashMessage) {
    setTimeout(function () {
      flashMessage.style.display = "none";
    }, 5000); // Adjust the delay (in milliseconds) as needed (e.g., 5000 milliseconds = 5 seconds).
  }
}

// Call the closeFlashMessage function when the page loads
window.onload = closeFlashMessage;
// script.js

// Add an event listener for the "click" event on the document
document.addEventListener('click', function (event) {
    // Check if the event target is the element with the ID "reset_password"
    if (event.target && event.target.id === 'reset_password') {
        // Get the current value of the "reset_password" checkbox
        var resetCheckbox = document.getElementById('reset_password');
        var resetValue = resetCheckbox.checked;

        // Get the element with the ID "submit"
        var submitButton = document.getElementById('submit');

        // Change the text and color of the submit button based on the checkbox value
        if (resetValue) {
            submitButton.innerHTML = 'RESET';
            submitButton.style.backgroundColor = 'red'; // Change the background color to red
            submitButton.style.color = 'white'; // Change the text color to white
            
        } else {
            submitButton.innerHTML = 'Login';
            submitButton.style.backgroundColor = 'blue'; // Change the background color to blue
            submitButton.style.color = 'white'; // Change the text color to black
        }
    }
});
function changeBackgroundColor() {
  // Get the element by its ID
  var applicationStatus = document.getElementById("application_status");

  // Check if the inner HTML is equal to "you have not applied"
  if (applicationStatus.innerHTML.trim() === "you have not yet applied apply now!!!") {
    // Change the background color to red
    applicationStatus.style.backgroundColor = "red";
  }
}