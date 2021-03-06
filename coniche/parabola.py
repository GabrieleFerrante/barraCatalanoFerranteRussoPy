import numpy as np
from coniche.retta import Retta


class Parabola:
    def __init__(self, tipo=0, *params):
        '''
        Il tipo è 0 per costruire la parabola con a, b, c; 1 per costruire la parabola con tre punti per la quale passa
        '''
        if tipo == 0:
            self.__a = params[0]
            self.__b = params[1]
            self.__c = params[2]
            self.__delta = self.__b ** 2 - (4 * self.__a * self.__c)
        elif tipo == 1:
            matrix_a = np.array([
                [params[0][0]**2, params[0][0], 1],
                [params[1][0]**2, params[1][0], 1],
                [params[2][0]**2, params[2][0], 1]
            ])
            matrix_b = np.array([params[0][1], params[1][1], params[2][1]])
            matrix_c = np.linalg.solve(matrix_a, matrix_b)

            self.__a = matrix_c[0]
            self.__b = matrix_c[1]
            self.__c = matrix_c[2]
            self.__delta = self.__b ** 2 - (4 * self.__a * self.__c)


        else:
            raise Exception("Il tipo specificato non è un'opzione")

    # PROPRIETA' DELLA PARABOLA
    @property
    def a(self):
        return self.__a

    @property
    def b(self):
        return self.__b

    @property
    def c(self):
        return self.__c

    @property
    def vertice(self):
        x = -(self.__b / (2 * self.__a))
        y = -(self.__delta / (4 * self.__a))
        return x, y

    @property
    def asse(self):
        return Retta(0, 1, -self.__b / (2 * self.__a))

    @property
    def fuoco(self):
        x = -(self.__b / (2 * self.__a))
        y = (1 - self.__delta) / (4 * self.__a)
        return x, y

    @property
    def direttrice(self):
        return -((1 + self.__delta) / (4 * self.__a))

    def trovaY(self, x):
        y = self.__a * x ** 2 + self.__b * x + self.__c
        return y

    def punti(self, n, m, step=1):
        output = []
        for x in range(int(min(n, m)), int(max(n, m)) + 1, step):
            output.append((x, self.trovaY(x)))
        return output

    def equazione(self):
        a = f'{round(self.__a, 2)}x^2' if round(self.__a, 2) != 0 else ''
        a = f'{a}' if self.__a != 1 else 'x^2'
        if a == 'x^2' and self.__a < 0:
            a = f'-{a}'
        
        b = f'+{round(self.__b, 2)}x' if self.__b != 1 else 'x'
        if self.__b < 0:
            if b == 'x':
                b = f'-{b}'
            else:
                b = b.replace('+', '')
        b = f'{b}' if round(self.__b, 2) != 0 else ''
        
        c = f'+{round(self.__c, 2)}' if self.__c != 0 else ''
        if self.__c < 0:
            c = c.replace('+', '')
        
        return f'y={a}{b}{c}'

    def intersezione_retta(self, retta):  # WIP; Le formule dovrebbero essere corrette, ma i risultati non lo sono
        if type(retta) != Retta:
            raise Exception("L'input non è una retta")
        matrix_a = np.array([[self.__a, self.__b], [retta.a, retta.b]])
        matrix_b = np.array([self.__c, retta.c])
        matrix_c = np.linalg.solve(matrix_a, matrix_b)
        return matrix_c[0], matrix_c[1]


if __name__ == '__main__':

    parabola = Parabola(0, 4, 2,-3)

    print(parabola.a, parabola.b, parabola.c)
    print(parabola.equazione())
