from itertools import product
from sys import argv
import pp


def set_cycled_tuple(t, n):
    s = set()
    for i in range(n):
        s.add(tuple(t[(i+j)%n] for j in range(n)))
    return s


def cycle(A, n):
    mask = (1 << (2*n - 2)) - 1
    return ((A & mask) << 2) | (A >> (2*n - 2))


def compute_probability(n):
    ppservers = ()
    job_server = pp.Server(ppservers=ppservers)
    core_count = job_server.get_ncpus()


    # generate all vectors A
    list_A = [0b00, 0b11]
    for i in range(n-1):
        list_A2 = []
        for A in list_A:
            list_A2.append((A << 2) | 0b00)
            list_A2.append((A << 2) | 0b11)
        list_A = list_A2

    # generate and divide all possible vector A (modulo cycled vectors)
    todo = [list() for _ in range(core_count)]
    tmp = 0
    set_A = set()
    for A in list_A:
        if A not in set_A:
            double_set = set()
            for i in range(n):
                A = cycle(A, n)
                double_set.add(A)
            set_A.update(double_set)
            todo[tmp%core_count].append((A, len(double_set)))
            tmp += 1

    # start threads on each core, wait and combine results
    count = [0] * n
    jobs = [job_server.submit(core_computation,(todo_core,n), (sum_AB,), ()) for todo_core in todo]
    for job in jobs:
        count2 = job()
        for i in range(1, n):
            count[i] += count2[i]
    count[0] = oeis_A081671(n)

    for i in range(n):
        print("{:2d}  {:10d} / {:10d} {:6.2%}".format(i+1, count[i], 6**n, float(count[i])/6**n))


def oeis_A081671(n):
    if n == 0:
        return 1
    a, b = 1, 4
    for i in range(2, n+1):
        a, b = b, (4*(2*i-1)*b - 12*(i-1)*a) / i
    return b


def sum_AB(S):
    result = 0
    while S:
        t = S & 0b11
        if t == 0b01:
            result += 1
        elif t == 0b10:
            result -= 1
        S >>= 2
    return result


def core_computation(todo, n):
    count = [0] * n
    cycle_mask = (1 << (2*n - 2)) - 1

    # create look-up table for sum calculations
    lookup = dict()
    lookup[0] = 0
    for i in range(n):
        for k, v in list(lookup.iteritems()):
            lookup[(k << 2) | 0b01] = v + 1
            lookup[(k << 2) | 0b00] = v
            lookup[(k << 2) | 0b10] = v - 1


    # create minus and plus 1 masks
    plus_mask, minus_mask = [0b00], [0b00]
    for i in range(n):
        minus_mask.append((minus_mask[-1] << 2) | 0b10)
        plus_mask.append((plus_mask[-1] << 2) | 0b01)

    stack = []
    # for each vector A, create all possible vectors B
    for A, cycled_count in todo:
        stack.append((0, 0)) # empty vector, 0 entries filled

        while stack:
            B, index = stack.pop()
            if index < n:
                tmp = (B << (2*(n-index)))
                min_B = tmp | minus_mask[n - index]
                max_B = tmp | plus_mask[n - index]

                #if lookup[A & min_B] <= 0 <= lookup[A & max_B]:
                if sum_AB(A & min_B) <= 0 <= sum_AB(A & max_B):
                    min_B = ((min_B & cycle_mask) << 2) | (min_B >> (2*n - 2))
                    max_B = ((max_B & cycle_mask) << 2) | (max_B >> (2*n - 2))
                    #if lookup[A & min_B] <= 0 <= lookup[A & max_B]:
                    if sum_AB(A & min_B) <= 0 <= sum_AB(A & max_B):
                        tmp = B << 2
                        stack.append((tmp | 0b00, index + 1))
                        stack.append((tmp | 0b01, index + 1))
                        stack.append((tmp | 0b10, index + 1))
            else:
                # B is complete, calculate the sums
                for i in range(0, n):
                    #if lookup[A & B] == 0:
                    if sum_AB(A & B) == 0:
                        count[i] += cycled_count
                        B = ((B & cycle_mask) << 2) | (B >> (2*n - 2))
                    else:
                        break
    return count


if __name__ == "__main__":
    if len(argv) > 1:
        compute_probability(int(argv[1]))
    else:
        compute_probability(11)
