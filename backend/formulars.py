import numpy as np
from scipy.stats import norm

class ImpliedIZV:
    def __init__(self, bank_commitment: np.ndarray, repayment: np.ndarray, discount_at_end: np.ndarray, day_count_fraction: np.ndarray) -> None:
        # check data types
        if not all(type(arr) == type(bank_commitment) for arr in [repayment, discount_at_end, day_count_fraction]):
            raise ValueError("Input arrays must have the same data np.ndarray")
        
        # check input for consistency
        if not all(arr.shape == bank_commitment.shape for arr in [repayment, discount_at_end, day_count_fraction]):
            raise ValueError("Input arrays must have the same shape")
        
        self.bank_commitment = bank_commitment
        self.repayment = repayment
        self.discount_at_end = discount_at_end
        self.day_count_fraction = day_count_fraction
        self.implied_izv = self.__calculate_implied_izv()
    
    def __calculate_implied_izv(self) -> float:
        numerater = -self.bank_commitment[0] + np.sum(self.repayment * self.discount_at_end)
        denominator = np.sum(self.bank_commitment * self.day_count_fraction * self.discount_at_end)
        return numerater / denominator

class Pricing:
    def __init__(self, bank_commitment: np.ndarray, survival_probability: np.ndarray, df_end: np.ndarray, expected_usage: np.ndarray, 
                 costumer_margin: float, izv: float, commitment_fee: float, fls: np.ndarray, lgd: np.ndarray, fdp: np.ndarray, 
                 day_count_fraction: np.ndarray, disount_factor: np.ndarray, rwa: np.ndarray, cap_ratio: float, cap_return: float, 
                 op_risk_weight: float, cost_income_ratio: float) -> None:
        self.bank_commitment = bank_commitment
        self.survival_probability = survival_probability
        self.df_end = df_end
        self.expected_usage = expected_usage
        self.costumer_margin = costumer_margin
        self.izv = izv
        self.commitment_fee = commitment_fee
        self.fls = fls
        self.lgd = lgd
        self.fdp = fdp
        self.day_count_fraction = day_count_fraction
        self.discount_factor = disount_factor
        self.rwa = rwa
        self.cap_ratio = cap_ratio
        self.cap_return = cap_return
        self.op_risk_weight = op_risk_weight
        self.cost_income_ratio = cost_income_ratio
        self.sdf = self.__calculate_sdf()
        self.lad = self.__calculate_lad()
        
        # Operational Sales Revenue (OSR)
        self.gross_profit = self.__calculate_gross_profit()
        self.funding_cost = self.__calculate_funding_cost()
        self.heding_cost = 0 # TBD
        self.operational_sales_revenue = np.sum(self.gross_profit + self.funding_cost + self.heding_cost) # Does not make sense since prfit and funding is a list and not a number
        
        # Risk Price
        self.standard_risk_cost = self.__calcualte_standard_risk_cost()
        self.capital_cost = self.__calculate_capital_cost()
        self.operational_risk_cost = self.__calculate_operational_risk_cost()
        self.risk_price = np.sum(self.standard_risk_cost + self.capital_cost + self.operational_risk_cost)

        # Economic Profit
        self.product_cost = self.__calculate_product_cost() 
        self.sales_steering = 0 # TBD
        self.ecomomic_profit = np.sum(self.operational_sales_revenue + self.risk_price + self.product_cost + self.sales_steering)

    def __calculate_product_cost(self) -> np.ndarray:
        N = len(self.bank_commitment)
        product_cost = np.zeros(N)
        for i in range(N):
            product_cost[i] = -self.gross_profit[i] * self.cost_income_ratio
    def __calculate_lad(self) -> np.ndarray:
        N = len(self.bank_commitment)
        lad = np.zeros(N)
        for i in range(N):
            lad[i] = self.bank_commitment[i] * self.lgd[i]
        return lad

    def __calculate_operational_risk_cost(self) -> float:
        N = len(self.bank_commitment)
        operational_risk_cost = np.zeros(N)
        for i in range(N):
            operational_risk_cost[i] = -self.gross_profit[i] * self.op_risk_weight * self.cap_return
        return operational_risk_cost

    def __calcualte_standard_risk_cost(self) -> float:
        N = len(self.bank_commitment)
        standard_risk_cost = np.zeros(N)
        for i in range(N):
            standard_risk_cost[i] = -self.lad[i] * self.fdp[i] * self. sdf[i]
        return standard_risk_cost

    def __calculate_capital_cost(self) -> float:
        N = len(self.bank_commitment)
        capital_cost = np.zeros(N)
        for i in range(N):
            capital_cost[i] = -self.day_count_fraction[i] * self.discount_factor[i] * self.survival_probability[i] * self.rwa[i] * self.cap_ratio * self.cap_return
        return capital_cost

    def __calculate_sdf(self) -> float:
        N = len(self.bank_commitment)
        sdf = np.zeros(N)
        for i in range(N):
            sdf[i] = self.day_count_fraction[i] * self.survival_probability[i] * self.df_end[i]
        return sdf
    
    def __calculate_funding_cost(self) -> float:
        N = len(self.bank_commitment)
        funding_cost = np.zeros(N)
        for i in range(N):
            funding_cost[i] = - self.bank_commitment[i] * self.fls[i] * self.sdf[i]
        return funding_cost

    def __calculate_gross_profit(self) -> float:
        N = len(self.bank_commitment)
        gross_profit = np.zeros(N)
        for i in range(N):
            gross_profit[i] = self.bank_commitment[i] * (self.expected_usage[i] * (self.costumer_margin - self.izv) + (1 - self.expected_usage[i]) * self.commitment_fee) * self.sdf[i]
        return gross_profit
    

class RiskWeightedAssets:
    def __init__(self, exposure_at_default: np.ndarray, pd: np.ndarray, lgd: np.ndarray, maturity_factor: np.ndarray, risk_weighted_asset_relief: np.ndarray, small_and_medium_enterprises: bool) -> None:
        self.exposure_at_default = exposure_at_default
        self.risk_weighted_asset_relief = risk_weighted_asset_relief
        self.lgd = lgd
        self.pf = pd
        self.small_and_medium_enterprises = small_and_medium_enterprises
        self.r = self.__calculate_r()
        self.matrurity_factor = self.__calculate_maturity_factor
        self.core = self.__calculate_core()
        self.risk_weight = self.core * maturity_factor
        self.risk_weighted_assets = exposure_at_default * self.risk_weight * risk_weighted_asset_relief


    def __calculate_core(self) -> float:
        M = 1 # TBD
        phi_inv_pd = norm.ppf(self.pd)
        phi_inv_999 = norm.ppf(0.999)       
        core = (self.lgd * norm.cdf(1/np.sqrt(1-self.r) * phi_inv_pd + np.sqrt(self.r / (1-self.r)) * phi_inv_999) - self.lgd * self.pd) * 12.5 * 1.06
        return core

    def __calculate_maturity_factor(self) -> float:
        b = (0.11852 - 0.05478 * np.log(self.pd))**2
        M = 1 # TBD
        mf = (1 + (max(1 , min(5, M)) -2.5) * b) / (1 - 1.5 * b) 
    
    def __calculate_r(self) -> float:
        turnover = 1
        e_pd = 1 - np.exp(-50 * self.pd)
        e_50 = 1 - np.exp(-50)
        r = 0.12 * (e_pd / e_50) + 0.24 * (1 - e_pd / e_50)
        if self.small_and_medium_enterprises:
            r += -0.04 * (1- (min(50, max(5, turnover * 1_000_000)) - 5)/ 45)