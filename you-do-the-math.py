from itertools import product
from sys import argv
from fractions import Fraction

def compute_probability(n):
    c = [0]*n
    for A in product((0,1), repeat=n):
        for B in product((-1,0,1), repeat=n):
            for i in range(n):
                sum_prod = 0
                for j in range(n):
                    sum_prod += A[j] * B[(i+j)%n]
                if sum_prod:
                    break
                else:
                    c[i] += 1

    for i in range(n):
        print("{:2d}: {:6.2%}, {}".format(i+1, c[i]/6**n, Fraction(c[i], 6**n)))

if __name__ == "__main__":
    if len(argv) > 1:
        compute_probability(int(argv[1]))