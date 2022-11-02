# opensource_ai_sourcing

## Getting Started 

1. Create a virtual Environment from requirements.txt : 
`python3 -m venv ai_sourcing_env`

2. Activate your newly created environmnent
`source ai_sourcing_env/bin/activate`

3. Now, install dependencies using `requirements.txt` file
`python3 -m pip install -r requirements.txt`

4. Collect repositories data from github `python3 sourcing/collect.py` OR 
    Put the existing data in `DATA_DIR` folder the data should be named like defined in `GITHUB_REPO_FILENAME`

5. Score repositories `python3 sourcing/score   .py`