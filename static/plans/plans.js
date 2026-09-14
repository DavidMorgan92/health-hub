document.addEventListener('DOMContentLoaded', () => {
  const resetModalElement = document.querySelector('[data-plan-reset-modal]');
  const resetModal = bootstrap.Modal.getOrCreateInstance(resetModalElement);
  const confirmResetButton = resetModalElement.querySelector('[data-plan-reset-confirm]');
  let pendingResetCheckbox = null;

  document.querySelectorAll('[data-plan-selection-form]').forEach((form) => {
    form.querySelectorAll('input[name="selected_plans"]').forEach((checkbox) => {
      checkbox.addEventListener('change', () => form.submit());
      checkbox.addEventListener('click', (event) => {
        if (checkbox.dataset.currentSelected !== 'true') return;

        event.preventDefault();
        pendingResetCheckbox = checkbox;
        resetModal.show();
      });
    });
  });

  confirmResetButton.addEventListener('click', () => {
    if (!pendingResetCheckbox) return;

    const checkbox = pendingResetCheckbox;
    checkbox.dataset.currentSelected = 'false';
    pendingResetCheckbox = null;
    resetModal.hide();
    checkbox.click();
  });

  resetModalElement.addEventListener('hidden.bs.modal', () => {
    pendingResetCheckbox = null;
  });
});