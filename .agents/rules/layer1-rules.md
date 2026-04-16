---
trigger: always_on
---

1. Python: Always create env before executing if already there then use it.
2. Python in this machine manage by PyEnv
3. Commit Protocol: Standardize on Conventional Commits (e.g., `feat:`, `fix:`, `refactor:`).
4. Documentation Sync: Every update MUST reflect in `readme.md`, `changelog.md`, and `checkpoint.md`. `checkpoint.md` is the ground truth for project logic; read it before any planning.
5. Strict Linting: Enable `ruff` or `very_good_analysis`. Zero tolerance for `//ignore`, `# noqa`, or `eslint-disable`. Fix the root cause.
6. Feature Persistence: Forbidden to delete/override existing features or logic unless explicitly requested. Cross-check against `checkpoint.md`.
7. Planning Phase: Detailed step-by-step plan required before any code modification. Wait for user "ACK" to execute.
8. Test and Report : Every executing plan do test for every scenario available. Make proper and detail report from application, hardware, result, and many more based on the system. Report can use image like diagram or table to help detailing result.
9. Versioning : After plan, executing, and report update `readme.md`, `changelog.md`, and `checkpoint.md` and commit to git local and remote. Make sure when commit do versioning to maintain the code.
