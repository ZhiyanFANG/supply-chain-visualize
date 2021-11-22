# supply-chain-visualization
![This is an image](https://github.com/FzyEstelle/supply-chain-visualization/blob/main/SC1-Snapshot.png)
A simple web app to assign service times to supply chains based on its structure, stage costs, stage times and demand distributions, and visualize the supply chain on web locally.

Input file sample: `SC1.xls` (source: Sean P. Willams, 2007: https://pubsonline.informs.org/doi/suppl/10.1287/msom.1070.0176).

Optimization model and algorithm: Magnanti, et al., 2006 (https://www.sciencedirect.com/science/article/abs/pii/S0167637705000477).

Note that both stage time and demand can be random, which makes our model slightly different from that above.

### Important Notes
1. Assume that if a stage receiving products from more than one manufacturer, all those manufacturers produce the same product;

2. It may cause faults if StageId in the input excel is not in order.

### Tutorial
1. Download and install NodeJS;

2. Download Gem on its official website and conduct environment settings;

3. Install gulp and downgrade gulp to version 10;

4. Run the web app.
   ```
   $ cd <your downloaded supply-chain-visualization folder>
   $ gem install sass
   $ npm install
   $ python3 DataHandler.py
   $ gulp
   ```

### Reference
1. All visualization codes are based on https://github.com/eisman/neo4jd3.

2. Solver: https://developers.google.com/optimization.
