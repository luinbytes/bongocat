# Bongo Cat Interactive App

A fun interactive Bongo Cat application that responds to keyboard, mouse, and controller inputs!

## Features
- Draggable Bongo Cat window
- Responds to all keyboard inputs
- Responds to controller/gamepad inputs
- Logs all interactions
- Always stays on top of other windows
- Resizable window

## Requirements
- Python 3.7+
- Required packages listed in `requirements.txt`

## Setup
1. Clone the repository:
```
git clone <repository-url>
cd <repository-folder>
```

2. Install the required packages:
```
pip install -r requirements.txt
```

3. Ensure the bongo cat images (`cat-left.png` ` cat-right.png ` `cat-rest.png`) are in the same directory as the script.

## Usage
1. Run the script:
```
python bongo_cat.py
```

2. The Bongo Cat window will appear and stay on top of other windows.
3. You can:
   - Drag the cat around with left mouse click.
   - Press any key to make the cat slap.
   - Use any controller/gamepad input to make the cat slap.
   - Resize the window as needed.

All interactions are logged in `bongo_cat_inputs.log`.

## .gitignore
Ensure the following files and directories are ignored in your repository:
- `venv/`
- `*.pyc`
- `__pycache__/`
- `*.log`
- `build/`
- `dist/`
- `.idea/`
- `.vscode/`
