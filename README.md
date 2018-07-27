# Anomaloy Detection in Logs - POC 

This repository contains the prototype for a Log Anomaly Detector. It currently uses ElasticSearch as its source of data, gensim for log encoding, and Self-Organizing maps for analyzing logs. 

This repo has two main scripts **trainer.py** and ***infer.py***. 
* trainer.py trains our log analysis model and saves it to disk. 
* infer.py uses the trained model to analyis logs continually. 


Both Scripts rely on correctly configuring the environment varaibles in env.sh where the prefix LADT_ denotes training paramters and LADI_ denotes inference parameters.

LADT_ELASTICSEARCH_ENDPOINT= address to Elasticsearch endpoint
LADT_MODEL= path to SOM map to update 
LADT_INDEX= name of Elasticsearch index to pull logs from 
LADT_TIME_SPAN= number of seconds from now that you would like to query Elasticsearch for
LADT_MAX_ENTRIES= limits the number of entries returned from Elasticsearch for the training query
LADT_ITERS= number of training iterations of the SOM 
LADT_SERVICE= name of Elasticsearch service to be monitored 

LADI_ELASTICSEARCH_ENDPOINT= address to Elasticsearch endpoint
LADI_INDEX= path to SOM map to test against
LADI_OUTDEX= name of index the anoamliy data will be pushed back to in Elasticsearch
LADI_TIME_SPAN=number of seconds from now that you would like to query Elasticsearch for
LADI_MAX_ENTRIES=limits the number of entries returned from Elasticsearch for the inference query
LADI_SERVICE= name of Elasticsearch service to be monitored 
LADI_THRESHOLD= float tunes the anomaly threshold based on the max value of the training set
LADI_MAX_ANOMALIES= maximum number of anomalies allowed on each testing iteration



**trainer.py*** will load a saved model if it exists, pull the last N minutes of data from a user specified service from ES up to X records and will iterate over the SOM T times. It will then save the word2vec models, the SOM map, baseline meta_data about the training set, and a plot of the U-map to your working directory. It takes about 8 minutes to process 10 minutes (~15,000 logs) of data for one service.

**infer.py** currently loads the information saved by trainer.py. To run this script simply use `python infer.py` from the command line. This script also has a 'while True' loop so that every minute it pulls the last minute of data and generates an anomaly score for each log until you manually shut it down. At each minute it will look at the N most anomalous logs and print their messages out if they are .99 times greater than the training data's max distance.