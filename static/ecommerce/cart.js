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

const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

function updateCartBadge(count) {
  const badge = document.getElementById('cart-count-badge');
  badge.textContent = count;
  badge.classList.toggle('d-none', count === 0);
}

async function sendCartRequest(url, body = {}) {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken,
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams(body),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Unable to update your cart.');
  }
  return data;
}

document.querySelectorAll('[data-cart-row]').forEach((row) => {
  const quantity = row.querySelector('[data-cart-quantity]');
  const decreaseButton = row.querySelector('[data-cart-decrease]');
  const increaseButton = row.querySelector('[data-cart-increase]');
  const canAdjustQuantity = Boolean(row.dataset.updateUrl);

  const updateQuantityControls = () => {
    decreaseButton.disabled = !canAdjustQuantity || Number(quantity.textContent) <= 1;
    increaseButton.disabled = !canAdjustQuantity;
  };
  updateQuantityControls();

  row.querySelector('[data-cart-remove]').addEventListener('click', async () => {
    row.querySelectorAll('button').forEach((button) => { button.disabled = true; });
    try {
      const data = await sendCartRequest(row.dataset.removeUrl);
      row.remove();
      updateCartBadge(data.count);
      if (!document.querySelector('[data-cart-row]')) {
        document.getElementById('cart-table').classList.add('d-none');
        document.getElementById('empty-cart-actions').classList.add('d-none');
        document.getElementById('empty-cart').classList.remove('d-none');
      }
    } catch (error) {
      window.alert(error.message);
      row.querySelectorAll('button').forEach((button) => { button.disabled = false; });
    }
  });

  if (!canAdjustQuantity) return;

  const updateQuantity = async (newQuantity) => {
    row.querySelectorAll('button').forEach((button) => { button.disabled = true; });
    try {
      const data = await sendCartRequest(
        row.dataset.updateUrl,
        { quantity: newQuantity },
      );
      quantity.textContent = data.quantity;
      row.querySelector('[data-cart-total]').textContent = data.total;
      updateCartBadge(data.count);
    } catch (error) {
      window.alert(error.message);
    } finally {
      row.querySelectorAll('button').forEach((button) => { button.disabled = false; });
      updateQuantityControls();
    }
  };

  decreaseButton.addEventListener('click', () => {
    updateQuantity(Number(quantity.textContent) - 1);
  });
  row.querySelector('[data-cart-increase]').addEventListener('click', () => {
    updateQuantity(Number(quantity.textContent) + 1);
  });
});

const emptyCartButton = document.querySelector('[data-empty-cart]');
if (emptyCartButton) {
  emptyCartButton.addEventListener('click', async () => {
    emptyCartButton.disabled = true;
    try {
      const data = await sendCartRequest(emptyCartButton.dataset.emptyCartUrl);
      document.querySelectorAll('[data-cart-row]').forEach((row) => row.remove());
      document.getElementById('cart-table').classList.add('d-none');
      document.getElementById('empty-cart-actions').classList.add('d-none');
      document.getElementById('empty-cart').classList.remove('d-none');
      updateCartBadge(data.count);
    } catch (error) {
      window.alert(error.message);
      emptyCartButton.disabled = false;
    }
  });
}
