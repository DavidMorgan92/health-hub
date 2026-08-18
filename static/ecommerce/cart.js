document.querySelectorAll('[data-add-to-cart]').forEach((button) => {
  button.addEventListener('click', async () => {
    button.disabled = true;
    try {
      const response = await fetch(button.dataset.addToCart, {
        method: 'POST',
        headers: {
          'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content,
          'X-Requested-With': 'XMLHttpRequest',
        },
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Unable to add this item to your cart.');
      }

      const badge = document.getElementById('cart-count-badge');
      badge.textContent = data.count;
      badge.classList.toggle('d-none', data.count === 0);
    } catch (error) {
      window.alert(error.message);
    } finally {
      button.disabled = false;
    }
  });
});
