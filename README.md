# supply-chain-visualization

![demo](https://github.com/ZhiyanFANG/supply-chain-visualize/blob/main/demo.png)
This project designs an interactive tool inspired by the industrial supply chain applications. Through this tool, users are able to optimize the guaranteed service inventory placement with random lead times, and visualize the optimized supply chain on a local web page. We hope this will help to clarify complicated relationships within a supply chain, and to identify the weak link - the specific stages in the supply chain need extra attention.

| File | Functions |
| ------ | ------ |
| `SC-Form.xls` | Store features of your input supply chain |
| `DataHandler.py` | Read input data `SC-Form.xls`, Optimize inventory, and Output solutions to `SC-Result.csv` and `neo4jData.json` |
| `SC-Result.csv` | Store features of the optimized supply chain for your reference |
| `visualization/docs/json/neo4jData.json` | Store output supply chain data for visualization |
| `visualization/docs/index.html` | Define elements in web visualization |

This project is part of the Master Thesis of Zhiyan FANG, Institute of Operations Research and Analytics, National University of Singapore.

## User Guide

### Input, Output And Optimization

* Write your supply chain data into the file `SC-Form.xls`, where each stage may contain the following features. Note that the lead time distribution is represented by a list of numbers, where no spaces needed.

| Feature | Explanation | Example | 
| ------ | ------ | ------ |
| StageId | Id of the stage | `1` |
| StageName | Name of the stage | `Dist_002` |
| RelDepth | Relative depth of the stage to network root, beginning from 0 | `0` |
| StageCost | Value added to the product at this stage | `150.00` |
| avgDemand | Average demand of the stage, from external customers | `126` |
| stdDevDemand | Standard deviation of the stage, from external customers | `132.3` |
| maxServiceTime | Maximum outbound service time of the stage, to external customers | `0` |
| ServiceLevel | Service level of the stage, to external customers | `0.95` |
| StageTime | Lead time distribution of the stage: `time1,possibility1;time2,possibility2;...` | `1,0.8;2,0.2` |
| DownstreamStage | List of its downstream stages | `2,3` |
| UpstreamStage | List of its upstream stages | `15,16` |

* Run `DataHandler.py` to read user's supply chain data, optimize the guaranteed service inventory placement model, and output files for visualization.

   ```bash
   > cd your-directory/supply-chain-visualization
   > python3 DataHandler.py
   ```

* The file `SC-Result.csv` is generated automatically, with the following features.

| Feature | Explanation | Example | 
| ------ | ------ | ------ |
| StageId | Id of the stage | `1` |
| StageName | Name of the stage | `Dist_002` |
| StageType | Type of the stage | `Dist` |
| RelDepth | Relative depth of the stage to network root, beginning from 0 | `0` |
| StageCost | Value added to the product at this stage | `150.00` |
| HoldingCost | Calcualted holding cost of the stage | `820.5` |
| avgDemand | Average demand of the stage, calcualted for all stages | `126` |
| stdDevDemand | Standard deviation of the stage, calcualted for all stages | `132.3` |
| maxServiceTime | Maximum outbound service time of the stage, to external customers | `0` |
| ServiceLevel | Service level of the stage, set for all stages | `0.95` |
| StageTime | Lead time distribution of the stage: `[[time1,possibility1],[time2,possibility2],...]` | `[[1,0.8],[2,0.2]]` |
| DownstreamStage | List of its downstream stages | `[2,3]` |
| UpstreamStage | List of its upstream stages | `[15,16]` |
| InboundServiceTime | Optimized inbound service time of the stage | `0` |
| OutboundServiceTime | Optimized outbound service time of the stage | `12` |
| SafetyInventoryCost | Optimized safety inventory cost of the stage | `111681.269` |
| SafetyInventory | Optimized safety inventory of the stage | `136.0970863` |
| ApproxObjValue | Objective value (safety inventory cost) of the stage using the piece-wise linear approximation, in the final algorithm iteration | `11681.269` |
| ObjValueGap | Gap between real objective value and the approximated one, in the final algorithm iteration | `0` |
| IteNum | Number of iterations used in the algorithm | `5` |

### Visualization

* Download and install `NodeJS`.
* Download `Gem` on its official website and configure its environment variables.
* Install `Gulp` and downgrade it to version 10.
* Run:

   ```bash
   > cd visualization
   > gem install sass
   > npm install
   > gulp
   ```

   and open `http://localhost:8080` in your browser.


## Reference

* Input file sample: Sean P. Willems, 2007: `https://pubsonline.informs.org/doi/suppl/10.1287/msom.1070.0176`.

* All visualization codes are based on `https://github.com/eisman/neo4jd3`.

* Solver: Google OR-Tools, `https://developers.google.com/optimization`;
            SCIP, `https://www.scipopt.org/index.php#license`.
