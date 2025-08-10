# Multiple Payment Gateway Integration Approach

To support transactions in multiple currencies, I initially integrated **SSLCommerz** as the payment gateway for BDT (Bangladeshi Taka) transactions. Later, I recognized the importance of **Stripe** for international users and USD transactions.

Implementing two different payment gateways led to code duplication. To adhere to the **DRY (Don't Repeat Yourself)** principle, I designed an abstract class `PaymentGateway` with the following components:

- **Abstract Methods**:
  - `initiate_payment`: Defines the logic to start a payment process.
  - `validate_payment`: Verifies the payment status.

- **Static Method**:
  - `process_order`: Handles common order processing logic.

This abstraction allows any future payment gateway to be integrated by simply inheriting the `PaymentGateway` abstract class. Additionally, I created a unified `initiate` view to handle the initiation process for all payment gateways, reducing redundancy and improving maintainability.