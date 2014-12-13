from itertools import product
from sys import argv
import pp

def set_cycled_tuple(t, n):
    s = set()
    for i in range(n):
        s.add(tuple(t[(i+j)%n] for j in range(n)))
    return s

def compute_probability(n):
    ppservers = ()
    job_server = pp.Server(ppservers=ppservers)
    core_count = job_server.get_ncpus()

    # generate and divide all possible vector A (modulo cycled vectors)
    set_A = set()
    d = [dict() for i in range(core_count)]
    tmp = 0
    for A in product((0,1), repeat=n):
        if A not in set_A:
            cycled_set = set_cycled_tuple(A, n)
            cycled_count = len(cycled_set)
            set_A.update(cycled_set)
            d[tmp%core_count][A] = cycled_count
            tmp += 1

    # start threads on each core, wait and combine results
    count = [0] * n
    jobs = [job_server.submit(core_computation,(d1,n), (), ()) for d1 in d]
    for job in jobs:
        count2 = job()
        for i in range(n):
            count[i] += count2[i]

    for i in range(n):
        print("{:2d}  {:10d} / {:10d} {:6.2%}".format(i+1, count[i], 6**n, float(count[i])/6**n))

def core_computation(dict_A, n):
    count = [0] * n

    stack = []
    # for each vector A, create all possible vectors B
    for A, cycled_count in dict_A.iteritems():
        ones = [sum(A[i:]) for i in range(n)]
        stack.append(([0] * n, 0, 0))

        while stack:
            B, index, sum1 = stack.pop()
            if index < n:
                # fill vector B[index] in all possible ways,
                # so that it's still possible to reach 0.
                if A[index] == 0:
                    for v in(-1, 0, 1):
                        C = B[:]
                        C[index] = v
                        stack.append((C, index + 1, sum1))
                else:
                    if ones[index]-1 > -sum1:
                        C = B[:]
                        C[index] = -1
                        stack.append((C, index + 1, sum1 - 1))
                    if abs(sum1) <= ones[index] - 1:
                        # already zero
                        stack.append((B, index + 1, sum1))
                    if sum1 < ones[index]-1:
                        C = B[:]
                        C[index] = 1
                        stack.append((C, index + 1, sum1 + 1))
            else:
                # B is complete, calculate the sums
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
    return count

if __name__ == "__main__":
    if len(argv) > 1:
        compute_probability(int(argv[1]))
    else:
        compute_probability(10)
