# Testing

All tests are located in the folder ([`tests`](../tests))

To run the tests clone the [repository from the GitHub](https://github.com/0dminnimda/enrollment_yandex_academy)  
Open a terminal in the root of the repository and run the commands

```console
$ python -m pip install .[test]
$ python -m pytest
```

If you want to test not the local server, but one from the container, or profile the app then you can set the `utils.LOCAL` and `utils.PROFILE` to requested boolean values. Also if `utils.PROFILE` is setting `utils.LOCAL` will not change anything.
> ⚠ If you want to run tests on the container you need to set some secrets. Don't worry though, `utils.py` will guide you through, just set the `utils.LOCAL = False`.

## Files

- [`my_secrets.py`](my_secrets.py) - Secretes, used in testing
- [`my_secrets.py_template`](my_secrets.py_template) - Template file for `my_secrets.py`
- [`README.md`](README.md) - This file, nice recursion `;>`
- `test_X.py` - Script for testing `X`
- [`unit_tst.py`](unit_tst.py) - Smol collection of "manual" tests
- [`utils.py`](utils.py) - Utilities used in test scripts
