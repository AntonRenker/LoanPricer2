import unittest
import numpy as np
from scipy.interpolate import CubicSpline as CubicSplineScipy
import QuantLib as ql
import sys
import os
# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
from backend import CubicSpline

class TestCubicSpline(unittest.TestCase):
    def setUp(self):
        # Gegebene Daten
        initial_date = ql.Date("2024-01-22", "%Y-%m-%d")
        period_add = ['1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '15Y', '30Y']
        swap_data = [3.113, 3.421, 2.861, 2.651, 2.535, 2.533, 2.593, 2.695, 2.467]

        # Umwandlung der Daten in passende Formate für CubicSpline
        self.x = np.array([initial_date.serialNumber()])
        self.x = np.append(self.x, np.array([(initial_date + ql.Period(p)).serialNumber() for p in period_add]))
        self.y = np.array(swap_data)

        # Initialisiere die CubicSpline-Objekte für die beiden Implementierungen
        self.cs_own = CubicSpline(self.x, self.y)
        self.cs_scipy = CubicSplineScipy(self.x, self.y)

    def test_interpolation(self):
        # Wert für die Interpolation
        x_i = ql.Date("2029-06-22", "%Y-%m-%d").serialNumber()
        x_i = ql.Date("2025-01-22", "%Y-%m-%d").serialNumber() # March 16th, 2024

        # Interpolation mit der eigenen Implementierung
        y_i_own = self.cs_own.evaluate(x_i)

        # Interpolation mit SciPy CubicSpline
        y_i_scipy = self.cs_scipy(x_i)

        # Überprüfe, ob die Ergebnisse übereinstimmen
        self.assertAlmostEqual(y_i_own, y_i_scipy, places=2)

if __name__ == '__main__':
    unittest.main()
