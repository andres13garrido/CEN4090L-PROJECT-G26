# CEN4090L Project G26

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
python3 -m venv .venv 
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
uv pip install -e .

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
    "Weather-Demo": {
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

