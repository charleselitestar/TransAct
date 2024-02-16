// Connect to the SocketIO server
var socket = io.connect("http://" + document.domain + ":" + location.port);

// Listen for new product listings from the server
socket.on("new_product_listing", function (product) {
  // Handle the new product listing information
  console.log("New product listing:", product);

  // Create a new product element
  var newProductElement = document.createElement("div");
  newProductElement.className = "template_box";

  // Construct the full URL for the product main image
  var mainImageUrl = product.main_image
    ? `/static/uploads/${product.main_image}`
    : `/static/uploads/default_image.jpg`;

  // Assuming product.primary_image and product.secondary_image are the respective fields in your model
  var primaryImageUrl = product.primary_image
    ? `/static/uploads/${product.primary_image}`
    : `/static/uploads/default_image.jpg`;

  var secondaryImageUrl = product.secondary_image
    ? `/static/uploads/${product.secondary_image}`
    : `/static/uploads/default_image.jpg`;

  // Populate the new product element with product information
  newProductElement.innerHTML = `
        <div class="row">
            <div class="col-12">
                <strong class="seller_name">Seller: ${
                  product.seller
                }</strong>
                <form action="/view_product" method="post" enctype="multipart/form-data">
                    <br>
                    <div class="row">
                        <div class="col-12">
                            <ol style="list-style-type: none;">
                                <li><strong class="name">Product Name: ${
                                  product.name
                                }</strong></li>
                                <li><strong>Price</strong>: ${
                                  product.price
                                }</li>
                                <li><strong class="name">Category: ${
                                  product.category
                                }</strong></li>
                                <li><strong class="name">Brand: ${
                                  product.brand
                                }</strong></li>
                                <li>Listed: ${product.date_listed} at ${
    product.time_listed.hour
  }:${product.time_listed.minute}:${product.time_listed.second}</li>
                            </ol>
                        </div>
                    </div>
                    <div class="row">
                        <input type="hidden" name="product_id" id="product" value="${
                          product.id
                        }">
                        <div class="col-12">
                            <ol style="list-style-type: none;">
                                <li>${product.billing_city} ${
    product.billing_state
  }</li>
                            </ol>
                        </div>
                    </div>
                </form>
            </div>
        </div>
        <div class="row">
            <div class="col-4">
                <img src="${mainImageUrl}" alt="Product Main Image">
            </div>
            <div class="col-4">
                ${
                  product.primary_image
                    ? `<img src="${primaryImageUrl}" alt="Primary Image">`
                    : `<img src="/static/uploads/default_image.jpg" alt="Default Image">`
                }
            </div>
            <div class="col-4">
                ${
                  product.secondary_image
                    ? `<img src="${secondaryImageUrl}" alt="Secondary Image">`
                    : `<img src="/static/uploads/default_image.jpg" alt="Default Image">`
                }
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
                    <form action="/review" method="post">
                        <input type="hidden" name="product" id="product" value="${
                          product.id
                        }">
                        <button type="submit" class="btn btn-primary">Reviews</button>
                    </form>
                </div>
                <div class="col-4">
                    <form method="POST" action="/contact">
                        <input type="hidden" name="contact_id" value="${
                          product.user_name
                        }">
                        <button type="submit" class="btn btn-success">Contact</button>
                    </form>
                </div>
            </div>
        </center>
    </div>`;

  // Add the new product element to the product list
  var productList = document.querySelector(".template_area");
  productList.insertBefore(newProductElement, productList.firstChild);
});
