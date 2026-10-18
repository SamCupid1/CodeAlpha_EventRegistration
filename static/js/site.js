document.addEventListener("DOMContentLoaded", () => {
  const filterForm = document.querySelector("[data-auto-submit]");
  if (filterForm) {
    filterForm.querySelectorAll("select, input[type='date']").forEach((field) => {
      field.addEventListener("change", () => filterForm.requestSubmit());
    });
  }

  document.querySelectorAll("[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });
});
