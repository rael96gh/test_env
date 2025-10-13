"""
Constantes para cálculos de secuencias de DNA
"""

# Parámetros termodinámicos para nearest-neighbor
H_NN = {
    'AA': -7.9, 'AT': -7.2, 'TA': -7.2, 'CA': -8.5, 'GT': -8.4,
    'CT': -7.8, 'GA': -8.2, 'CG': -10.6, 'GC': -9.8, 'GG': -8.0,
    'TT': -7.9, 'TG': -8.2, 'TC': -7.8, 'AG': -8.4, 'AC': -8.5
}

S_NN = {
    'AA': -22.2, 'AT': -20.4, 'TA': -21.3, 'CA': -22.7, 'GT': -22.4,
    'CT': -21.0, 'GA': -22.2, 'CG': -27.2, 'GC': -24.4, 'GG': -19.9,
    'TT': -22.2, 'TG': -22.2, 'TC': -21.0, 'AG': -22.4, 'AC': -22.7
}

H_INIT = {'A': 2.3, 'T': 2.3, 'G': 0.1, 'C': 0.1}
S_INIT = {'A': 4.1, 'T': 4.1, 'G': -2.8, 'C': -2.8}

# Constante de gas en cal/(mol·K)
R = 1.987

# Penalización de loop simplificada en kcal/mol
H_LOOP = 5.6