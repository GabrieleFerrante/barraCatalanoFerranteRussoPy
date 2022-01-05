from math import sqrt, pow

from retta import Retta


class Parabola:
    def __init__(self, tipo="PARAMETRI", *params):
        if tipo == "PARAMETRI":
            self.__a = params[0]
            self.__b = params[1]
            self.__c = params[2]
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
        for x in range(min(n, m), max(n, m) + 1, step):
            output.append((x, self.trovaY(x)))
        return output

    def intersezione(self, retta):  # WIP; Le formule dovrebbero essere corrette, ma i risultati non lo sono
        if type(retta) != Retta:
            raise Exception("L'input non è una retta")
        d = pow(self.__b - retta.m, 2) - (4 * self.__a * (self.__c - retta.q))
        # return d

        if d == 0:
            x = (-self.__b + sqrt(d)) / (2 * self.__a)
            y = self.trovaY(x)
            return x, y
        elif d > 0:
            x1 = (-self.__b + sqrt(d)) / (2 * self.__a)
            x2 = (-self.__b - sqrt(d)) / (2 * self.__a)
            y1 = self.trovaY(x1)
            y2 = self.trovaY(x2)
            return (x1, y1), (x2, y2)
        elif d < 0:
            return None



if __name__ == '__main__':

    parabola = Parabola("PARAMETRI", 2, 0, 1)
    retta = Retta("PARAMETRI", -1, 1, -2)
    
    parabola2 = Parabola("PARAMETRI",1,0,0)
    retta2 = Retta("PARAMETRI", 0,1,-10)
    
    print(retta.m, retta.q)
    print(parabola.intersezione(retta))

    print(retta2.m, retta2.q)
    print(parabola2.intersezione(retta2))
