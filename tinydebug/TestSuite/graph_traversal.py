from collections import deque


def dfs(graph, start):
    visited, stack = [], deque([start])
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.append(vertex)
            stack.extend([x for x in graph[vertex] if x not in visited])
    return visited


def bfs(graph, start):
    visited, queue = [], deque([start])
    while queue:
        vertex = queue.popleft()
        if vertex not in visited:
            visited.append(vertex)
            queue.extend([x for x in graph[vertex] if x not in visited])
    return visited
