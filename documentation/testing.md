# Testing

## Automated test suite

Invoke `python manage.py test` at the project root to run the automated test suite.

## Manual testing

### Access control

There are routes which should only be accessed by authenticated users.

Then there are routes which should only be accessed by unauthenticated users.

Then there are routes which should only be accessed by authenticated admin users.

#### Authenticated users only

<details>
  <summary>Plans home page</summary>
  <p>The plans home page is for an authenticated user to view and manage their subscribed plans. An unauthenticated user has no purpose for this page.</p>
  <p>I have confirmed that when attempting to access the plans route as an unauthenticated user I am redirected to the login page.</p>
</details>

<details>
  <summary>Plan details page</summary>
  <p>The plan details page is for an authenticated user to see a plan details only if they have an active subscription to it. An unauthenticated user has no purpose for this page.</p>
  <p>I have confirmed that when attempting to access the plans/8 route as an unauthenticated user I am redirected to the login page.</p>
</details>

<details>
  <summary>Logout page</summary>
  <p>The logout page is for an authenticated user to logout. An unauthenticated user has no purpose for this page.</p>
  <p>I have confirmed that when attempting to access the accounts/logout route as an unauthenticated user I am redirected to the home page.</p>
</details>

<details>
  <summary>Checkout page with plans in cart</summary>
  <p>Plans must be associated with an account when purchasing. An unauthenticated user should not be able to purchase plans. The expected flow is that when the checkout page is reached and the user has plans in the basket, if they are unauthenticated they will be required to log in, and then be redirected to continue the checkout.</p>
  <p>I have confirmed that when attempting to purchase a plan as an unauthenticated user I am required to log in, and upon login I am redirected to continue the checkout.</p>
  <p>I have also confirmed that I am not required to log in as an unauthenticated user if there are only products in the basket, and no plans.</p>
</details>

#### Unauthenticated users only

<details>
  <summary>Login page</summary>
  <p>The login page is for unauthenticated users to log in. An authenticated user has no purpose for this page.</p>
  <p>I have confirmed that when I navigate to the accounts/login route as an authenticated user I am redirected to the home page.</p>
</details>

<details>
  <summary>Sign up page</summary>
  <p>The sign up page is for an unauthenticated user to create an account. An authenticated user already has an account and so has no purpose for this page.</p>
  <p>I have confirmed that when I navigate to the accounts/signup route as an authenticated user I am redirected to the home page.</p>
</details>

#### Admin users only

<details>
  <summary>Admin site section</summary>
  <p>All routes under the /admin section should be accessible only to admin users.</p>
  <p>I have confirmed that when authenticated as a non-admin user I am required to authenticate as an admin user when accessing the /admin route.</p>
</details>

<details>
  <summary>Create plan page</summary>
  <p>This is the page for creating new plan products, and should only be available to staff users.</p>
  <p>I have confirmed that the navbar "create plan" link is not visible to non-staff users, authenticated or not, and that when attempting to access the route I am challenged to provide staff user credentials.</p>
</details>

### Ecommerce flow

<details>
  <summary>Purchasing products requires delivery address</summary>
  <p>When purchasing physical products a delivery address will be required from the user. When purchasing only plans no delivery address will be required.</p>
  <p>I have confirmed that a cart containing only products requires a delivery address on the checkout page before proceeding.</p>
  <p>I have confirmed that a cart containing only plans does not require a delivery address on the checkout page before proceeding.</p>
  <p>I have confirmed that a cart containing both plans and products requires a delivery address on the checkout page before proceeding.</p>
</details>

<details>
  <summary>In the cart, a plan must only be allowed a quantity of 1</summary>
  <p>When purchasing a plan, the quantity increment/decrement buttons should be disabled, and the quantity must always be 1.</p>
  <p>I have confirmed this is the case for plans in the cart.</p>
</details>

<details>
  <summary>In the cart, a product's quantity should not be allowed to exceed the amount in stock</summary>
  <p>I have confiremd this is the case for products in the cart. When attempting to increment beyond the stock quantity, an alert appears informing the user "There is not enough stock for that quantity."</p>
</details>

<details>
  <summary>In the cart, a product's quantity should not be allowed to go below 1</summary>
  <p>I have confirmed this is the case for products in the cart. When attempting to decrement below 1 the decrement button is disabled.</p>
</details>

<details>
  <summary>Adding the same product twice to cart should increment the quantity</summary>
  <p>Instead of adding two separate line items, it should simply increment the quantity of the existing line item.</p>
  <p>I have confirmed this is the behaviour when adding two of the same product to the cart.</p>
</details>

<details>
  <summary>Adding the same plan twice to cart should not affect the cart</summary>
  <p>If a plan is already in the cart then adding it again should have no effect.</p>
  <p>I have confirmed this is the behaviour when adding a plan twice to the cart.</p>
</details>

<details>
  <summary>Cancelling payment on the Stripe website should lead to the "payment cancelled" page</summary>
  <p>If a user chooses the back button from the Stripe website instead of completing the payment the user should be taken to the "payment cancelled" page where they're informed the cart is still available if they'd like to try again.</p>
  <p>I've confirmed this is the behaviour, and the cart remains intact for the user to try again.</p>
</details>

<details>
  <summary>Completing payment on the Stripe website should lead to the "payment complete" page</summary>
  <p>I've confirmed this behaviour.</p>
</details>

### Plan functionality

<details>
  <summary>When a plan subscription is purchased the plan should be available in the plans page</summary>
  <p>I've confirmed this behaviour is as expected.</p>
</details>

<details>
  <summary>When making a plan active its events should appear in the selected plan calendar starting from the current day</summary>
  <p>Also, events of each plan should have their own colour to make it clear to which plan those events belong.</p>
  <p>The calendar on the home page should appear the same.</p>
  <p>I've confirmed this behaviour.</p>
</details>

<details>
  <summary>When making a plan inactive the user should be warned that doing so will reset the plan schedule, and user confirmation must be acquired before committing the action</summary>
  <p>I've confirmed the user is warned, and if they choose the cancel the action then no action will be taken. If they confirm the action then the plan's events will no longer appear in the selected plan calendar, or the home page calendar.</p>
</details>

<details>
  <summary>When clicking a plan event a dialog box should show the event's details</summary>
  <p>I've confirmed this behaviour on the home screen, the plans home screen, and the plan details pages.</p>
</details>

<details>
  <summary>A plan's recommended products should be listed on the plan details page</summary>
  <p>I've confirmed this behaviour is as expected.</p>
</details>

<details>
  <summary>All a plan's related subscriptions should be listed on the plan details page</summary>
  <p>I've confirmed this behaviour is as expected.</p>
</details>

<details>
  <summary>When cancelling a subscription from Stripe this should be reflected in the subscription information on the plan details page</summary>
  <p>I have found a bug here. I cancelled a subscription through the Stripe web interface, but it did not update in Health Hub. There must be an issue with the web hook endpoint.</p>
  <p><a href="#cancelling-a-subscription-via-stripe-did-not-update-the-entity-in-the-database">The bug is documented here.</a> Upon investigation I found I had simply misconfigured the webhook endpoint. I have confirmed the behaviour is as expected.</p>
</details>

<details>
  <summary>When a plan has no active subscriptions it should become inactive</summary>
  <p>I have confirmed this behaviour.</p>
</details>

<details>
  <summary>When a plan has at least one active subscription it should be active</summary>
  <p>I have confirmed this behaviour.</p>
</details>

<details>
  <summary>When a plan becomes inactive it should not be able to be selected</summary>
  <p>I have confirmed this behaviour. I had a plan selected as current, then made its last active subscription inactive. The plan was no longer selected, and now the checkbox is disabled to prevent selecting it.</p>
</details>

<details>
  <summary>When a plan is active it should be possible to select it as current</summary>
  <p>I have confirmed this behaviour. An active subscription can be made "current" by checking its checkbox, which will make its events appear in the calendar starting from the current day.</p>
</details>

<details>
  <summary>Create plan page works as expected</summary>
  <p>I tested that I was able to create plan with an attached image, a set of events, and all required information input. I was able to purchase the plan as a non-staff user and it had the correct title, description and price, and the event information is all correct.</p>
</details>

### Bugs found

#### Cancelling a subscription via Stripe did not update the entity in the database

I suspect the webhook endpoint ignored the event, and should be updated to accept cancellation events and update the database entity.

As it happens, I simply forgot to create a new webhook for the Heroku deployment, separate to the development webhook. After configuring this in both Stripe and Heroku, when I cancel a subscription in Stripe this is reflected in Health Hub.
