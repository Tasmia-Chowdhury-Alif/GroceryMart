
# Stripe Integration Issue and Resolution

While integrating **Stripe**, I initially explored a custom Stripe gateway implementation. As it was my first time working with Stripe and I had not yet implemented the frontend, I opted for the **Stripe Hosted Gateway** approach, which provides a Stripe-hosted URL for payment processing.

During the integration, I encountered an issue due to an error in my environment configuration. I had set up a webhook endpoint for event handling but neglected to update the `STRIPE_WEBHOOK_SECRET` in the environment variables. This resulted in **Bad Request** errors in the logs. Once I corrected the `STRIPE_WEBHOOK_SECRET`, the webhook functionality worked as expected.