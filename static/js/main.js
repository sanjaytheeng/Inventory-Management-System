// Main JavaScript file for the inventory management system

$(document).ready(function () {
  // Initialize tooltips
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Auto-hide alerts after 5 seconds
  $(".alert").delay(5000).fadeOut(500);

  // Handle form submissions with AJAX
  $("form.ajax-form").on("submit", function (e) {
    e.preventDefault();
    var form = $(this);
    var url = form.attr("action");

    $.ajax({
      type: "POST",
      url: url,
      data: form.serialize(),
      success: function (response) {
        if (response.success) {
          showAlert("success", response.message);
          if (response.redirect) {
            window.location.href = response.redirect;
          }
        } else {
          showAlert("danger", response.message);
        }
      },
      error: function (xhr, status, error) {
        showAlert("danger", "An error occurred. Please try again.");
      },
    });
  });

  // Function to show alerts
  function showAlert(type, message) {
    var alertHtml =
      '<div class="alert alert-' +
      type +
      ' alert-dismissible fade show" role="alert">' +
      message +
      '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>' +
      "</div>";

    $(".container").prepend(alertHtml);
    $(".alert").delay(5000).fadeOut(500);
  }

  // Handle agent name autocomplete
  $("#id_agent_name").on("input", function () {
    var query = $(this).val();
    if (query.length >= 2) {
      $.get("/api/agents/autocomplete/", { q: query }, function (data) {
        // Update autocomplete suggestions
        // Implementation depends on your autocomplete library
      });
    }
  });

  // Handle inventory quantity updates
  $(".update-quantity").on("click", function () {
    var itemId = $(this).data("item-id");
    var newQuantity = $("#quantity-" + itemId).val();

    $.post(
      "/inventory/update-quantity/",
      {
        item_id: itemId,
        quantity: newQuantity,
      },
      function (response) {
        if (response.success) {
          $("#available-" + itemId).text(response.available);
          $("#in-use-" + itemId).text(response.in_use);
          showAlert("success", "Quantity updated successfully");
        } else {
          showAlert("danger", response.message);
        }
      }
    );
  });
});
