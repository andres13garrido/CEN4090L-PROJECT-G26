If it does not exist the .venv file inside this folder 

```bash
uv venv 
```

```bash
source .venv/bin/activate

uv pip install -e . 
```

Add this in the json.config 

```json
      "FileSystem-Tools": {
        "command": "uv",
        "args": [
          "--directory",
          "/Path/To/Folder", 
          "run",
          "main.py",
          "Path/Which/You/Want/to/Give/Access"
        ]
      }


```