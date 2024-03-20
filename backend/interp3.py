import numpy as np
import QuantLib as ql

class Spline:
    def __init__(self, x: tuple, a: float, b: float, c: float, d:float) -> None:
        self.x = x
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.spline = self.__compute_spline(self.x[0], self.a, self.b, self.c, self.d)

    def __compute_spline(self, x: float, a: float, b: float, c: float, d: float) -> callable:
        return lambda x_i: a * (x_i - x) ** 3 + b * (x_i - x) ** 2 + c * (x_i - x) + d
    
    def check_interval(self, x_i: float) -> bool:
        if self.x[0] <= x_i and self.x[1] >= x_i:
            return True
        return False
        

class CubicSpline:
    def __init__(self, x: list, y: list) -> None:
        if x is None or y is None:
            # Gegebene Daten
            initial_date = ql.Date("2024-01-22", "%Y-%m-%d")
            period_add = ['1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '15Y', '30Y']
            swap_data = [3.113, 3.421, 2.861, 2.651, 2.535, 2.533, 2.593, 2.695, 2.467]

            # Umwandlung der Daten in passende Formate für CubicSpline
            # x = np.array([(initial_date + ql.Period(p)).serialNumber() for p in period_add])
            x = np.array([initial_date.serialNumber()])
            x = np.append(x, np.array([(initial_date + ql.Period(p)).serialNumber() for p in period_add]))
            y = np.array(swap_data)
        a, b, c, d = self.__compute_coefficients(x, y)
        self.splines = [Spline((x[i], x[i+1]), a[i], b[i], c[i], d[i]) for i in range(len(a))]


    def evaluate(self, x_i: float) -> float:
        for spline in self.splines:
            if spline.check_interval(x_i):
                return spline.spline(x_i)
        return "x_i out of range!"
    
    def __create_matrix_X(self, x: list) -> np.ndarray:
        n = len(x)
        X = np.zeros((n-2, n))
        
        for i in range(n-2):
            X[i, i] = x[i+1] - x[i]
            X[i, i+1] = 2*(x[i+2] - x[i])
            X[i, i+2] = x[i+2] - x[i+1]
        return X[:, 1:-1]

    def __create_matrix_Y(self, x: list, y: list) -> np.ndarray:
        n = len(y)
        Y = np.zeros(n-2)

        for i in range(n-2):
            Y[i] = 3 * ((y[i+2] - y[i+1]) / (x[i+2] - x[i+1]) - (y[i+1] - y[i]) / (x[i+1] - x[i]))
        return Y

    def __compute_a(self, b: list, x: list) -> np.ndarray:
        n = len(b)
        a = np.zeros(n)

        for i in range(n-1):
            a[i] = (b[i+1] - b[i]) / (3 * (x[i+1] - x[i]))
        return a

    def __compute_c(self, b:list, d: list, x: list) -> np.ndarray:
        n = len(b)
        c = np.zeros(n)

        for i in range(n-1):
            c[i] = (d[i+1] - d[i]) / (x[i+1] - x[i]) - (b[i+1] - b[i]) * (x[i+1] - x[i]) / 3 - b[i] * (x[i+1] - x[i])
        return c

    def __compute_coefficients(self, x: list, y: list) -> tuple:
        d = y
        b = np.append([0], np.linalg.solve(self.__create_matrix_X(x), self.__create_matrix_Y(x, y)))
        b = np.append(b, [0])
        a = self.__compute_a(b, x)
        c = self.__compute_c(b, d, x)

        a = a[:-1]
        b = b[:-1]
        c = c[:-1]
        d = d[:-1]

        return a, b, c, d
