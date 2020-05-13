# MazeClerk

 This project serves as a toolkit to populate and fix experimental dataset in Radial Maze Experient.
 
 The project is based on <a href=https://www.nature.com/articles/s41598-019-56408-9>ezTrack</a><sup>[1]</sup>, an open-source video analysis pipeline for the investigation of animal behavior. 
 
 ## Venv(optional)
 
  On windows: open cmd and run ```path\MazeClerk\Venv\Scripts\activate```. 
 
 
 ## Data
 
 **table1**: primary mice data (by 02-29-2020)
 **table2**: session records from 07-19-2019 to 02-29-2020 
 
 
 ## Pipeline Files
 
 **Pipeline_Individual.ipynb**: notebook for individual analysis (location tracking, velocity calculation and arm retrieval performance)
 **Pipeline_BatchProcess.ipynb**: not tested yet
 **PerformanceAnalysis.ipynb**: notebook for group analysis

 
 ## Lib
 
 **gui.py**: run data collection gui
 **LocationTracking_Functions.py and VelocityAndArmRetrieval_Functions.py**: define functions for location tracking and individual analysis pipeline
 **FreezeAnalysis_Functions.py**: not used in individual tracking
 **TrialDataAutofill_Functions.py**: not completed
 
 
 [1]Pennington, Z.T., Dong, Z., Feng, Y. et al. ezTrack: An open-source video analysis pipeline for the investigation of animal behavior. Sci Rep 9, 19979 (2019). https://doi.org/10.1038/s41598-019-56408-9
