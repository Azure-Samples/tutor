---
title: "Rust: Implement Feature"
description: "Implement a Rust feature with safe ownership patterns, proper error handling, and cargo test coverage."
mode: "rust-specialist"
input: "Describe the feature, crate, or module to implement. Include any trait contracts or wire formats."
---

Implement the requested Rust feature following these standards:

1. **Ownership** — Document ownership decisions. Prefer borrowing over cloning. Use Arc/Mutex only when shared mutable state is genuinely required.
2. **Error Handling** — thiserror for library crates, anyhow for application binaries. No unwrap() in production paths.
3. **Async** — tokio runtime with structured concurrency. Use select! for racing. Cancellation-safe operations only.
4. **Safety** — Zero unsafe blocks unless justified with a `// SAFETY:` comment explaining the invariant. cargo clippy --all-targets -- -D warnings must pass.
5. **Testing** — Unit tests in the same module. Integration tests in tests/. Property-based tests with proptest for complex logic.
6. **API Design** — Follow Rust API Guidelines. #[must_use] on fallible returns. Newtype pattern for domain types.

Deliver implementation, tests, and Cargo.toml dependency changes.
