## Running CI checks locally (and in GitHub CI using `pre-commit`)

This project uses `pre-commit` to run the tests in `virtualenv`s for Python2.7
and Python3.x:

The pre-commit configuration defines how it runs
`pytest`, `pylint` and static analysis using `mypy`, `pyright`, and `pytype`.
Links:

- https://mypy.readthedocs.io/en/stable/
- https://microsoft.github.io/pyright/
- https://google.github.io/pytype/user_guide.html

- Because this project straddles Python2 and Python3, type comments as described
  in PEP 484 is used instead of Python3 type annotations:
[Suggested syntax for Python 2.7 and straddling code](https://peps.python.org/pep-0484/#suggested-syntax-for-python-2-7-and-straddling-code)

`pre-commit` runs the full analysis and test suite for Python 2.7 and 3.x.
It is used locally before commit/push and for GitHub CI:

```bash
pip3 install pre-commit
pre-commit run -av
```
Without -a, it would only run hooks for staged files with changes.
With `-a`, `pre-commit run -a` runs all fixes and checks.

You can skip checks if you commit by passing `SKIP=` in the environment:
```py
export SKIP=mypy,pylint;git commit -m "quick save"  # (or for --amend)
```

Only the 1st invocation of pre-commit will be slow as it creates `virtualenv`s
for each sub-hook configured in its configuration file
[.pre-commit-config.yaml](.pre-commit-config.yaml). Subsequent runs are fast.

If a formatting hook like trailing-whitespace fails, just run `git add -p` to
stage the whitespace fixes into the index and run pre-commit again.
Or, if you already installed pre-commit as a git commit hook, commit again.

When you are ready to use pre-commit as a pre-commit hook in this clone,
run this command to install it. Until uninstalled from this repo, it will
then run on each commit. This is completely optional and just a matter of
preference:
```bash
pre-commit install
```

### The easy way to keep your repos tidy (5 minutes)
[![The easy way to keep your repos tidy.](https://img.youtube.com/vi/psjz6rwzMdk/0.jpg)](https://www.youtube.com/watch?v=psjz6rwzMdk)

### Python Pre-Commit Hooks Setup in a single video (9 minutes)
[![Python Pre-Commit Hooks Setup in a single video](https://img.youtube.com/vi/Wmw-VGSjSNg/0.jpg)](https://www.youtube.com/watch?v=Wmw-VGSjSNg)

### Configuring Pre-Commit Hooks to Automate Python Testing and Linting in vscode (15 mins)
[![Configuring Pre-Commit Hooks to Automate Python Testing and Linting in vscode](https://img.youtube.com/vi/moVieAAk_xo/0.jpg)](https://www.youtube.com/watch?moVieAAk_xo)
