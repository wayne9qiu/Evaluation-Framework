from regression_model import RegressionModel as Model
import csv
from collections import defaultdict
import codecs
import os
import pandas as pd

from code.abstract_taskManager import AbstractTaskManager
from numpy import mean

task_name = 'Regression'

class RegressionManager (AbstractTaskManager):
    def __init__(self, data_manager, debugging_mode):
        self.debugging_mode = debugging_mode
        self.data_manager = data_manager
        if debugging_mode:
            print("Regression task manager initialized")

    @staticmethod
    def get_task_name():
        return task_name

    def evaluate(self, vectors, vector_file, vector_size, results_folder, log_dictionary, scores_dictionary):
        log_errors = ""
        
        gold_standard_filenames = self.get_gold_standard_file()

        totalscores = defaultdict(dict)

        for gold_standard_filename in gold_standard_filenames:
            script_dir = os.path.dirname(__file__)
            rel_path = "data/"+gold_standard_filename+'.tsv'
            gold_standard_file = os.path.join(script_dir, rel_path)

            regression_model_names = ["LR", "KNN", "M5"]

            scores = defaultdict(list)
            totalscores_element = defaultdict(list)

            data, ignored = self.data_manager.intersect_vectors_goldStandard(vectors, vector_file, vector_size, gold_standard_file)

            self.storeIgnored(results_folder, gold_standard_filename, ignored)

            if data.size == 0:
                log_errors += 'Regression : Problems in merging vector with gold standard ' + gold_standard_file + '\n'
                if self.debugging_mode:
                    print('Regression : Problems in merging vector with gold standard ' + gold_standard_file)
            else:
                for i in range(10):
                    data = data.sample(frac=1, random_state=i).reset_index(drop=True)

                    for model_name in regression_model_names:
                        # initialize the model
                        model = Model(model_name, self.debugging_mode)
                        # train and print score
                        try:
                            result = model.train(data)
                            result['gold_standard_file'] = gold_standard_filename
                            scores[model_name].append(result)
                            totalscores_element[model_name].append(result) 
                        except Exception as e:
                            log_errors += 'File used as gold standard: ' + gold_standard_filename + '\n'
                            log_errors += 'Regression method: ' + model_name + '\n'
                            log_errors += str(e) + '\n'
        
                self.storeResults(results_folder, gold_standard_filename, scores)
                totalscores[gold_standard_filename] = totalscores_element

            results_df = self.resultsAsDataFrame(totalscores)
            scores_dictionary[task_name] = results_df
        
        log_dictionary[task_name] = log_errors

    def storeIgnored(self, results_folder, gold_standard_filename, ignored):
        if self.debugging_mode:
            print('Regression : Ignored data: ' + str(len(ignored)))
        
        file_ignored = codecs.open(results_folder+'/regression_'+gold_standard_filename+'_ignoredData.txt',"w", 'utf-8') 
        for ignored_tuple in ignored.itertuples():
            value = getattr(ignored_tuple,'name')
            if self.debugging_mode:
                print('Regression : Ignored data: ' + value.encode(encoding='UTF-8', errors='ignore'))
            
            if isinstance(value, str):
                value = unicode(value, "utf-8").encode(encoding='UTF-8', errors='ignore')
            file_ignored.write(value+'\n')
            
        file_ignored.close() 
                
    def storeResults(self, results_folder, gold_standard_filename, scores):
        with open(results_folder+'/regression_'+gold_standard_filename+'_results.csv', "wb") as csv_file:
            fieldnames = ['task_name', 'gold_standard_file', 'model_name', 'model_configuration', 'root_mean_squared_error']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for (method, scoresForMethod) in scores.items():
                for score in scoresForMethod:
                    writer.writerow(score)
                    if self.debugging_mode:
                        print('Regression ' + method + ' score: ' +   score)  
           
    def resultsAsDataFrame(self, scores):
        data_dict = dict()
        data_dict['task_name'] = list()
        data_dict['gold_standard_file'] = list()
        data_dict['model'] = list()
        data_dict['model_configuration'] = list()
        data_dict['metric'] = list()
        data_dict['score_value'] = list()
        
        metrics = self.get_metric_list()
        print(scores)
        
        for (gold_standard_filename, gold_standard_scores) in scores.items():
            for (method, scoresForMethod) in gold_standard_scores.items():
                for metric in metrics:
                    metric_scores = list()
                    for score in scoresForMethod:
                        metric_scores.append(score[metric])
                    metric_score = mean(metric_scores)
                    
                    score = scoresForMethod[0]
                    configuration = score['model_configuration']
                    if configuration is None:
                        configuration='-'
                        
                    data_dict['task_name'].append(score['task_name'])
                    data_dict['gold_standard_file'].append(score['gold_standard_file'])
                    data_dict['model'].append(score['model_name'])
                    data_dict['model_configuration'].append(configuration)
                    data_dict['metric'].append(metric)
                    data_dict['score_value'].append(metric_score)
        
        results_df = pd.DataFrame(data_dict, columns = ['task_name', 'gold_standard_file', 'model', 'model_configuration', 'metric', 'score_value'])
        return results_df
            
    @staticmethod
    def get_gold_standard_file():
        return ['Cities', 'MetacriticMovies', 'MetacriticAlbums', 'AAUP', 'Forbes']
    
    @staticmethod
    def get_metric_list():
        return ['root_mean_squared_error']
                        