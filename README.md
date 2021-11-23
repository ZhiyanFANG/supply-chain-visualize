# supply-chain-visualization

![web-page](https://github.com/FzyEstelle/supply-chain-visualization/blob/main/SC1-Snapshot.png)
A simple web app to assign service times to supply chains based on its structure, stage costs, stage times and demand distributions, and visualize the supply chain on web locally.

Input file sample: `SC-Form.xls` (source: Sean P. Willams, 2007: https://pubsonline.informs.org/doi/suppl/10.1287/msom.1070.0176).

Optimization model and algorithm: Magnanti, et al., 2006 (https://www.sciencedirect.com/science/article/abs/pii/S0167637705000477).

Note that both stage time and demand can be random, which makes our model slightly different from that above.

## User Guide

### Preparation

* Download and install NodeJS.
* Download Gem on its official website and conduct environment settings.
* Install gulp and downgrade gulp to version 10.

### Data Input

* Write your supply chain data into the file 'SC-Form.xls' according to the following formation:

---

* Run the web app:

   ```bash
   > cd <your directory>/supply-chain-visualization
   > python3 DataHandler.py
   > cd visualization
   > gem install sass
   > npm install
   > gulp
   ```

   and open your browser to the web `http://localhost:8080`.

## Important Notes

1. Assume that if a stage receiving products from more than one manufacturer, all those manufacturers produce the same product;

2. It may cause faults if StageId in the input excel is not in order.

## Reference

* All visualization codes are based on https://github.com/eisman/neo4jd3.

* Solver: https://developers.google.com/optimization.
