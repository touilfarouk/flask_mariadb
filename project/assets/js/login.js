$(document).ready(function () {
  // If already logged in
  if (localStorage.getItem("jwt_token")) {
    window.location.href = "protected.html";
    return;
  }

  $("#loginForm").on("submit", function (e) {
    e.preventDefault();

    $.ajax({
      url: API_BASE_URL + "/auth/login",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        email: $("#email").val(),
        password: $("#password").val()
      }),
      success: function (res) {
        if (res.token) {
          localStorage.setItem("jwt_token", res.token);
          $("#notification").css("color", "green").text("✅ Login successful, redirecting...");
          setTimeout(() => window.location.href = "protected.html", 1000);
        } else {
          $("#notification").css("color", "red").text("❌ No token received");
        }
      },
      error: function () {
        $("#notification").css("color", "red").text("❌ Invalid email or password");
      }
    });
  });
});
