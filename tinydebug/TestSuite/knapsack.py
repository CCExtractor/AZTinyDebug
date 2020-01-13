def knapsack(w, wt, val, n):
    if n == 0 or w == 0:
        return 0

    if wt[n - 1] > w:
        return knapsack(w, wt, val, n - 1)
    else:
        return max(val[n - 1] + knapsack(w - wt[n - 1], wt, val, n - 1), knapsack(w, wt, val, n - 1))
