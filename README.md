# CEN4090L-PROJECT-G26
Personal Assistant

This repository contains the CEN4090L Group 26 project.

## Requirements

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

Dependencies are managed in `pyproject.toml`.

This project uses the following Python packages:

- `fastmcp`  
- `python-dotenv`  
- `aiohttp`  

---

## Setup Instructions

## Make sure you install it in the root directory, if you save it in a /onedrive/project it will not work so save it in desktop or something similar.

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/CEN4090L-PROJECT-G26.git
cd CEN4090L-PROJECT-G26
```


### 2. Create virtual environment 
```bash
uv venv .venv --python 3.11
```

### 3. Activate the virtual environment 
```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows cmd
.venv\Scripts\activate.bat

```

### 4. Install the dependencies
```bash
pip install aiohttp fastmcp python-dotenv

pip install "mcp[cli]"
```


### 5. Add the file into claude config
#### a. Install claude desktop 
#### b. At the top in mac you will see file->settings
#### c. After you are in settings open developer 
#### d. Click at edit config and open the file that will redirect you to

### 6. Add this into the mcp.config.json 
```json
{
  "mcpServers": {
    "Personal-Assistant": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/directory",
        "run",
        "main.py"
      ]
    }
  }
}
```

### 7. Now in claude desktop, you should be able to see it running 


## To debug use 
```bash
mcp dev main.py 
```
### Here you can see if the API is actually being called. 

