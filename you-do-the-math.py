from itertools import product
from sys import argv

def set_cycled_tuple(t, n):
    s = set()
    for i in range(n):
        s.add(tuple(t[(i+j)%n] for j in range(n)))
    return s

def compute_probability(n):
    count = [0]*n
    set_A = set()
    for A in product((0,1), repeat=n):
        if A not in set_A:
            cycled_set = set_cycled_tuple(A, n)
            cycled_count = len(cycled_set)
            set_A.update(cycled_set)

            for B in product((-1,0,1), repeat=n):
                for i in range(n):
                    sum_prod = 0
                    for j in range(n-i):
                        sum_prod += A[j] * B[i+j]
                    for j in range(i):
                        sum_prod += A[n-i+j] * B[j]
                    if sum_prod:
                        break
                    else:
                        count[i] += cycled_count

    for i in range(n):
        print("{:2d}  {:9d} / {:10d} {:6.2%}".format(i+1, count[i], 6**n, count[i]/6**n))

if __name__ == "__main__":
    if len(argv) > 1:
        compute_probability(int(argv[1]))
