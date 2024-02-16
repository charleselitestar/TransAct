        // Function to close the flash message after a specified delay
        function closeFlashMessage() {
            var flashMessage = document.getElementById('flash-message');
            if (flashMessage) {
                setTimeout(function () {
                    flashMessage.style.display = 'none';
                }, 2000); // Adjust the delay (in milliseconds) as needed (e.g., 5000 milliseconds = 5 seconds).
            }
        }

        // Call the closeFlashMessage function when the page loads
        window.onload = closeFlashMessage;

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
  const phoneInput = document.getElementById("phone_number");
  const phoneError = document.getElementById("phone_number_error");

  phoneInput.addEventListener("input", () => {
    const phoneNumber = phoneInput.value;
    const phonePattern = /^\d{10}$/; // Assuming a 10-digit phone number
    if (phonePattern.test(phoneNumber)) {
      phoneError.textContent = "";
    } else {
      phoneError.textContent = "Please enter a valid 10-digit phone number.";
    }
  });