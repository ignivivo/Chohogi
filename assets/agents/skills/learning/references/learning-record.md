# Learning Record Contract

Use this reference only after the learning loop has confirmed a reusable
failure and selected a prevention. Project guidance chooses the destination and
stable ID; do not create a second generic ledger.

## Required sections

1. **Case metadata:** stable ID, dates, state, source evidence, and affected
   producer/consumer boundary.
2. **Observed problem:** impact and a reproduction or review finding. Keep it
   separate from the cause.
3. **Hypotheses and disposition:** list material candidate causes as
   `suspected`, `rejected`, or `confirmed`, each with evidence.
4. **Classification stack:** language/runtime, framework, library/platform,
   product/domain boundary, failure class, primary cause, and prevention scope.
   A framework or vendor is context, not blame, unless its behavior is the
   evidenced primary cause.
5. **Correction evidence:** minimal before/after excerpts, each tied to a file
   and commit, diff, test, log, or review reference. Label pseudocode as such.
   If original code is unavailable, state that evidence limit instead of
   reconstructing it.
6. **Verification and learning disposition:** checks actually run; selected
   prevention; why it is the smallest durable choice; negative scope.
7. **Later review:** append dated evidence when the record is confirmed,
   revised, or superseded.

## Evidence hygiene

- Keep excerpts small and omit secrets, personal inputs, provider prompts,
  complete report prose, and unrelated code.
- Prefer a focused regression test. If historical evidence contains only a
  review or manual reproduction, say so plainly.
- Do not promote a defect merely because it occurred in JavaScript, React,
  Next.js, Vercel, or a domain module. Classify the actual ownership boundary
  and choose the narrowest prevention that catches it.
