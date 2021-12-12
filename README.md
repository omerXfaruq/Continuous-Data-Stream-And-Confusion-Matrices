# Continuous-Data-Source & Confusion-Matrix-Calculation

_By FarukOzderim_

## Description

This is a continuous calculation of confusion matrices with a concurrent simulated continuous data source.

Whenever there is new incoming data, this program calculates the confusion matrices with moving windows and writes them to the database.

## Requirements

```
pip3 install -r requirements.txt
```

## Run

```
rm database.db
python3 -m src.__init__ [input] [close_after_seconds] [confusion_matrix_window_length] [debug]
```

Examples:

```
rm database.db
python3 -m src.__init__ test/data/data_small.csv 10 3 True
```

```
rm database.db
python3 -m src.__init__ test/data/data.csv 600 1000 False
```

## Tests

```
pytest -v --cov=src --cov-report term-missing test/unit.py
```

Tests take around 30 seconds

## Input
```
id,given_label,model1_A,model1_B,model2_A,model2_B,model3_A,model3_B
1,A,0.6315429094436551,0.3684570905563449,0.9881789935400176,0.011821006459982408,0.7254980531654877,0.27450194683451234
```
There are 3  ML models, and each modelX_Y represents probability of model X predicting that the label is Y.
We combine ML models' results and predict the label and create confusion matrices with that prediction.
https://en.wikipedia.org/wiki/Confusion_matrix
!image[img/confusion_matrix]