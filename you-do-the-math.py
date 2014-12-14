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
    todo = [dict() for _ in range(core_count)]
    core_index = 0
    for A in product((0,1), repeat=n):
        if A not in visited:
            # generate all vectors, which have the same probability
            # mirrored and cycled vectors
            same_probability_set = set()
            for i in range(n):
                tmp = [A[(i+j)%n] for j in range(n)]
                same_probability_set.add(tuple(tmp))
                same_probability_set.add(tuple(tmp[::-1]))
            visited.update(same_probability_set)
            todo[core_index%core_count][A] = len(same_probability_set)
            core_index += 1

    # start threads on each core, wait and combine results
    count = [0] * n
    jobs = [job_server.submit(core_computation,(todo_on_core,n), (), ()) \
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


def core_computation(dict_A, n):
    count = [0] * n

    # for each vector A, create all possible vectors B
    stack = []
    for A, cycled_count in dict_A.iteritems():
        ones = [sum(A[i:]) for i in range(n)] + [0]
        # + [0], so that later ones[n] doesn't throw a exception
        stack.append(([0] * n, 0, 0, 0))

        while stack:
            B, index, sum1, sum2 = stack.pop()
            if index < n:
                # fill vector B[index] in all possible ways,
                # so that it's still possible to reach 0.
                for v in (-1, 0, 1):
                    sum1_new = sum1 + v * A[index]
                    sum2_new = sum2 + v * A[index - 1 if index else n - 1]
                    if abs(sum1_new) <= ones[index+1] \
                       and abs(sum2_new) <= ones[index] - A[n-1]:
                        C = B[:]
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
    n = int(argv[1]) if len(argv) > 1 else 10

    start_time = time()
    count = compute_probability(n)
    end_time = time()
    duration = int(round(end_time - start_time))

    print("Calculation for n = {} took {}:{:02d} minutes\n" \
          .format(n, duration // 60, duration % 60))

    l = lambda x: str(len(str(x)))
    for i in range(n):
        print("{0:{1}d}  {2:{3}d} / {4}  {5:6.2%}" \
              .format(i+1, l(n), count[i], l(count[0]), 6**n, float(count[i])/6**n))
