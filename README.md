# Blockchaincerts_FatApi
The repo is a smart contract for issuing and managing blockchain certificates

## Requirements

- Python 3.7+
- FastAPI
- Uvicorn
- Other dependencies listed in `requirements.txt`

## Installation

### Clone the Repository
```bash
git clone https://github.com/Mickmacha/Blockchaincerts_FastApi.git
cd Blockchaincerts_FastApi
```

### Create a Virtual Environment to manage dependencies
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`


### Install Required dependenciess using Pip
pip install -r requirements.txt

### Running The FastApi Server
uvicorn main:app --host 0.0.0.0 --port 8080




