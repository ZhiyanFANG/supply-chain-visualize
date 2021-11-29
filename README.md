# supply-chain-visualization

![web-page](https://github.com/FzyEstelle/supply-chain-visualization/blob/main/demo.png)
This project designs a tool that is able to optimize supply chain inventory placement and visualize the optimal supply chain. Specifically, it 

1) reads input supply chain data, 

2) conduct optimization according to the famous inventory placement model of Graves and Willems (2003), 

3) solve the model based on the algorithm of Magnanti, et al. (2005), 

and 4) visualize the supply chain along with its properties on a local web page.

We hope that through this tool, 
Using this tool, it is easy to adjust a supply chain and observe the corresponding optimized inventory placement intuitively. 

| File | Notes |
| ------ | ------ |
| `SC-Form.xls` | |
| `DataHandler.py` | |
| `SC-Result.csv` | |
| `visualization/docs/json/neo4jData.json` | |
| `visualization/docs/index.html` | |

This project is part of the Master Thesis of Zhiyan FANG, Institute of Operations Research and Analytics, National University of Singapore.

## Optimization Model And Algorithm

* Assume that if a stage receiving products from more than one manufacturer, all those manufacturers produce the same product.

* Holding cost calculation

* Demand calculation

* Random Lead Time

slightly different from Graves and Willems

slightly different from Magnanti, et al., 2006 (https://www.sciencedirect.com/science/article/abs/pii/S0167637705000477)

others:
stop criterion: 0.02 of real obj value; M=100; max number of iteration=1000 to avoid dead loop


## User Guide

### Data Input And Optimization

* Write your supply chain data into the file 'SC-Form.xls' according to the following formation:

* Run `DataHandler.py` to read `Excel` data, optimize the inventory placement model and output model solutions for visualization:

   ```bash
   > cd your-directory/supply-chain-visualization
   > python3 DataHandler.py
   ```

   where the visualization data file `neo4jData.json` is placed under `visualization/docs/json`, and output csv

### Visualization

* Download and install NodeJS.
* Download Gem on its official website and conduct environment settings.
* Install gulp and downgrade gulp to version 10.
* Run:

   ```bash
   > cd visualization
   > gem install sass
   > npm install
   > gulp
   ```

   and open `http://localhost:8080` in your browser.


## Reference

* Input file sample: Sean P. Willems, 2007: https://pubsonline.informs.org/doi/suppl/10.1287/msom.1070.0176.

* All visualization codes are based on https://github.com/eisman/neo4jd3.

* Solver: https://developers.google.com/optimization.
