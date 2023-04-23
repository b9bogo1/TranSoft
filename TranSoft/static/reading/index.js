// Define an object with options for formatting the date and time
let options = {
  year: 'numeric',
  month: 'numeric',
  day: 'numeric',
  hourCycle: 'h23',
  hour: 'numeric',
  minute: 'numeric',
  second: 'numeric'
};

// Define a function that takes an array of readings and an index as parameters
function html_data_binding(readings, index) {
  // Use jQuery to update the HTML elements with the corresponding values from the readings array
  $(`#id-${index}`).html(`${readings[index].id}`);
  $(`#order-num-${index}`).html(`${readings[index].order_num}`);
  $(`#rtd-1-${index}`).html(`${readings[index].rtd_1} Ω`);
  $(`#temp-1-${index}`).html(`${readings[index].temp_1.toFixed(3)} °C`);
  $(`#rtd-2-${index}`).html(`${readings[index].rtd_2} Ω`);
  $(`#temp-2-${index}`).html(`${readings[index].temp_2.toFixed(3)} °C`);
  $(`#requestor-id-${index}`).html(`${readings[index].requestor_id}`);
  // Use the options object to format the date and time of the reading
  $(`#at-${index}`).html(`${(new Date(readings[index].created_at)).toLocaleString("en-US", options)}`);
};
function html_header_binding(readings) {
  $("#order-num-head").html(`${readings[0].order_num}`);
  $("#requestor-id-head").html(`${readings[0].requestor_id}`);
  $("#last_rx").html(`${(new Date((readings[0].last_rx)/1000)).toLocaleString("en-US", options)}`);
  $("#last_rrq").html(`${((readings[0].last_rrq - readings[0].last_rx)/1000).toFixed(3)}`);
  $("#last_rrs").html(`${((readings[0].last_rrs - readings[0].last_rx)/1000).toFixed(3)}`);
  $("#last_tx").html(`${((readings[0].last_tx - readings[0].last_rx)/1000).toFixed(3)}`);
  $("#counter").html(`${readings[0].id}`);
}

function html_styles_binding(reading) {
  let status;
  if (reading.is_data_transmitted && (new Date()).getTime() < reading.last_rrq/1000 + 600000) {
    status = "success";
  } else if (!reading.is_data_transmitted || (new Date()).getTime() > reading.last_rrq/1000 + 600000 ) {
    status = "warning";
  } else {
    status = "danger";
  }
  switch (status) {
    case "success":
      $("#readings").addClass("text-success").removeClass("text-danger text-warning");
      $("#status-table").addClass("text-success border-success").removeClass("text-danger border-danger text-warning border-warning");
      $("#square-box").addClass("bg-success").removeClass("bg-danger bg-warning");
      break;
    case "warning":
      $("#readings").addClass("text-warning").removeClass("text-success text-danger");
      $("#status-table").addClass("text-warning border-warning").removeClass("text-success border-success text-danger border-danger");
      $("#square-box").addClass("bg-warning").removeClass("bg-success bg-danger");
      break;
    case "danger":
      $("#readings").addClass("text-danger").removeClass("text-success text-warning");
      $("#status-table").addClass("text-danger border-danger").removeClass("text-success border-success text-warning border-warning");
      $("#square-box").addClass("bg-danger").removeClass("bg-success bg-warning");
      break;
  }
}

// Define a function that gets data from the server
function get_data_from_server() {
  // Send an AJAX GET request to the Flask view function
  $.ajax({
    type: "GET",
    url: "http://127.0.0.1:5000/internal-reading-list",
    success: function(readings) {
      $("#readings").html(`${readings[0].temp_1.toFixed(3)} °C | ${readings[0].temp_2.toFixed(3)} °C`);
      // Use a loop to call the html_data_binding function for each reading in the array
      for (let i = 0; i < readings.length; i++) {
        html_data_binding(readings, i);
      }
      html_header_binding(readings);
      html_styles_binding(readings[0]);
    }
  });
}

// Set the interval in milliseconds
const interval = 1000;

// Call the get_data_from_server function once
get_data_from_server();

// Call the get_data_from_server function every interval milliseconds
setInterval(get_data_from_server, interval);