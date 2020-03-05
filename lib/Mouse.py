import lib.TrialDataAutofill_Functions as autofill
import pandas as pd
import datetime

def get_info(database,m_ID,attribute):

    if attribute=='DOB':
        df = database.loc[database['Mouse ID']==m_ID][attribute]
        return pd.to_datetime(df)
    else:
        return str(database.loc[database['Mouse ID']==m_ID][attribute])

class Mouse(object):

    def __init__(self,m_ID,group,database):

        self.ID = m_ID
        self.group = group
        self.genotype = get_info(database,m_ID,'Genotype')
        self.gender = get_info(database,m_ID,'Gender')
        self.line = get_info(database,m_ID,'Line')
        self.genotype_2 = get_info(database,m_ID,'Genotype 2')
        self.genotype_3 = get_info(database,m_ID,'Genotype 3')
        self.father = get_info(database,m_ID,'Father')
        self.mother = get_info(database,m_ID,'Mother')
        self.dob = get_info(database,m_ID,'DOB')
        self.maze_configuration = get_info(database,m_ID,'Maze Configuration')