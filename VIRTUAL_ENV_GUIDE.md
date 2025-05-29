# Virtual Environment Setup Guide

This project uses a Python virtual environment to manage dependencies and ensure consistent behavior across different systems.

## Quick Start

### Activate Virtual Environment
```bash
# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### Deactivate Virtual Environment
```bash
deactivate
```

### Install Dependencies
```bash
# After activating the virtual environment
pip install -r requirements.txt
```

## Setting Up From Scratch

If you're cloning this repository for the first time:

### 1. Clone the Repository
```bash
git clone https://github.com/alexandrehuynh/client_outreach.git
cd client_outreach
```

### 2. Create Virtual Environment
```bash
# Python 3.8+ required
python3 -m venv venv
```

### 3. Activate Virtual Environment
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Test Installation
```bash
python test_setup.py
```

## Virtual Environment Benefits

✅ **Isolated Dependencies**: Prevents conflicts with other Python projects  
✅ **Reproducible Environment**: Same package versions across all systems  
✅ **Easy Deployment**: Simple requirements.txt for setup  
✅ **Clean System**: Doesn't modify system-wide Python installation  

## Important Notes

- **Never commit the `venv/` folder** - It's excluded in `.gitignore`
- **Always activate before working** - Ensures you're using the right packages
- **Update requirements.txt** if you add new packages:
  ```bash
  pip freeze > requirements.txt
  ```

## Troubleshooting

### Virtual Environment Not Found
```bash
# Recreate it
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Package Import Errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Python Version Issues
This project requires Python 3.8+. Check your version:
```bash
python --version
```

If you need a different Python version, create the virtual environment with:
```bash
python3.9 -m venv venv  # Example for Python 3.9
```

## IDE Setup

### VS Code
1. Install the Python extension
2. Open the project folder
3. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
4. Type "Python: Select Interpreter"
5. Choose the interpreter in `./venv/bin/python`

### PyCharm
1. Open the project
2. Go to File → Settings → Project → Python Interpreter
3. Click the gear icon → Add
4. Choose "Existing Environment"
5. Select `./venv/bin/python`

## Running the Application

Always activate the virtual environment first:
```bash
source venv/bin/activate
python main.py --mode status
``` 