# Nile Test

Nile test is a package providing tools for extending locust.io.

These tools come in three categories
1. Nile Server Integration (integration module)
2. Data Flow Modeling (dataflow module)
3. ToxiProxy Configuratoin (toxiproxy module)

This documentation is a work in progress

## Testing

To begin testing first enter the `nile_test_library` directory

If you don't want coverage run:
```
python -m pytest
```

If you do want coverage run:
```
python -m pytest --cov-report term-missing --cov=nile_test
```
