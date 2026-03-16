---
title: "Rust: Review Code"
description: "Review Rust code for safety, ownership correctness, performance, and idiomatic patterns."
mode: "rust-specialist"
input: "Provide the crate or file(s) to review. Optionally specify focus (safety, performance, API design)."
---

Review the specified Rust code checking for:

1. **Safety** — Audit all unsafe blocks for soundness. Verify SAFETY comments are present and correct. Check for UB risks.
2. **Ownership** — Unnecessary clones, missed borrows, lifetime over-specification, Arc where Rc suffices (or vice versa).
3. **Error Handling** — unwrap/expect in non-test code. Error type granularity. Proper ? propagation chains.
4. **Concurrency** — Data races (even in safe code via logical races). Deadlock potential. Channel vs mutex trade-offs.
5. **Performance** — Unnecessary allocations. Missing #[inline] on hot paths. Iterator chain vs loop efficiency.
6. **Idioms** — Match exhaustiveness. Builder pattern usage. Trait object vs generic trade-offs.

Deliver findings as a prioritized list with severity, location, and fix recommendations.
