import QuantLib as ql
import pandas as pd
from backend import CubicSpline


class Schedule(pd.DataFrame):
    def __init__(self, input: dict):
        self.schedule = self.init_with_ql(input)

    @staticmethod
    def init_with_ql(input: dict):
        effectiveDate = input.get("effectiveDate")
        tenorYears = int(input.get("tenor").split("Y")[0])
        frequency = ql.Period(input.get("frequency"))
        terminationDate = ql.Date(effectiveDate.dayOfMonth(), effectiveDate.month(), effectiveDate.year() + tenorYears)
        ql_schedule = ql.Schedule(effectiveDate, terminationDate, frequency, input.get("calendar"), input.get("holidayConvention"), input.get("terminationDateConvention"), input.get("dateGenerationRule"), input.get("endOfMonthRule"))

        schedule = pd.DataFrame({
            "StartDate": list(ql_schedule)[:-1],
            "EndDate": list(ql_schedule)[1:],
        })

        schedule["MidDate"] = [ql.Date((StartDate.serialNumber() + EndDate.serialNumber()) // 2) for StartDate, EndDate in zip(schedule.StartDate, schedule.EndDate)]
        schedule["DayCountFraction"] = [input.get("dayCountConvention").yearFraction(StartDate, EndDate) for StartDate, EndDate in zip(schedule.StartDate, schedule.EndDate)]
        schedule["DayCountFractionActAct"] = [ql.ActualActual(ql.ActualActual.ISDA).yearFraction(StartDate, EndDate) for StartDate, EndDate in zip(schedule.StartDate, schedule.EndDate)]
        schedule["BankComitment"] = Schedule.get_commitment(input.get("facilityType"), input.get("bankComitment0"), input.get('tenor'), input.get("frequency"))
        schedule["Repayment"] = Schedule.get_repayment(schedule["BankComitment"])
        schedule["ReferenceRateSart"] = [CubicSpline(None, None).evaluate(date.serialNumber()) for date in schedule["StartDate"]]
        schedule["ReferenceRateEnd"] = [CubicSpline(None, None).evaluate(date.serialNumber()) for date in schedule["EndDate"]]
        schedule["DiscountRateStart"] = [1 / (1 + rate * dayCountFraction) for rate, dayCountFraction in zip(schedule["ReferenceRateSart"], schedule["DayCountFraction"])]
        schedule["DiscountRateEnd"] = [1 / (1 + rate * dayCountFraction) for rate, dayCountFraction in zip(schedule["ReferenceRateEnd"], schedule["DayCountFraction"])]

        
        schedule["MidDate"] = [str(date) for date in schedule["MidDate"]]
        schedule["StartDate"] = [str(date) for date in schedule["StartDate"]]
        schedule["EndDate"] = [str(date) for date in schedule["EndDate"]]
        return schedule

    @staticmethod
    def get_repayment(bank_comitment):
        p = len(bank_comitment)

        repayment = [0] * p

        for i in range(0, p):
            repayment[i] = bank_comitment[i] - bank_comitment[i+1] if i < p - 1 else bank_comitment[i]
        return repayment
        
    
    @staticmethod
    def get_commitment(facility_type, bank_comitment0, tenor: str, frequency: str):
        if tenor[1] != 'Y'or frequency[1] != 'M':
            raise ValueError("Only yearly tenor and monthly frequency is supported")
        
        tenor = int(tenor[0])
        frequency = int(frequency[0])
        
        if facility_type == 1:
            commitment = [bank_comitment0]
            rate = (frequency / (tenor * 12)) * bank_comitment0
            for _ in range(1, tenor * 12 - frequency, frequency):
                bank_comitment0 -= rate
                commitment.append(bank_comitment0)
            return commitment
        else:
            raise ValueError("Facility type not supported")