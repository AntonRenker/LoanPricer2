if __name__ == "__main__":
    from backend import Schedule
    from backend import CubicSpline
    import QuantLib as ql
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
    schedule_jaso = Schedule.init_with_ql(input=input)