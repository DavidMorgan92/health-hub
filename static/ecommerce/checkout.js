const deliveryAddress = document.getElementById('delivery-address');

if (deliveryAddress) {
  const checkoutButton = deliveryAddress.form.querySelector('button[type="submit"]');
  const updateCheckoutButton = () => {
    checkoutButton.disabled = !deliveryAddress.value.trim();
  };

  deliveryAddress.addEventListener('input', updateCheckoutButton);
  updateCheckoutButton();
}
