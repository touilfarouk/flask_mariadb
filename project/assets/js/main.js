$(document).ready(function () {
  // Load header & footer
  $("#header").load("partials/header.html", function () {
    $(".nav-link").on("click", function () {
      const pageId = $(this).data("page");
      $(".page").addClass("hidden");
      $("#" + pageId).removeClass("hidden");
    });
  });
  $("#footer").load("partials/footer.html");

  // Show accueil by default
  $(".page").addClass("hidden");
  $("#accueil").removeClass("hidden");
});
