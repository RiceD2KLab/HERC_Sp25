from utils.getData import engineer_performance
import pandas as pd

options = [
    'STAAR Testing',
    'Dropout Rate',
    'Attendance',
    'Chronic Absenteeism',
    'College, Career, & Military Ready Graduates',
    '4-Year Longitudinal Graduation Rate',
    'AP/IB',
    'SAT/ACT'
]

suboptions = {'STAAR Testing': [
    'Mathematics',
    'Reading/ELA',
    'Science',
    'Social Studies'
    ],
             '4-Year Longitudinal Graduation Rate': ['RHSP/DAP or FHSP-E/DLA', 'FHSP-DLA Graduates'],
             'AP/IB': ['Course Completion Graduates', 'Test Taking', 'Students Above Criterion'],
             'SAT/ACT': ['Graduates Above Criterion', 'Students Above Criterion', 'Test Taking']}

demographics = {
    'All':'All Students',
    'African American':'African American',
    'White': 'White',
    'Econ Disadv': 'Economically Disadvantaged',
    'Special Ed': 'Special Education',
    'EB/EL': 'Emergent Bilingual/English Learner',
    'Hispanic': 'Hispanic'
}

demographic_string_patterns = {'AP/IB': {'Course Completion Graduates': r"AP/IB Course Completion Graduates: (.*) Rate",
                                         'Test Taking':  r'AP/IB: (.*) \((All Subjects)\) % Taking', 
                                         'Students Above Criterion': r"AP/IB: (.*) \((All Subjects)\) % Students Above Criterion"},
                               'SAT/ACT': {'Test Taking':r'SAT/ACT: (.*), % Test-Taking', 
                                           'Graduates Above Criterion':r'SAT/ACT: (.*), % Graduates Above Criterion', 
                                           'Students Above Criterion':r"SAT/ACT: (.*?), % Above Criterion"},
                               '4-Year Longitudinal Graduation Rate': {'RHSP/DAP or FHSP-E/DLA':r"for (.*) Rate$",
                                                                       'FHSP-DLA Graduates': r"for (.*) Rate$"},
                               'College, Career, & Military Ready Graduates': r'College, Career, & Military Ready Graduates: (.*) Rate',
                               'Dropout Rate': r'(.*) Dropout Rate',
                               'Attendance': r'Attendance: (.*) Rate',
                               'Chronic Absenteeism': r'Chronic Absenteeism (.*) Group: Rate'
                               }