class Retta:
    def __init__(self, tipo="PARAMETRI", *args):
        """
        Il tipo è PARAMETRI per a, b, c; COEFFICIENTE per m e un punto; PUNTI per due punti
        """
        if tipo == "PARAMETRI":
            self.__a = args[0]
            self.__b = args[1]
            self.__c = args[2]
        elif tipo == "COEFFICIENTE":
            self.__m = args[0]
            self.__punto = args[1]

            self.__a = -self.__m
            self.__b = 1
            self.__c = self.__m * self.__punto[0] - self.__punto[1]
        elif tipo == "PUNTI":
            self.__punto1 = args[0]
            self.__punto2 = args[1]
            self.__m = (self.__punto2[1] - self.__punto1[1]) / (self.__punto2[0] - self.__punto1[0])
            self.__a = -self.__m
            self.__b = 1
            self.__c = -self.__punto1[0] + self.__punto1[1]
        else:
            raise Exception("Il tipo specificato non è un'opzione")

    # PROPRIETA' DELLA RETTA
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
    def m(self):
        """
        :returns: il coefficiente angolare
        """
        try:
            return self.__m
        except AttributeError:
            if self.__b != 0:
                return -self.__a / self.__b
            else:  # Se b = 0, dai un errore
                raise ZeroDivisionError

    @property
    def q(self):
        """
        :returns: l'intercetta
        """
        if self.__b != 0:
            return -self.__c / self.__b
        else:  # Se b = 0, dai un errore
            raise ZeroDivisionError

    def eqImplicita(self):
        """
        :returns: la stringa dell'equazione implicita
        """
        # PRIMO TERMINE
        incognita_1 = f"{self.__a}x" if self.__a != 0 else ""
        incognita_1 = f"x" if self.__a == 1 else incognita_1
        incognita_1 = f"-x" if self.__a == -1 else incognita_1
        incognita_1 = incognita_1 if self.__a <= 0 else f"+{incognita_1}"

        # SECONDO TERMINE
        incognita_2 = f"{self.__b}y" if self.__b != 0 else ""
        incognita_2 = f"y" if self.__b == 1 else incognita_2
        incognita_2 = f"-y" if self.__b == -1 else incognita_2
        incognita_2 = incognita_2 if self.__b <= 0 else f"+{incognita_2}"

        # TERMINE NOTO
        noto = f"{self.__c}" if self.__c != 0 else ""
        noto = noto if self.__c <= 0 else f"+{noto}"

        return f"{incognita_1}{incognita_2}{noto}=0"

    # FUNZIONI DELLA RETTA
    def eqEsplicita(self):
        """
        :returns: la stringa dell'equazione esplicita
        """
        if self.__b == 0:
            ind = ""
        else:
            b = self.__b if self.__b >= 0 else -self.__b

            # VARIABILE INDIPENDENTE
            a = self.__a if self.__b >= 0 else -self.__a

            ind = f"{a}/{b}x" if abs(self.__b) != 1 else f"{a}x"
            ind = ind if abs(a/b) != 1 else f"x"
            ind = ind if a <= 0 else f"+{ind}"
            ind = ind if a != 0 else ""

        # TERMINE NOTO
        c = self.__c if self.__b >= 0 else -self.__c

        noto = f"{c}/{b}" if abs(self.__b) != 1 else f"{c}"
        noto = noto if c <= 0 else f"+{noto}"
        noto = noto if c != 0 else ""

        return f"y={ind}{noto}"

    def trovaY(self, x):
        """
        :returns: la stringa dell'equazione esplicita
        """
        return round(self.__a / self.__b * x + self.__c / self.__b, 2)

    def punti(self, n, m, step=1):
        """
        :returns: la stringa dell'equazione esplicita
        """
        return [(i, self.trovaY(i)) for i in range(min(n, m), max(n, m) + 1, step)]

    def intersezione(self, retta1):
        if type(retta1) != Retta:
            raise Exception("Per calcolare l'intersezione serve un altra retta")

        if retta1.b == 0:
            raise ZeroDivisionError

        if -self.__a / self.__b == -retta1.a / retta1.b and -self.__c / self.__b != -retta1.c / retta1.b:
            return None

        if -self.__a / self.__b == -retta1.a / retta1.b and -self.__c / self.__b == -retta1.c / retta1.b:
            return self

        x = ((self.__c / self.__b) - (retta1.c / retta1.b)) / ((-self.__a / self.__b) + (retta1.a / retta1.b))
        y = (-self.__a / self.__b) * x + (-self.__c / self.__b)
        return round(x, 2), round(y, 2)


def main():
    tipo = input("Scegli il tipo di retta tra PARAMETRI, COEFFICIENTE, PUNTI: ").upper()
    if tipo == "PARAMETRI":
        a, b, c = input("Inserisci a, b e c separati da spazi: ").split()
        a, b, c = float(a), float(b), float(c)
        retta = Retta(tipo, a, b, c)
        print(retta.m)
    elif tipo == "COEFFICIENTE":
        m = float(input("Inserisci m: "))
        x, y = float(input("Inserisci x: ")), float(input("Inserisci y: "))
        retta = Retta(tipo, m, (x, y))
        print(retta.eqEsplicita())
    elif tipo == "PUNTI":
        x1, y1 = float(input("Inserisci x1: ")), float(input("Inserisci y1: "))
        x2, y2 = float(input("Inserisci x2: ")), float(input("Inserisci y2: "))
        retta = Retta(tipo, (x1, y1), (x2, y2))
        print(retta.m)
        print(retta.eqEsplicita())
    else:
        raise Exception("Il tipo specificato non è valido")


if __name__ == '__main__':
    main()
