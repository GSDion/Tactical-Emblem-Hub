const steps = document.querySelectorAll(".form-step");
const nextBtns = document.querySelectorAll(".next-step");
const prevBtns = document.querySelectorAll(".prev-step");
const progressBar = document.querySelector(".progress-bar");

let currentStep = 0;

// Initialize dataLayer if not already initialized
window.dataLayer = window.dataLayer || [];

// Function to update progress bar
function updateProgressBar() {
  const progress = ((currentStep + 1) / steps.length) * 100;
  progressBar.style.width = `${progress}%`;
  progressBar.setAttribute("aria-valuenow", progress);
}

// Function to show the current step and send dataLayer event
function showCurrentStep() {
  steps.forEach((step, index) => {
    if (index === currentStep) {
      step.classList.add("active");
    } else {
      step.classList.remove("active");
    }
  });
  
  // Fire dataLayer event for each step
  window.dataLayer.push({
    'event': `form_step_${currentStep + 1}`
  });

  updateProgressBar();
}

// Initialize first step visibility
showCurrentStep();

// Next button event listeners
nextBtns.forEach((button) => {
  button.addEventListener("click", () => {
    const currentInputs = steps[currentStep].querySelectorAll("input, select");
    let valid = true;

    // Validate the current inputs
    currentInputs.forEach((input) => {
      if (!input.checkValidity()) {
        input.classList.add("is-invalid");
        valid = false;
      } else {
        input.classList.remove("is-invalid");
        input.classList.add("is-valid");
      }
    });

    if (valid) {
      steps[currentStep].classList.remove("active");
      currentStep++;

      // Populate review fields if on the final step
      if (currentStep === steps.length - 1) {
        document.getElementById('reviewFirstName').textContent = document.getElementById('firstName').value;
        document.getElementById('reviewLastName').textContent = document.getElementById('lastName').value;
        document.getElementById('reviewEmail').textContent = document.getElementById('businessEmail').value || document.getElementById('email').value;
      }

      showCurrentStep();
    }
  });
});

// Previous button event listeners
prevBtns.forEach((button) => {
  button.addEventListener("click", () => {
    currentStep--;
    showCurrentStep();
  });
});

// Add event listener for form submission to fire the generate_lead event
document.getElementById("multiStepForm").addEventListener("submit", function (e) {
  e.preventDefault();  // Prevent the default form submission for this example
  
  // Fire generate_lead event in the dataLayer
  window.dataLayer.push({
    'event': 'generate_lead'
  });

  // Continue with form submission logic or AJAX call, if needed
  // Example: alert('Form submitted successfully!');
});
