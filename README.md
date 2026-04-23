# GameDevProject

## Setup

This project is expected to run with Python `3.13.3`.

If you use `pyenv`, the repo already includes a `.python-version` file.

### 1. Install the correct Python version

```bash
pyenv install 3.13.3
```

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
- If `python` is not pointing to `3.13.3`, run `pyenv local 3.13.3` before creating the venv.
