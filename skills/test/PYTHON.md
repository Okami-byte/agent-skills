# Python testing

## Running

- **In a project with `pyproject.toml` / uv:** `uv run pytest -v`
- **Loose code with no project:** run in a throwaway environment so nothing is installed globally:
  `uv run --with pytest [--with numpy --with pandas …] pytest -v test_<module>.py`
- **Useful flags:**
  - `-x`: stop at the first failure
  - `-k <expr>`: run only matching tests
  - `--lf`: re-run only the tests that failed last time
  - `-q`: quieter output
  - `--cov=<pkg> --cov-report=term-missing`: coverage, with the needed `--with pytest-cov`

Put tests in `tests/test_<module>.py`, mirroring the package layout. For loose code, put them next to it.

## Tools worth knowing

| Need | Use |
|---|---|
| Many inputs, same assertion | `@pytest.mark.parametrize` |
| Setup/teardown, shared objects | fixtures (`@pytest.fixture`, `yield` for teardown) |
| Files | `tmp_path` fixture, never real paths |
| Env vars, attributes | `monkeypatch.setenv`, `monkeypatch.setattr` |
| Expected exceptions | `with pytest.raises(ValueError, match="…"):` |
| Logs | `caplog` |
| Time | `freezegun` / `time-machine`, or inject a clock |
| HTTP clients | `respx` (httpx), `responses` (requests) — mock at the boundary |
| FastAPI | `fastapi.testclient.TestClient` / `httpx.AsyncClient` |
| Async | `pytest-asyncio` or `anyio` |
| Property-based (find edge cases for you) | `hypothesis` |
| Real Postgres/Redis in tests | `testcontainers` |
| Server state after config (Ansible, images) | `pytest-testinfra` |

## ML / data code

- Check **shapes, dtypes and value ranges** of outputs, not exact floats. Use `pytest.approx` or `numpy.testing.assert_allclose`.
- Fix seeds (`random`, `numpy`, `torch`) so tests are deterministic.
- Train on a tiny sample, then assert that the loss goes down or that a metric beats a trivial baseline.
- Validate data schemas at the boundary (`pandera` or `pydantic`) and test that bad rows are rejected.

## Example

```python
import pytest
from pricing import apply_discount


@pytest.mark.parametrize(("price", "pct", "expected"), [(100, 10, 90), (100, 0, 100), (0, 50, 0)])
def test_apply_discount_valid_inputs(price, pct, expected):
    """Valid percentages reduce the price proportionally.

    Covers the happy path plus the zero-price and zero-percent boundaries.
    """
    assert apply_discount(price, pct) == expected


def test_apply_discount_rejects_over_100_percent():
    """A discount over 100% would produce a negative price, so it must raise."""
    with pytest.raises(ValueError, match="percent"):
        apply_discount(100, 150)
```
