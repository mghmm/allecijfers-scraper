# AlleCijfers Municipality data scraper

This script automatically downloads the “250 onderwerpen” tables for every Dutch municipality from AlleCijfers.nl and saves each set of tables into a separate Excel workbook.

---

## Features

- **Automatic discovery** of all 342 municipalities via the `/gebieden/` overview page  
- **HTML parsing** of the `#250-onderwerpen` section using BeautifulSoup  
- **Proxy support** (optional): load from `proxies.txt`  
- **Pandas → Excel**: one sheet per category, filenames like `./data/Maastricht.xlsx`  

---

## Prerequisites

- Python 3.7+  
- A working internet connection  
- (Optional) `proxies.txt` in the project root, with lines of the form: ```1.2.3.4:8080:username:password```

---

## Installation

1. Clone this repo (or copy `main.py` & this README)  
2. Create & activate a virtualenv (recommended)  
 ```bash
 python3 -m venv venv
 source venv/bin/activate
 ```

---

## Usage
```python main.py```

- **Outputs** will be written to ```./data/``` (create it automatically)
- Each municipality produces ```./data/<Name>.xlsx``` with one sheet per category

--- 

## Configuration

**Output directory**: adjust ```OUTPUT_DIR``` at the top of ```main.py```

**Logging level**: change ```logging.basicConfig(level=…)```

**Proxy file**: name or path can be modified in the ```ProxyManager``` constructor

