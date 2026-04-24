# Alien Outbreak

## Setup

This project is expected to run with Python `3.13.3`.

The repo includes a `.python-version` file for `pyenv` users.
That file does not change Python by itself. It only tells `pyenv` which version to select when `pyenv` is installed and initialized in your shell.

If you do not use `pyenv`, install Python `3.13.3` manually and make sure `python` points to that version before creating the virtual environment.

### 1. Install the correct Python version

If you use `pyenv`:

```bash
pyenv install 3.13.3
pyenv local 3.13.3
```

If you do not use `pyenv`, install Python `3.13.3` with your normal package manager or installer.

### 2. Create and activate the virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the game

```bash
python main.py
```

## Notes

- Do not use Python `3.14` for this project. `pygame.mixer` had issues there during setup.
- Teammates do not need `pyenv`, but they do need Python `3.13.3`.
- If you use `pyenv` and `python` is not pointing to `3.13.3`, run `pyenv local 3.13.3` before creating the venv.
