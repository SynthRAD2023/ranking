import csv
import numpy as np
import json
import warnings

def create_export_dict(csv_file):
    export_dict = {}
    with open(csv_file, 'r') as inf:
        csv_reader = csv.reader(inf)
        for line, row in enumerate(csv_reader):
            if line == 0 :
                titles = row
            else:
                submission = row[3] # Check if this ID is correct
                # check if it succeeded
                if row[8] == 'Succeeded':
                    # check if it is published
                    if row[4] == 'True':
                        if submission not in export_dict.keys():
                            export_dict[submission] = {}
                            for title, value in zip(titles, row):
                                export_dict[submission][title] = value
                                
                        else: 
                            warnings.warn('Not unique ID')
    metrics_dict = {}
    for submission, info in export_dict.items():
        metrics_dict[submission] = json.loads(info['outputs'])[0]['value']['aggregates']
    return export_dict, metrics_dict





def define_best_and_worst(metrics_dict):
    global_min = {}
    global_max = {}
    for i, (submission, metrics) in enumerate(metrics_dict.items()):
        for metric, values in metrics.items():
            if metric not in global_min.keys():
                global_min[metric] = values['mean']
            else:
                global_min[metric] = min([global_min[metric], values['mean']])
            
            if metric not in global_max.keys():
                global_max[metric] = values['mean']
            else:
                global_max[metric] = max([global_max[metric], values['mean']])
    return global_min, global_max


def normalize_metrics(metrics_dict):
    global_min, global_max = define_best_and_worst(metrics_dict)
    
    normalized = {}
    for i, (submission, metrics) in enumerate(metrics_dict.items()):
        normalized[submission] = {}
        for metric, values in metrics.items():
            if metric.lower() in ['psnr', 'ssim']:
                # a good performance is a high value
                best = global_max[metric]
                worst = global_min[metric]
            else:
                # a good performance is a low value
                best = global_min[metric]
                worst = global_max[metric]     
            
    
        
            # Normalize all results
            if best == worst:
                normalized[submission][metric] = 0.5
            else:
                normalized[submission][metric] = (values['mean'] - worst) / (best - worst)
    return normalized
                                        
    
def rank(normalized_results):
    keys = ['psnr', 'mae', 'ssim']
    
    final_ranking = {}
    for metric in keys:
        all_values = [values[metric] for _, values in normalized_results.items()]
        all_names = [submission for submission, _ in normalized_results.items()]
        final_ranking[metric] = sorted(zip(all_values, all_names))
        
        for x in final_ranking[metric]:
            print(x[1], x[0])


    
if __name__=="__main__":
    leader_board_export = '../val_exports/export_val_task1_20230703_after.csv'
    export_dict, metrics_dict = create_export_dict(leader_board_export)
    
    normalized_results = normalize_metrics(metrics_dict)
    rank(normalized_results)
    
    
    
        