.PHONY: test test-verbose lint

# Run pytest in non-interactive CI-friendly mode
test:
\tPYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 pytest --maxfail=1 --disable-warnings -q

test-verbose:
\tPYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 pytest -vv

# Basic lint stub (flake8 already in requirements.txt)
lint:
\tflake8 app
