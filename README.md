# Continuous-Learning

_By FarukOzderim_

## Description

This is a continuous learning from a simulated continuous data source.

## Requirements

```
pip3 install -r requirements.txt
```

## Run

```
python3 -m src.__init__ [input] [close_after_seconds]

Examples:

python3 -m src.__init__ test/data/data_small.csv 10

python3 -m src.__init__ test/data/data.csv 100
```

## Tests

```
pytest -v --cov=src --cov-report term-missing test/unit.py
```