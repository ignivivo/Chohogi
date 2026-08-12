---
name: frontend-surface
metadata:
  chohogi_assurance: advisory
description: Review a substantive user-facing interface addition, redesign, or visual interaction change before implementation. Establish intentional hierarchy, composition, density, typography, and motion choices without displacing accessibility, performance, or state-safety review.
---

# Frontend surface review

Use this method first for a substantive user-facing interface addition, redesign, or visual interaction change. Its purpose is to prevent an unexamined default component stack from becoming the product surface.

This is not a style generator, brand authority, visual-certification gate, or controller. It does not replace accessibility, performance, Core Web Vitals, or asynchronous-state review.

## Establish the surface before code

Read the request, relevant product context, and the existing design system or adjacent screens. State a compact surface packet before selecting components:

- **Task and audience:** who must accomplish what, in which context and state.
- **Primary hierarchy:** the one action or piece of information that must win attention, plus the deliberate secondary path.
- **Composition and density:** the information grouping, persistent versus progressive detail, and the intended reading rhythm.
- **System fit:** tokens, components, content conventions, responsive behavior, and constraints that already exist.
- **Distinctive but functional choice:** one justified decision about layout, type, data presentation, imagery, or interaction; do not add decoration merely to appear different.
- **Risk handoff:** identify which changed semantic or interactive surfaces require accessibility review, which rendering or media decisions require performance/Core Web Vitals review, and whether asynchronous state changes require state-safety review.

If the task, audience, or existing system cannot be established, say so and keep the result provisional. Do not fabricate a brand, product narrative, or visual evidence.

## Review for intentionality, not an aesthetic verdict

Check the proposed surface against concrete failure modes:

- The page has one undifferentiated card grid, repeated pills, badges, gradients, or decorative controls without a task reason.
- Every section has equal visual weight, so scanning does not reveal priority.
- Typography, spacing, radius, shadows, and color use the component-library defaults without relating to content or the existing system.
- Placeholder copy, fake metrics, invented logos, or ornamental browser chrome are presented as product evidence.
- Motion, media, or visual effects obscure state, compete with reading, or add cost without helping the task.

For each applicable finding, revise the hierarchy or remove the unnecessary element. A familiar pattern is acceptable when it is the clearest fit for the user task; novelty is not the goal.

## Hand off to the specialized methods

Run or apply the following methods when their trigger is met; this review cannot waive them:

- **Accessibility:** every changed user-facing semantic or interactive surface.
- **Performance and Core Web Vitals:** media, fonts, motion, above-the-fold work, client rendering, or rendering-cost changes.
- **React async state safety:** client UI that adds or changes requests, stale-result handling, retries, reset/close behavior, cache invalidation, locale, or identity state.

Record the surface packet and the handoffs with the delivery evidence. If an implementation contradicts the packet, update the packet or explain the intentional deviation.

## Limits

This advisory method cannot prove that a design feels human, that users are not fatigued, or that an interface meets accessibility, performance, or product-quality targets. Those claims require project evidence, user research, measurements, and the corresponding specialist verification.
