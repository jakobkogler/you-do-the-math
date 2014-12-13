import itertools
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

    count = [0]*n
    set_A = set()
    d = [dict() for i in range(core_count)]

    tmp = 0
    for A in itertools.product((0,1), repeat=n):
        if A not in set_A:
            cycled_set = set_cycled_tuple(A, n)
            cycled_count = len(cycled_set)
            set_A.update(cycled_set)
            d[tmp%core_count][A] = cycled_count
            tmp += 1

    count = [0] * n
    jobs = [job_server.submit(core_computation,(d1,n), (), ("itertools",)) for d1 in d]
    for job in jobs:
        count2 = job()
        for i in range(n):
            count[i] += count2[i]

    for i in range(n):
        print("{:2d}  {:10d} / {:10d} {:6.2%}".format(i+1, count[i], 6**n, float(count[i])/6**n))

def core_computation(dict_A, n):
    count = [0] * n

    stack = []
    for A, cycled_count in dict_A.iteritems():
        ones = [sum(A[i:]) for i in range(n)]
        stack.append(([0] * n, 0, 0))

        while stack:
            l2, t, sum_bisher = stack.pop()
            if t < n:
                if A[t] == 0:
                    for v in(-1, 0, 1):
                        l3 = l2[:]
                        l3[t] = v
                        stack.append((l3, t+1, sum_bisher))
                else:
                    if ones[t]-1 > -sum_bisher:
                        l3 = l2[:]
                        l3[t] = -1
                        stack.append((l3, t+1, sum_bisher-1))
                    if abs(sum_bisher) <= ones[t] - 1:
                        l3 = l2[:]
                        l3[t] = 0
                        stack.append((l3, t+1, sum_bisher))
                    if sum_bisher < ones[t]-1:
                        l3 = l2[:]
                        l3[t] = 1
                        stack.append((l3, t+1, sum_bisher+1))
            else:
                for i in range(n):
                    sum_prod = 0
                    for j in range(n-i):
                        sum_prod += A[j] * l2[i+j]
                    for j in range(i):
                        sum_prod += A[n-i+j] * l2[j]
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
