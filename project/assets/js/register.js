$(document).ready(function () {
  $("#signupForm").on("submit", function (e) {
    e.preventDefault();

    const payload = {
      firstname: $("#firstname").val(),
      lastname: $("#lastname").val(),
      email: $("#email").val(),
      password: $("#password").val(),
      role: $("#role").val()
    };

    $.ajax({
      url: API_BASE_URL + "/auth/signup",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(payload),
      success: function (res) {
        $("#notification")
          .css("color", "green")
          .text("✅ Inscription réussie !");
        $("#signupForm")[0].reset();
      },
      error: function (err) {
        const msg = err.responseJSON?.error || "Erreur inconnue";
        $("#notification")
          .css("color", "red")
          .text("❌ Échec de l'inscription : " + msg);
      }
    });
  });
});
