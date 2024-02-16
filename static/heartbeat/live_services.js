// Connect to the SocketIO server
var socket = io.connect("http://" + document.domain + ":" + location.port);

// Listen for new service listings from the server
socket.on("new_service_listing", function (service) {
  // Handle the new service listing information
  console.log("New service listing:", service);

  // Create a new service element
  var newServiceElement = document.createElement("div");
  newServiceElement.className = "template_box";

  // Construct the full URL for the company logo
  var logoUrl = service.company_logo
    ? `/static/uploads/${service.company_logo}`
    : `/static/uploads/${current_user.main_image}`;

  // Populate the new service element with service information
  newServiceElement.innerHTML = `
        <div class="row">
            <div class="col-12">
                <strong class="seller_name">Organization : ${service.company_name}</strong>
                <form action="{{ url_for('view_service') }}" method="post" enctype="multipart/form-data">
                    <br>
                    <div class="row">
                        <div class="col-4">
                            <img src="${logoUrl}" alt="Company Logo">
                        </div>
                        <div class="col-8">
                            <ol style="list-style-type: none;">
                                <li><strong class="name">Type : ${service.service_type}</strong></li>
                                <li><strong class="name">Position : ${service.position}</strong></li>
                                <li><strong>Location</strong> : ${service.service_location}</li>
                                <li><strong>Price</strong> : ${service.basic}</li>
                            </ol>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-12">
                    <input type="hidden" name="service_id" id="service_id" value="${service.id}">
                    <ol style="list-style-type: none;">
                        <li><strong>Requirements</strong> : ${service.service_requirements}</li>
                        <hr>
                        <li><strong>Duties</strong> : ${service.responsibilities}</li>
                    </ol>
                </div>
            </div>
            <br>
            <center>
                <div class="row">
                    <div class="col-4">
                        <button type="submit" class="btn btn-primary">View</button>
                    </form>
                </div>
                <div class="col">
                    <form action="{{ url_for('apply_services') }}" method="post">
                        <input type="hidden" name="application_position" id="application_position" value="${service.position}">
                        <input type="hidden" name="company_name" id="company_name" value="${service.company_name}">
                        <input type="hidden" name="applied_service" id="applied_service" value="${service.id}">
                        <button type="submit" class="btn btn-primary">Apply</button>
                    </form>
                </div>
                <div class="col-4">
                    <form method="POST" action="/contact">
                        <input type="hidden" name="contact_id" value="${service.user_name}">
                        <button type="submit" class="btn btn-success">Contact</button>
                    </form>
                </div>
            </div>
        </center>
    </div>`;

  // Add the new service element to the service list
  var serviceList = document.querySelector(".template_area");
  serviceList.insertBefore(newServiceElement, serviceList.firstChild);
});
