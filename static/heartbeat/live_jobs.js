var socket = io.connect("http://" + document.domain + ":" + location.port);

// Listen for new job updates from the server
socket.on("new_job", function (job) {
  // Handle the new job information
  console.log("New job:", job);

  // Create a new job element
  var newJobElement = document.createElement("div");
  newJobElement.className = "template_box";

  // Construct the full URL for the company logo
  var logoUrl = job.company_logo
    ? `/static/uploads/${job.company_logo}`
    : `/static/uploads/${current_user.main_image}`;

  // Populate the new job element with job information
  newJobElement.innerHTML = `
    <div class="row">
        <div class="col-12">
            <strong class="seller_name">Organization: ${job.company_name}</strong>
            <form action="/view_job" method="post" enctype="multipart/form-data">
                <br>
                <div class="row">
                    <div class="col-4">
                        <img src="${logoUrl}" alt="Company Logo">
                    </div>
                    <div class="col-8">
                        <ol style="list-style-type: none;">
                            <li><strong class="name">Position: ${job.position}</strong></li>
                            <li><strong>Type:</strong> ${job.employment_type}</li>
                            <li><strong>Location: ${job.job_location}</strong></li>
                            <li><strong class="name">Deadline: ${job.application_deadline}</strong></li>
                            <li><strong>Working Hours:</strong> ${job.hours}</li>
                            <li><strong>Avg Salary:</strong> ${job.basic_salary}</li>
                        </ol>
                    </div>
                </div>
        </div>
    </div>
    <div class="row">
        <input type="hidden" name="job_id" id="job_id" value="${job.id}">
        <div class="col-12">
            <ol style="list-style-type: none;">
                <li>Requirements: ${job.job_requirements}</li>
                <li><strong class="name">Experience: ${job.experience_level}</strong></li>
                <li>Benefits: ${job.benefits}</li>
            </ol>
        </div>
    </div>
    <br>
    <center>
        <div class="row">
            <div class="col-4">
                <button type="submit" class="btn btn-primary">View</button>
            </div>
            </form>
            <div class="col">
                <form action="/apply_job" method="post">
                    <input type="hidden" name="applied_job" id="applied_job" value="${job.id}">
                    <button type="submit" class="btn btn-primary">Apply</button>
                </form>
            </div>
            <div class="col-4">
                <form method="POST" action="/contact">
                    <input type="hidden" name="contact_id" value="${job.user_name}">
                    <button type="submit" class="btn btn-success">Contact</button>
                </form>
            </div>
        </div>
    </center>
</form>
</div>
  `;

  // Add the new job element to the job list
  var jobList = document.querySelector(".template_area");
  jobList.insertBefore(newJobElement, jobList.firstChild);
});
