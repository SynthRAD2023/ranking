import csv
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


def define_best_and_worst(metrics_dict, aggregate='mean'):
    best, worst = {}, {}
    global_min, global_max = {}, {}
    for i, (submission, metrics) in enumerate(metrics_dict.items()):
        for metric, values in metrics.items():
            if i == 0:
                global_min[metric] = values[aggregate]
                global_max[metric] = values[aggregate]
            else:
                global_min[metric] = min([global_min[metric], values[aggregate]])
                global_max[metric] = max([global_max[metric], values[aggregate]])
                          
            if metric in ['psnr', 'ssim', 'gamma_photon', 'gamma_proton']:
                # a good performance is a high value
                best[metric] = global_max[metric]
                worst[metric] = global_min[metric]
            else:
                # a good performance is a low value
                best[metric] = global_min[metric]
                worst[metric] = global_max[metric]
    
    print('\t\t\t\tWorst \t\tBest')
    for metric in best.keys():
        print(f"{metric:16} {worst[metric]:.2f} \t\t{best[metric]:.2f}")
    print()
    return best, worst


def normalize_metrics(metrics_dict, aggregate='mean'):
    best, worst = define_best_and_worst(metrics_dict, aggregate)
    
    normalized = {}
    for i, (submission, metrics) in enumerate(metrics_dict.items()):
        normalized[submission] = {}
        for metric, values in metrics.items():
            
            # Normalize all results (0=worst score, 1=best score)
            if best[metric] == worst[metric]:
                normalized[submission][metric] = 0.5
            else:
                normalized[submission][metric] = (values[aggregate] - worst[metric]) / (best[metric] - worst[metric])
        normalized[submission]['sum'] = sum(normalized[submission].values())
    return normalized

    
def rank_and_save(normalized_results, metrics_dict, export_dict, aggregate='mean'):
    sorted_results = (sorted(normalized_results.items(), key=lambda x:x[1]['sum'], reverse=True))
    
    
    with open('final_ranking.csv', 'w') as outf:
        writer = csv.writer(outf)
        print('Rank \tTeam \t\t\t\tSummed normalized metrics')
        for team_rank, (submission, result) in enumerate(sorted_results):
            team = export_dict[submission]['title']
            team = team[team.find(' ')+1:]
            print(f"{team_rank+1:2d}   \t{team:20}\t{result['sum']:.2f}")
            
            save_row = [team_rank+1, team, submission, result['sum']]
            if team_rank == 0:
                header = ['Rank','team', 'pk','Sum of normalized metrics']
            for metric in metrics_dict[submission].keys():
                save_row.extend([metrics_dict[submission][metric][aggregate], result[metric]])
                if team_rank == 0:
                    header.extend([f"{metric} (absolute)", f"{metric} (normalized)"])                
            if team_rank == 0:
                writer.writerow(header)
            writer.writerow(save_row)

    
if __name__=="__main__":
    leader_board_export = 'leaderboard_export.csv'
    export_dict, metrics_dict = create_export_dict(leader_board_export)
    normalized_results = normalize_metrics(metrics_dict)
    rank_and_save(normalized_results, metrics_dict, export_dict)
    
    
    
        