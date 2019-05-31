Here are all the code needed for 200 PU analysis as well as resulting figs



## Batch
First step is preprocessing the ntuples. For this we use a batch system to speed up the process.
To run the batchscript just use with python3 python batch.py -p "parameters_file" 
Where paramaters file is the name of the python file with your parameters, without the .py


Then use batch_merge to merge the files for further use. The feature_analysis notebook allows you to get plots for feature distribution such as correlation matrices, violin plots etc.

## BDT
The BDT_* notebooks contain the code to trains the BDTs. Transverse is the version that trains only on transverse variables and nosplit run the training on the full dataset to avoid fluctuations due to small sample size. Tuning was used for hyperparameters tuning

##NN
The NN notebook was used to create the neural network and tune it, while the NN-BDT is used for the final comparison.

##figs
the V_* directories contains different version of the plots. v_4,5,6 are for old v8 geometry while v_8 is for the current v9. V9 is for v9 geometry but added BestChoice selection.

