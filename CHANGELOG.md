# CHANGELOG

<!-- version list -->

## v0.4.0 (2026-07-20)

### Bug Fixes

- Default signal.connect to weak=False to prevent silent no-op receivers
  ([`e0aaff1`](https://github.com/ivellios/celery-signal-receivers/commit/e0aaff1b081387a2df0257c85af8a9d8353f97db))

- Drop redundant task registration and Python 3.14 signature mismatch
  ([`5b67001`](https://github.com/ivellios/celery-signal-receivers/commit/5b67001a0c69cd9f341fcf25a8f9c4a759de8e51))

- Use explicit is-not-None check for message in producer
  ([`922b18f`](https://github.com/ivellios/celery-signal-receivers/commit/922b18f38f3c9b86dec55646c91c43bfdbc6c37a))

- Validate receiver_task input and detect Celery task name collisions
  ([`0859ffc`](https://github.com/ivellios/celery-signal-receivers/commit/0859ffcbf9ce15dcb7f5665e2dcb560088f66351))

### Chores

- Fix stale test fixture leftovers
  ([`e2c084a`](https://github.com/ivellios/celery-signal-receivers/commit/e2c084ab6674993d3791ef6eb38c470bd8121200))

- Remove stray .github/tests/ leftover testing unified_signals directly
  ([`6e0d5de`](https://github.com/ivellios/celery-signal-receivers/commit/6e0d5de614e64e9029fe2743a92e3a40d46f90a7))

- Sync uv.lock version
  ([`9af4b82`](https://github.com/ivellios/celery-signal-receivers/commit/9af4b8214218bdfe05f1dce96b426ecb8c9580d2))

### Continuous Integration

- Add Python 3.14 to CI and tox test matrix
  ([`c35c2f1`](https://github.com/ivellios/celery-signal-receivers/commit/c35c2f11b69c5c3cc3b2a4739b56386f3dc85af4))

### Documentation

- Add CI/coverage badges and Contributing/Releasing sections to README
  ([`2752b65`](https://github.com/ivellios/celery-signal-receivers/commit/2752b65ba18b67f0aedaea3b6aea2ba391e85ec6))

- Document message JSON-serialization requirement and task-name collision gotcha
  ([`d693257`](https://github.com/ivellios/celery-signal-receivers/commit/d693257d73463c881f21286d1e552b41fede311f))

- Fix decorator import path typo, document direct-call gotcha
  ([`6120f25`](https://github.com/ivellios/celery-signal-receivers/commit/6120f259eb0b378d56a1305f676a9fe4de705347))

### Features

- Add PyPI/TestPyPI publish workflows
  ([`d80de78`](https://github.com/ivellios/celery-signal-receivers/commit/d80de78d06b173f1aa382c4e66433b14cf46feb5))

- Upload coverage report to Codecov in CI
  ([`1a2296e`](https://github.com/ivellios/celery-signal-receivers/commit/1a2296e4798133ac732e22331dab862fc5b98442))

### Testing

- Cover celery_task_options, dispatch_uid, and error paths in receiver_task
  ([`6cd4af6`](https://github.com/ivellios/celery-signal-receivers/commit/6cd4af614aa9866f6e51256a64bc274918b08100))

- Cover malformed non-JSON message payload
  ([`6c4883f`](https://github.com/ivellios/celery-signal-receivers/commit/6c4883f4b7de1f4600b642d23a27a1168539f168))

- Cover non-JSON-serializable message field validation
  ([`b2b8f7e`](https://github.com/ivellios/celery-signal-receivers/commit/b2b8f7eba99ed10f7099623e70f16a57f557f0fb))

- Lock in that registered task run doesn't leak receiver signature
  ([`6d9b3f2`](https://github.com/ivellios/celery-signal-receivers/commit/6d9b3f2579393bc6f322f5f5d7570224a2582405))


## v0.3.0 (2026-07-20)

### Bug Fixes

- Bump django-unified-signals floor to 0.4.1
  ([`33949e6`](https://github.com/ivellios/celery-signal-receivers/commit/33949e6055e96d16fabab9ea72da783bac4440c1))

- Satisfy ruff-lint (exception chaining, dict literal, re-export, arg order)
  ([`fb32cfd`](https://github.com/ivellios/celery-signal-receivers/commit/fb32cfdbd49a0ed2043dd920d70a44aa3a9cb407))

### Chores

- Add BSD-3-Clause to liccheck authorized licenses
  ([`f73a95e`](https://github.com/ivellios/celery-signal-receivers/commit/f73a95e1cafa8b43444ebb639a20c24880167504))

- Authorize SPDX-style Apache-2.0/BSD-2-Clause in liccheck
  ([`1a5d4b4`](https://github.com/ivellios/celery-signal-receivers/commit/1a5d4b4761daf696d9a9ff9a877873eb815d1d9c))

- Convert ci.yaml to uv, bump matrix to py3.11-3.13/dj5.2-6.0
  ([`0860643`](https://github.com/ivellios/celery-signal-receivers/commit/08606438566e21becc5f0019cbfaad99f3985656))

- Convert tox.ini to uv/ruff matrix
  ([`0e27632`](https://github.com/ivellios/celery-signal-receivers/commit/0e27632d906b0ec95a2a84a243e1c8e51aee3176))

- Drop unused tox install from workflow_security.yaml
  ([`7a79cbe`](https://github.com/ivellios/celery-signal-receivers/commit/7a79cbe7dc1263e6be325b07494ab10005f54467))

- Migrate to uv + hatchling
  ([`b04c055`](https://github.com/ivellios/celery-signal-receivers/commit/b04c055b4fb1fcd6abcc876ee75237c32ff8df4c))

### Features

- Add pre-commit hooks and python-semantic-release automation
  ([`da9c498`](https://github.com/ivellios/celery-signal-receivers/commit/da9c49852637ee72601e5ff7ba0cb6df196e81c5))


## v0.2.1 (2024-10-10)


## v0.2.0 (2024-10-07)

### Features

- **package**: Add support for using with Django@5
  ([`94acb98`](https://github.com/ivellios/celery-signal-receivers/commit/94acb9816176cecae352c71a6c0306421047480a))


## v0.1.0 (2023-09-22)

- Initial Release
