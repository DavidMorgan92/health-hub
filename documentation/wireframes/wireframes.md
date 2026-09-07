# Wireframes

## Ecommerce

<details>
  <summary>Store front page</summary>
  <p>The store front page shows a selection of 5 products from each product category. They are displayed horizontally with a scrollbar used for narrow screens. Each section has a "view all" link that will take the user to the search page and allow the user to search within that product category.</p>
  <p>There is a search bar at the top allowing the user to jump to the search page with a free-text query term and/or a product type query term.</p>
  <img src="ecommerce/store-front-page.png">
</details>

<details>
  <summary>Store search page</summary>
  <p>The search page shows the same search form as the store front page, and shows similar product cards too, with the same add-to-cart functionality. The difference is in the content shown. Here the content is user-driven based on their search parameters.</p>
  <img src="ecommerce/store-search-page.png">
  <p>If there are no results the content will be a simple message.</p>
  <img src="ecommerce/store-search-page-no-results.png">
</details>

<details>
  <summary>Cart</summary>
  <p>The cart page shows the content of the cart, and allows for adjusting quantity or removing any items.</p>
  <p>Plan type products can only have a quantity of 1, so the - and + buttons are disabled.</p>
  <p>For product type products, they have a minimum quantity of 1, and the max quantity should not be allowed to go higher than the amount in stock.</p>
  <p>The total cost is displayed, and the user is presented with an option to go to the checkout.</p>
  <img src="ecommerce/cart.png">
  <p>If the cart is empty a simple info alert will be shown.</p>
  <img src="ecommerce/cart-empty.png">
</details>

<details>
  <summary>Checkout login</summary>
  <p>When the user is attempting to check out with plan type products and is unauthenticated, they must be authenticated so the plans can be associated with an account. This page will be displayed in that case to require the user to either login or create an account and then they will be redirected to the checkout page.</p>
  <img src="ecommerce/checkout-login.png">
</details>

<details>
  <summary>Checkout</summary>
  <p>The checkout shows a simple list of the items and prices about to be purchased, and a total.</p>
  <p>The user is presented with a button to continue to pay with Stripe where they will be redirected to a Stripe page, and a link to go back to the cart to make adjustments.</p>
  <p>If the user navigates to the checkout page and there are no items in the cart, the user will be redirected to the cart page.</p>
  <img src="ecommerce/checkout.png">
  <p>If the cart contains product type products (as opposed to plans) then a delivery address is required, so an input is shown for that, and is required to continue to pay.</p>
  <img src="ecommerce/checkout-products.png">
</details>

<details>
  <summary>Payment complete</summary>
  <p>On successfuly payment the user will be shown a thank you message and a link to continue shopping in the store.</p>
  <img src="ecommerce/payment-complete.png">
</details>

<details>
  <summary>Payment cancelled</summary>
  <p>On a cancelled payment the user will be shown a message informing them their cart is still ready to be purchased again, and a link to continue shopping in the store.</p>
  <img src="ecommerce/payment-cancelled.png">
</details>

## Plans

<details>
  <summary>Plans front page</summary>
  <p>This page shows a user's plans and their states, and allows the user to choose which ones are currently active.</p>
  <p>It also shows a calendar which shows the events in each selected plan.</p>
  <p>This is how it will appear whent he user has no subscribed plans.</p>
  <img src="plans/plans-front-page.png">
  <p>When the user has subscribed plans they will be shown.</p>
  <p>The user can toggle plans as "current" or not with the checkboxes. When they are started they will be started on the current day. When a user is about to uncheck one, they will first be warned that this will reset their position within the plan, and must confirm their decision. Plans that are chosen will have their events shown in the calendar below. Each chosen plan will have its events shown in a unique colour. Clicking on an event will give more detail about it.</p>
  <img src="plans/plans-front-page-with-plans.png">
</details>
