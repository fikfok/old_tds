# Prerequisites

- install Django > 1.10.6
- install python > 3.5 and configure virtualenv
- pip install elasticsearch
- pip install csv2es
- Changes in csv2es.py:
    
```
#!python

def all_docs():
#                           'rb'
        with open(filename, 'r') if filename != '-' else sys.stdin as doc_file:
            # delimited file should include the field names as the first row
#            fieldnames = doc_file.next().strip().split(delimiter)
            fieldnames = doc_file.readline().strip().split(delimiter)
```

- Install Miniconda (https://conda.io/docs/install/quick.html)
- conda install pandas