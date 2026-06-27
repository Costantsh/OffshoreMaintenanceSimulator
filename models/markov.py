"""

Modelo de degradação baseado em Cadeias de Markov.

Estados:

0 -> Operational
1 -> Warning
2 -> Critical
3 -> Failure
4 -> Maintenance

Objetivo:

Simular a degradação progressiva
e eventual recuperação dos ativos.
"""

import numpy as np


TRANSITION_MATRIX = np.array([

    # Operational
    [0.85, 0.15, 0.00, 0.00, 0.00],

    # Warning
    [0.10, 0.70, 0.20, 0.00, 0.00],

    # Critical
    [0.00, 0.15, 0.55, 0.30, 0.00],

    # Failure
    [0.00, 0.00, 0.00, 0.05, 0.95],

    # Maintenance
    [0.75, 0.20, 0.00, 0.00, 0.05]

])


STATE_NAMES = {

    0: "Operational",

    1: "Warning",

    2: "Critical",

    3: "Failure",

    4: "Maintenance"

}


class MarkovEngine:

    @staticmethod
    def next_state(current_state):

        """
        Calcula o próximo estado
        utilizando a matriz de transição.
        """

        return np.random.choice(

            [0, 1, 2, 3, 4],

            p=TRANSITION_MATRIX[current_state]

        )

    @staticmethod
    def get_state_name(state):

        return STATE_NAMES.get(

            state,

            "Unknown"

        )