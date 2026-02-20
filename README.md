# Random Moving Dot

An interactive application featuring a smooth animated shape that moves randomly around the screen. 

---

## Features

- **Multiple UI Options**: Run using CustomTkinter (native desktop) or Streamlit (web-based)
- **Customizable Animation**: Control speed, shape type, and colors
- **Dynamic Shapes**: Support for circles, squares, and other geometries
- **Color Picker**: Customize dot and background colors
- **Frame Rate Display**: Real-time speed feedback in frames per second

---

## Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

For CustomTkinter app:
- customtkinter
- darkdetect
- packaging

For Streamlit app:
- streamlit

---

## Installation

### 1. Create and Activate Virtual Environment

#### Windows (Command Prompt)
```cmd
python -m venv .venv
.venv\Scripts\activate
```

#### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If you receive an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application


### Streamlit Web App
```bash
python launcher.py
```

Alternatively, run Streamlit directly:
```bash
streamlit run streamlit_app.py
```

---

## Usage

1. **Start the application** using one of the methods above
2. **Adjust controls**:
   - Speed slider to control animation speed
   - Shape selector to change dot appearance
   - Color pickers to customize dot and background colors
3. **Exit**: Close the window or use the exit button (Streamlit app)

---

## Project Structure

- `streamlit_app.py` - Web-based Streamlit interface with p5.js animation
- `launcher.py` - Application launcher for Streamlit app with native window integration
- `requirements.txt` - Python package dependencies
- `app_icon.ico` - Application icon for compiled executables

---

## Building Standalone Executables

To create a standalone `.exe` for Windows using PyInstaller:

```bash
git clone https://github.com/talha-0/RandomMovingObj

cd RandomMovingObj

pyinstaller --onefile --noconsole --name "Random Moving Obj" --icon="app_icon.ico" --add-data "streamlit_app.py;." --copy-metadata streamlit --collect-all streamlit launcher.py
```

The executable will be created in the `dist/` folder.

To run Execute the following command:
```bash
& '.\dist\Random Moving Obj.exe'
```

Or open the file.

---

## Deactivating Virtual Environment

When finished:
```bash
deactivate
```

---

## License

This project is open source and available on [Github](https://github.com/talha-0/RandomMovingObj).