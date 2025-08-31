$(document).ready(function () {
  const token = localStorage.getItem("jwt_token");

  if (!token) {
    window.location.href = "login.html";
    return;
  }

  // Call backend
  $.ajax({
    url: API_BASE_URL + "/protected",
    method: "GET",
    headers: { Authorization: "Bearer " + token },
    success: function (res) {
      $("#content").text("✅ Accès autorisé : " + JSON.stringify(res));
    },
    error: function () {
      $("#content").text("❌ Accès refusé, redirection...");
      setTimeout(() => (window.location.href = "login.html"), 1000);
    }
  });

  // Logout
  $("#logoutBtn").on("click", function () {
    localStorage.removeItem("jwt_token");
    window.location.href = "login.html";
  });
});
