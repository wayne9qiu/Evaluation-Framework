import pandas as pd
import numpy as np
import classification_data_manager as data_manager
import classification_model as model
import csv
from collections import defaultdict
import codecs

class Evaluator:
    def __init__(self):
        print("Classification evaluator init")

    @staticmethod
    def evaluate(vector_filename, vector_size, results_folder):
        gold_standard_filenames = ['Cities', 'MetacriticMovies', 'MetacriticAlbums', 'AAUP', 'Forbes']

        #for reproducibility
        seedVector = [1,2,3,4,5,6,7,8,9,10]

        for gold_standard_filename in gold_standard_filenames:
            gold_standard_file = 'ClassificationAndRegression/data/'+gold_standard_filename+'.tsv'

            classification_model_names = ["NB", "KNN", "C45"]
            SVM_configurations = [pow(10, -3), pow(10, -2), 0.1, 1.0, 10.0, pow(10, 2), pow(10, 3)]

            regression_model_names = ["LR", "KNN", "M5"]

            scores = defaultdict(list)

            data, ignored = data_manager.DataManager.read_data(vector_filename, vector_size, gold_standard_file)

            print('Classification : Ignored data: ' + str(len(ignored)))
            
            file_ignored = codecs.open(results_folder+'/classification_'+gold_standard_filename+'_ignoredData.txt',"w", 'utf-8') 
            for ignored_data in ignored:
                print('Classification : Ignored data: ' + ignored_data)
                file_ignored.write(ignored_data+'\n')
            file_ignored.close() 

            if data.size == 0:
                print('Classification : Problems in merging vector with gold standard ' + gold_standard_file)
            else:
                for i in range(10):
                    data = data.sample(frac=1, random_state=seedVector[i]).reset_index(drop=True)
                    for model_name in classification_model_names:
                        # initialize the model
                        classification_model = model.ClassificationModel(model_name)
                        # train and print score
                        scores[model_name].append(classification_model.train(data))
                    for conf in SVM_configurations:
                        # initialize the model
                        classification_model = model.ClassificationModel("SVM", conf)
                        # train and print score
                        scores["SVM"].append(classification_model.train(data))

            with open(results_folder+'/classification_'+gold_standard_filename+'_results.csv', "wb") as csv_file:
                fieldnames = ['task_name', 'model_name', 'model_configuration', 'score_type', 'score_value']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()

                for (method, scoresForMethod) in scores.items():
                    for score in scoresForMethod:
                        writer.writerow(score)
                
           

            

                        