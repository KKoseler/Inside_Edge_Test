"""Main script for generating output.csv."""
import pandas as pd

def main():
    # Read in the raw data from csv
    pitch_data = pd.read_csv('./data/raw/pitchdata.csv')
    
    # Read the combinations.txt file
    combinations = open('./data/reference/combinations.txt', 'r')
    
    # We won't use this header
    header = combinations.readline()
    
    # create the dict mapping stat to its proper function
    stat_to_func = {'AVG': avgStat, 'OBP': obpStat, 
                    'SLG': slgStat, 'OPS': opsStat}
    # do the same for split
    split_to_func = {'vs RHP': splitRHP, 'vs LHP': splitLHP, 
                     'vs LHH': splitLHH, 'vs RHH': splitRHH}
    
    # initialize our empty master dataframe
    master_df = None
    
    # loop through the file
    for line in combinations:
        # grab info from each line
        stat, subject, split = line.split(',')
        split = split.strip('\n')
        
        # perform the calculations based on stat and split values
        grouped_df = split_to_func[split](pitch_data, subject)
        grouped_df = stat_to_func[stat](grouped_df)
            
        # add the Stat, Subject and Split columns
        grouped_df['Stat'] = stat
        grouped_df['Split'] = split
        grouped_df['Subject'] = subject
        
        # Name the subject column appropriately
        grouped_df.rename(columns={subject: 'SubjectId'}, inplace=True)
        # re-order the columns
        grouped_df = grouped_df[['SubjectId', 'Stat', 'Split', 'Subject', 'Value']]
        # add the grouped_df to the master_df
        master_df = pd.concat([master_df, grouped_df])
    
    # sort by first 4 columns ascending and set SubjectId as the index
    master_df.sort_values(['SubjectId', 'Stat', 'Split', 'Subject'], inplace=True)
    master_df.set_index('SubjectId', inplace=True)
    
    # output the master file to csv
    master_df.to_csv('./data/processed/output.csv')
    
def splitRHP(pitch_df, subject):
    temp_df = pitch_df[pitch_df['PitcherSide'] == 'R']
    return temp_df.groupby([subject])

def splitLHP(pitch_df, subject):
    temp_df = pitch_df[pitch_df['PitcherSide'] == 'L']
    return temp_df.groupby([subject])

def splitLHH(pitch_df, subject):
    temp_df = pitch_df[pitch_df['HitterSide'] == 'L']
    return temp_df.groupby([subject])

def splitRHH(pitch_df, subject):
    temp_df = pitch_df[pitch_df['HitterSide'] == 'R']
    return temp_df.groupby([subject])
    
def avgStat(avg_df):
    # grab the sums for columns needed for AVG calculation
    avg_df = avg_df[['PA', 'H', 'AB']].sum()
            
    # Only grab rows with PA >= 25
    avg_df = avg_df[avg_df['PA'] >= 25]
    
    # calculate avg stat            
    avg_df.reset_index(inplace=True)
    avg_df['Value'] = round(avg_df['H'] / avg_df['AB'], 3)
    
    return avg_df


def obpStat(obp_df):
    # grab sums for columns needed for OBP calculation
    obp_df = obp_df[['H', 'HBP', 'AB', 'BB', 'SF', 'PA']].sum()
    
    # only grab rows with PA >= 25
    obp_df = obp_df[obp_df['PA'] >= 25]
    
    # calculate obp stat
    obp_df.reset_index(inplace=True)
    obp_df['Value'] = round((obp_df['H'] + obp_df['BB'] + obp_df['HBP']) / 
                            (obp_df['AB'] + obp_df['BB'] + obp_df['HBP'] 
                            + obp_df['SF']) , 3)
    
    return obp_df

def slgStat(slg_df):
    # grab sums for columns needed for SLG calculation
    slg_df = slg_df[['TB', 'AB', 'PA']].sum()
    
    # only grab rows with PA >= 25
    slg_df = slg_df[slg_df['PA'] >= 25]
    
    # calculate slugging stat
    slg_df.reset_index(inplace=True)
    slg_df['Value'] = round(slg_df['TB'] / slg_df['AB'], 3)
    
    return slg_df

def opsStat(ops_df):
    # grab sums for columns needed for OPS calculation
    ops_df = ops_df[['H', 'HBP', 'AB', 'BB', 'SF', 'PA', 'TB']].sum()
    
    # only grab rows with PA >= 25
    ops_df = ops_df[ops_df['PA'] >= 25]
    
    # calculate ops stat
    ops_df.reset_index(inplace=True)
    ops_df['Value'] = round((ops_df['H'] + ops_df['BB'] + ops_df['HBP']) /
                      (ops_df['AB'] + ops_df['BB'] + ops_df['HBP'] + ops_df['SF'])
                      + (ops_df['TB'] / ops_df['AB']), 3)
    return ops_df

if __name__ == '__main__':
    main()
