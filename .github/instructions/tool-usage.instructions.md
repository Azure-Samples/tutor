---
applyTo: '**'
---

## Tool Usage Directives

Agents MUST actively use the tools declared in their `tools:` frontmatter. Tool declarations grant access — these directives specify **when and how** to invoke them.

### Standard Tool Categories

#### `execute` — Terminal Commands

| When | Example |
|------|---------|
| Run tests after any code change | `pytest -x`, `npm test`, `cargo test` |
| Build and compile artifacts | `cargo build --release`, `tsc`, `python -m build` |
| Run linters and formatters | `ruff check .`, `eslint .`, `rustfmt --check` |
| Install dependencies | `uv pip install`, `npm install`, `cargo add` |
| Run migration scripts | `alembic upgrade head`, `prisma migrate dev` |
| Check runtime behaviour | `python -c "..."`, `node -e "..."` |

**Rule**: Never describe a command without running it. If you recommend running something, run it.

#### `read` — File Reading

| When | Example |
|------|---------|
| Before modifying any file | Read the file and surrounding context first |
| Resolving an error | Read the file at the reported line number |
| Understanding imports and dependencies | Read referenced modules |
| Reviewing existing patterns | Read related files to match conventions |

**Rule**: Never propose changes to code you have not read. Always read first, then modify.

#### `edit` — File Editing

| When | Example |
|------|---------|
| Implementing a feature or fix | Replace or insert code at the right location |
| Refactoring code | Apply refactoring techniques with precise edits |
| Updating configuration | Modify config files, manifests, YAML |

**Rule**: Prefer targeted edits (`replace_string_in_file`) over full rewrites. Include 3–5 lines of context around the target.

#### `search` — Workspace Search

| When | Example |
|------|---------|
| Finding where a symbol is defined or used | `grep_search` for function names, class names |
| Locating files by name or pattern | `file_search` with glob patterns |
| Understanding how a concept is implemented | `semantic_search` for broad context |
| Navigating unfamiliar code | Combine `file_search` to find files, then `read` |

**Rule**: Search before asking the user for locations. Use `grep_search` for exact text, `semantic_search` for concepts.

#### `web` — External Resources

| When | Example |
|------|---------|
| Consulting official documentation | Fetch language docs, framework guides, API references |
| Checking latest versions or release notes | Verify package versions, deprecation notices |
| Researching best practices | Azure Well-Architected, OWASP, platform guides |

**Rule**: Cite the source URL when basing recommendations on web content.

#### `agent` — Sub-Agent Delegation

| When | Example |
|------|---------|
| Task crosses domain boundaries | Delegate Python code to PythonDeveloper, Azure IaC to an Azure specialist |
| Architecture validation needed | Delegate to SystemArchitect |
| PR review required | Delegate to PRReviewer |
| UI work needed | Delegate to UIDesigner |

**Rule**: Always provide a structured brief when delegating — include scope, acceptance criteria, and constraints. Consult `.github/agents/data/team-mapping.md` for the full agent registry.

#### `todo` — Task Tracking

| When | Example |
|------|---------|
| Multi-step work requiring sequencing | Break complex tasks into tracked items |
| User provides multiple requests | Create a todo for each request |
| Long-running implementation | Track milestones and mark progress |

**Rule**: Mark todos in-progress before starting. Mark completed immediately after finishing. Limit one in-progress at a time.

### MCP Tool Invocation Protocol

When your `tools:` array includes MCP server tools (e.g., `azure-mcp/*`, `email-local/*`, `research-server/*`):

1. **Load before use** — MCP tools are deferred. Use `tool_search_tool_regex` to discover and load them before invocation.
2. **Prefer MCP tools over manual alternatives** — If an MCP tool exists for an operation (e.g., `azure-mcp/deploy` vs. manual `az` CLI), use the MCP tool.
3. **Chain MCP calls logically** — Gather context first (`subscription_list`, `group_list`), then perform operations (`deploy`, `monitor`).
4. **Capture diagnostics** — When an MCP tool returns errors or warnings, log them and adjust the approach rather than retrying blindly.

### Subagent Name Resolution Protocol

Before invoking `#runSubagent`:

1. **Resolve canonical names first** — Load `.github/agents/data/team-mapping.md` and use the `Agent Name` values (for example, `SystemArchitect`, `TypeScriptDeveloper`, `PlatformEngineer`).
2. **Do not assume slug names** — Avoid hardcoded kebab-case names unless they are explicitly registered in the runtime.
3. **Runtime fallback** — If the target specialist is not available in the current runtime, stay in the current agent and use the appropriate workspace, terminal, MCP, and web tools directly while preserving the same role boundaries.
4. **Explain fallback** — State which specialist was intended, why direct execution was used instead, and what acceptance criteria the fallback path must still satisfy.
