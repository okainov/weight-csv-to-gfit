# google-fit-data

Initial code and idea from https://github.com/motherapp/weight-csv-to-gfit

Modified for modern Python by [@okainov](https://github.com/okainov)

Load bulk weight/steps data to a Google Fit account

## Download and installation
```
git clone https://github.com/okainov/weight-csv-to-gfit
cd weight-csv-to-gfit
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

## Import weight data into Google Fit
```
python weight/import_weight_to_gfit.py
```

## Import steps data into Google Fit
```
python steps/import_steps_to_gfit.py
```
