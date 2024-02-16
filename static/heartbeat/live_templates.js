var socket = io.connect("http://" + document.domain + ":" + location.port);


socket.on("new_template", function (template) {
  console.log("new_template:", template);

  var NewTemplateElement = document.createElement("div");
  NewTemplateElement.className = "template_box";

  // Construct the full URL for the product main image
  var mainImageUrl = template.main_image
    ? `/static/uploads/${template.main_image}`
    : `/static/uploads/default_image.jpg`;

  // Assuming product.primary_image and product.secondary_image are the respective fields in your model
  var primaryImageUrl = template.primary_image
    ? `/static/uploads/${template.primary_image}`
    : `/static/uploads/default_image.jpg`;

  var secondaryImageUrl = template.secondary_image
    ? `/static/uploads/${template.secondary_image}`
    : `/static/uploads/default_image.jpg`;

    NewTemplateElement.innerHTML = `
    
    `;

    var templateList = document.querySelector(".template_area");
    templateList.insertBefore(NewTemplateElement, templateList.firstChild);
})