from time import time
from itertools import product
from sys import argv
import pp


def compute_probability(n):
    ppservers = ()
    job_server = pp.Server(ppservers=ppservers)
    core_count = job_server.get_ncpus()

    # generate all possible vector A
    # and divide them to the cores
    visited = set()
    todo = [[] for _ in range(core_count)]
    core_index = 0
    def l(B):
        o = 0
        for v in B:
            o = 3*o + v + 1
        return o
    for B in product((-1, 0, 1), repeat=n):
        if l(B) not in visited:
            # generate all vectors, which have the same probability
            # mirrored and cycled vectors
            same_probability_set = set()
            for i in range(n):
                tmp = [B[(i+j) % n] for j in range(n)]
                same_probability_set.add(l(tmp))
                same_probability_set.add(l(tmp[::-1]))
                tmp = [-v for v in tmp]
                same_probability_set.add(l(tmp))
                same_probability_set.add(l(tmp[::-1]))
            visited.update(same_probability_set)
            todo[core_index % core_count].append((B, len(same_probability_set)))
            core_index += 1

    for t in todo:
        print(len(t))

    # start threads on each core, wait and combine results
    count = [0] * n
    jobs = [job_server.submit(core_computation, (todo_on_core, n), (), ())
            for todo_on_core in todo]
    for job in jobs:
        count2 = job()
        for i in range(1, n):
            count[i] += count2[i]

    count[0] = oeis_A081671(n)

    return count


def oeis_A081671(n):
    if n == 0:
        return 1
    a, b = 1, 4
    for i in range(2, n+1):
        a, b = b, (4*(2*i-1)*b - 12*(i-1)*a) / i
    return b


def core_computation(list_B, n):
    count = [0] * n

    # for each vector A, create all possible vectors B
##    stack = []
##    for B, cycled_count in list_B:
##        for A in itertools.product((0, 1), repeat=n):
##            for i in range(n):
##                sum_prod = 0
##                for j in range(n-i):
##                    sum_prod += A[j] * B[i+j]
##                for j in range(i):
##                    sum_prod += A[n-i+j] * B[j]
##                if sum_prod:
##                    break
##                else:
##                    count[i] += cycled_count
##    return count

    for B, cycled_count in list_B:
        t_o = sum(1 for v in B if v == 1)
        t_m = sum(1 for v in B if v == -1)
        t_o2 = t_o
        t_m2 = t_m
        ones, minones = [], []
        ones_shifted, minones_shifted = [], []
        for v in B:
            if v == 1:
                t_o -= 1
            elif v == -1:
                t_m -= 1
            ones.append(t_o)
            minones.append(t_m)
        for v in list(B[1:]) + [B[0]]:
            if v == 1:
                t_o2 -= 1
            elif v == -1:
                t_m2 -= 1
            ones_shifted.append(t_o2)
            minones_shifted.append(t_m2)

##        print(ones)
##        print(minones)
##        print(ones_shifted)
##        print(minones_shifted)

        stack = []
        stack.append(([0] * n, 0, 0, 0))

        while stack:
            A, index, sum1, sum2 = stack.pop()
            if index < n:
                # fill vector A[index] in all possible ways,
                # so that it's still possible to reach 0.
                for v in (0, 1):
                    sum1_new = sum1 + v * B[index]
                    sum2_new = sum2 + v * B[index + 1 if index +1 < n else 0]
                    if sum1_new - minones[index] <= 0 <= sum1_new + ones[index] and \
                        sum2_new - minones_shifted[index] <= 0 <= sum2_new + ones_shifted[index]:
                            C = A[:]
                            C[index] = v
                            stack.append((C, index + 1, sum1_new, sum2_new))
            else:
                # B is complete, calculate the sums
                count[1] += cycled_count  # we know that the sum = 0 for i = 1
                for i in range(2, n):
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
    n = int(argv[1]) if len(argv) > 1 else 5

    #core_computation([((1, -1, 0, -1, 1), 1)], n)
    #exit()

    start_time = time()
    count = compute_probability(n)
    end_time = time()
    duration = int(round(end_time - start_time))

    print("Calculation for n = {} took {}:{:02d} minutes\n"
          .format(n, duration // 60, duration % 60))

    l = lambda x: str(len(str(x)))
    for i in range(n):
        print("{0:{1}d}  {2:{3}d} / {4}  {5:6.2%}"
              .format(i+1, l(n), count[i], l(count[0]),
                      6**n, float(count[i])/6**n))
