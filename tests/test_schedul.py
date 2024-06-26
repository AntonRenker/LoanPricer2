import QuantLib as ql
import sys
import os
import pandas as pd

# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from backend import Schedule


if __name__ == "__main__":
    input = {
        "effectiveDate": ql.Date("2024-02-01", "%Y-%m-%d"),
        "tenor": "5Y",
        "frequency":  '3M', # ql.Period("3M"),
        "calendar": ql.Germany(ql.Germany.Settlement),
        "holidayConvention": ql.Preceding,
        "terminationDateConvention": ql.Preceding,
        "dateGenerationRule": ql.DateGeneration.Forward,
        "endOfMonthRule": False,
        "dayCountConvention": ql.Actual360(),
        "facilityType": 1, # 1 for Fixed Rate Amortizing Loan 
        "bankComitment0": 1_000_000, # Currency is assumed to be EUR
    }
    schedule = Schedule.init_with_ql(input=input)
    print(schedule)