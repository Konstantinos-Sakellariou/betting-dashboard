import base64
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score


def image_base(image):
    return base64.b64encode(open(image, 'rb').read())


archived_predictions = (pd.read_csv('assets/csv/all_archive.csv', header=0, sep=',', index_col=0)
                        .assign(**{"Actual_Result": lambda x: np.where(x.Actual_Score_Home > x.Actual_Score_Away,
                                                                       'Assos', 'Diplo'),
                                   "Actual_Line": lambda x: np.where(
                                       x.Actual_Score_Home + x.Actual_Score_Away > x.Line, 'Over', 'Under'),

                                   "Predicted_Line": lambda x: np.where(x.Predicted_Points_Sum != x.Line,
                                                                        x.Predicted_Line, 'Draw'),
                                   }
                                )
                        .loc[lambda x: x.Predicted_Line != 'Draw']
                        .assign(odds_res_sum=lambda x: np.where(x.Predicted_Result == 'Assos',
                                                                x.Odd_Home_Mean, x.Odd_Away_Mean))
                        .assign(k_sum_res=lambda x: np.where(x.Actual_Result == x.Predicted_Result, 1, 0))
                        .assign(k_sum_lines=lambda x: np.where(x.Actual_Line == x.Predicted_Line, 1, 0))
                        )

recommended_preds_archive = (archived_predictions.loc[archived_predictions.Difference > 2.5]
                             .loc[lambda x: x.League != "NBA"]
                             .drop_duplicates(subset=['Home_Team', 'Away_Team', 'Date'])
                             .reset_index(drop=True)
                             .assign(odds_res_sum=lambda x: np.where(x.Predicted_Result == 'Assos',
                                                                     x.Odd_Home_Mean,
                                                                     x.Odd_Away_Mean))
                             .assign(k_sum_res=lambda x: np.where(
    x.Actual_Result == x.Predicted_Result,
    1, 0))
                             .assign(k_sum_lines=lambda x: np.where(
    x.Actual_Line == x.Predicted_Line,
    1, 0))
                             )

accuracy_line_rec = round(
    accuracy_score(recommended_preds_archive.Actual_Line, recommended_preds_archive.Predicted_Line), 2)
accuracy_result_rec = round(accuracy_score(recommended_preds_archive.Actual_Result,
                                           recommended_preds_archive.Predicted_Result), 2)
accuracy_line_all = round(accuracy_score(archived_predictions.loc[archived_predictions.League != 'NBA'].Actual_Line,
                                         archived_predictions.loc[archived_predictions.League != 'NBA'].Predicted_Line),
                          2)
accuracy_result_all = round(accuracy_score(archived_predictions.loc[archived_predictions.League != 'NBA'].Actual_Result,
                                           archived_predictions.loc[
                                               archived_predictions.League != 'NBA'].Predicted_Result), 2)

leagues = ['Recommended', 'All Predictions']
odds_lines_per_league = [1.90, 1.90]

dictionary_dataframe = {'Leagues': leagues,
                        'Accuracy Lines': [accuracy_line_rec, accuracy_line_all],
                        'Accuracy Results': [accuracy_result_rec, accuracy_line_all],
                        'Total Matches': [len(recommended_preds_archive), len(archived_predictions)],
                        'Correct Lines': [recommended_preds_archive.k_sum_lines.sum(),
                                          archived_predictions.k_sum_lines.sum()],
                        'Correct Results': [recommended_preds_archive.k_sum_res.sum(),
                                            archived_predictions.k_sum_res.sum()],
                        'Average Odds Lines': odds_lines_per_league,
                        'Average Odds Results': [
                            round(recommended_preds_archive.odds_res_sum.sum() / len(recommended_preds_archive), 2),
                            round(archived_predictions.odds_res_sum.sum() / len(archived_predictions), 2)]}

dataframe = pd.DataFrame(data=dictionary_dataframe)

_ = recommended_preds_archive.drop(['odds_res_sum', 'k_sum_res', 'k_sum_lines'], axis=1, inplace=True)
_ = archived_predictions.drop(['odds_res_sum', 'k_sum_res', 'k_sum_lines'], axis=1, inplace=True)

leagues = []
accuracy_line_leagues = []
accuracy_results_leagues = []
total_size_per_league = []

correct_lines_per_league = []
correct_results_per_league = []

odds_results_per_league = []
odds_lines_per_league = []

for league in archived_predictions.League.unique().tolist():
    leagues.append(league)

    league_data = (archived_predictions.loc[lambda x: x.League == league]
                   .assign(k_sum=lambda x: np.where(x.Actual_Line == x.Predicted_Line, 1, 0))
                   .assign(k_sum_res=lambda x: np.where(x.Actual_Result == x.Predicted_Result, 1, 0))
                   .assign(odds_sum=lambda x: np.where(x.Predicted_Result == 'Assos',
                                                       x.Odd_Home_Mean, x.Odd_Away_Mean))
                   )

    accuracy_line_leagues.append(round(league_data.k_sum.sum() / len(league_data), 2))
    accuracy_results_leagues.append(round(league_data.k_sum_res.sum() / len(league_data), 2))
    total_size_per_league.append(len(league_data))

    correct_lines_per_league.append(league_data.k_sum.sum())
    correct_results_per_league.append(league_data.k_sum_res.sum())

    odds_results_per_league.append(round(league_data.odds_sum.sum() / len(league_data), 2))
    odds_lines_per_league.append(1.90)

dictionary_dataframe = {'Leagues': leagues,
                        'Accuracy Lines': accuracy_line_leagues,
                        'Accuracy Results': accuracy_results_leagues,
                        'Total Matches': total_size_per_league,
                        'Correct Lines': correct_lines_per_league,
                        'Correct Results': correct_results_per_league,
                        'Average Odds Lines': odds_lines_per_league,
                        'Average Odds Results': odds_results_per_league}

dataframe_2 = pd.DataFrame(data=dictionary_dataframe)
predictions_summary_table = pd.concat([dataframe, dataframe_2]).reset_index(drop=True)

predictions_dataset = (pd.read_csv('assets/csv/next_days89.csv', header=0, sep=',', index_col=0)
                       .assign(Predicted_Line=lambda x: np.where(x.Predicted_Points_Sum == x.Line,
                                                                 'No Pred', x.Predicted_Line)))

recommended_preds = predictions_dataset.loc[predictions_dataset.Difference > 2.5][['Date', 'Time', 'League',
                                                                                   'Home_Team', 'Away_Team',
                                                                                   'Line', 'Predicted_Line']]

dataset = (pd.read_csv('assets/csv/nba_plus_europe.csv', header=0, sep=',', index_col=0)
           .assign(Result=lambda x: np.where(x.Score_home > x.Score_away,
                                             'Assos', 'Diplo')))

cols = ['Date', 'Time', 'League', 'Season', 'Home_Team', 'Away_Team', 'Result', 'Line', 'Odd_Over', 'Odd_Under',
        'Odd_Home_Mean',
        'Odd_Away_Mean', 'Odd_Home_Min_Max_Difference', 'Odd_Away_Min_Max_Difference', 'Mean_Home_Winning_Probability',
        'Mean_Away_Winning_Probability', 'Home_Team_Home_Scoring', 'Away_Team_Away_Scoring', 'Home_Team_Total_Scoring',
        'Away_Team_Total_Scoring', 'Score_home', 'Score_away']

dataset = dataset[cols]
