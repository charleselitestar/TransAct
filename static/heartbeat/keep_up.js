document.addEventListener("DOMContentLoaded", function () {
  const HEARTBEAT_INTERVAL = 1000; // 1 second
  let currentHtml = "";
  let url_path = document.getElementById("url_path").value;

  function checkHeartbeat() {
    fetch(`${url_path}`, {
      method: "GET",
      headers: {
        "Content-Type": "text/html",
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.text();
      })
      .then((html) => {
        if (html !== currentHtml) {
          document.body.innerHTML = html;
          currentHtml = html;
        }
      })
      .catch((error) => {
        console.error("Fetch error:", error);
      });
  }

  const heartbeatIntervalId = setInterval(checkHeartbeat, HEARTBEAT_INTERVAL);

  // Optionally, you can clear the interval when it's no longer needed
  // clearInterval(heartbeatIntervalId);
});
