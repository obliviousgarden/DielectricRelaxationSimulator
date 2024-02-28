from decimal import Decimal
import numpy as np


class DecimalComplex:
    def __init__(self, real, imag=Decimal("0")):
        if isinstance(real,(str,int,float)):
            self.real = Decimal(str(real))
        else:
            # 可能是Decimal或者ndarray[Decimal]
            self.real = real
        if isinstance(imag,(str,int,float)):
            self.imag = Decimal(str(imag))
        else:
            self.imag = imag

    def __str__(self):
        return f"{self.real}+{self.imag}j"

    def __add__(self, other):
        if isinstance(other, DecimalComplex):
            return DecimalComplex(self.real + other.real, self.imag + other.imag)
        else:
            raise TypeError("Unsupported operand type")

    def __sub__(self, other):
        if isinstance(other, DecimalComplex):
            return DecimalComplex(self.real - other.real, self.imag - other.imag)
        else:
            raise TypeError("Unsupported operand type")

    def __mul__(self, other):
        if isinstance(other, DecimalComplex):
            real_part = self.real * other.real - self.imag * other.imag
            imag_part = self.real * other.imag + self.imag * other.real
            return DecimalComplex(real_part, imag_part)
        else:
            raise TypeError("Unsupported operand type")

    def __truediv__(self, other):
        if isinstance(other, DecimalComplex):
            denominator = other.real**2 + other.imag**2
            real_part = (self.real * other.real + self.imag * other.imag) / denominator
            imag_part = (self.imag * other.real - self.real * other.imag) / denominator
            return DecimalComplex(real_part, imag_part)
        else:
            raise TypeError("Unsupported operand type")

    def __pow__(self, n):
        if isinstance(n, Decimal):
            numerator, denominator = n.as_integer_ratio()
            if denominator == 1: # 分母是1那么是int
                n = int(n)
            else:   #否则是float
                n = float(n)
        if isinstance(n, (int, float)):
            # 注意：当前实例有可能是ndarray[Decimal]的情况
            if isinstance(self.real,np.ndarray) or isinstance(self.imag,np.ndarray):
                real_rst = []
                imag_rst = []
                if isinstance(self.real,np.ndarray) and not isinstance(self.imag,np.ndarray):
                    for index in range(len(self.real)):
                        complex_number = np.complex128(complex(f"{self.real[index]}+{self.imag}j"))
                        result = np.power(complex_number, n)
                        real_rst.append(Decimal(result.real))
                        imag_rst.append(Decimal(result.imag))
                elif not isinstance(self.real,np.ndarray) and isinstance(self.imag,np.ndarray):
                    for index in range(len(self.imag)):
                        complex_number = np.complex128(complex(f"{self.real}+{self.imag[index]}j"))
                        result = np.power(complex_number, n)
                        real_rst.append(Decimal(result.real))
                        imag_rst.append(Decimal(result.imag))
                else:
                    for index in range(len(self.real)):
                        complex_number = np.complex128(complex(f"{self.real[index]}+{self.imag[index]}j"))
                        result = np.power(complex_number, n)
                        real_rst.append(Decimal(result.real))
                        imag_rst.append(Decimal(result.imag))
                real_rst = np.array(real_rst)
                imag_rst = np.array(imag_rst)
            else:
                complex_number = np.complex128(complex(f"{self.real}+{self.imag}j"))
                result = np.power(complex_number, n)
                real_rst = Decimal(result.real)
                imag_rst = Decimal(result.imag)
            return DecimalComplex(real_rst, imag_rst)
        else:
            raise TypeError("Unsupported operand type")


if __name__ == "__main__":
    a = DecimalComplex(1.3,0.8)
    b = DecimalComplex(-3.2,-1.7)
    print(a+b)
    print(a-b)
    print(a*b)
    print(a/b)
    print(a**0.8)