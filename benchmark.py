import networkx as nx
from util import *
from matplotlib import pyplot as plt
from algo import compute_tree, compute_metric, build_stiener_seed
import os


def benchmark_single(factory, budget, loc=None):
    # To make life a little a easier, this function will require you to pass a function
    # which takes no arguments and returns a graph G, start s, and targets
    # So make your own factory method
    #
    # compute a single improvement

    # construct graph
    G, s, targets = factory()

    # get before
    mst, pred = build_stiener_seed(G, s, targets)
    forced, metric, target_list = compute_metric(mst, s, targets, pred)
    before = metric if not forced else 0.0
    # display_tree(G, mst)

    # get after
    mst, pred = compute_tree(G, s, targets, budget, loc=loc)
    forced, metric, target_list = compute_metric(mst, s, targets, pred)
    after = metric if not forced else 0.0
    # display_tree(G, mst)

    improvement = True if after > before else False
    return improvement, before, after


def benchmark_many(n, factory, budget, loc=None):
    # To make life a little a easier, this function will require you to pass a function
    # which takes no arguments and returns a graph G, start s, and targets
    # So make your own factory method
    #
    # compute many improvements

    both_forced = 0
    now_unforced = 0
    unimproved = 0
    improved = 0

    for i in range(n):
        print(f"Starting benchmark {i} / {n - 1}")
        # Set up graph, seed tree, and metric values.
        curr_loc = f"{loc}/{i}" if loc != None else None
        improvement, before, after = benchmark_single(factory, budget, loc=curr_loc)

        if improvement:
            improved += 1
            print("Made Improvements")
            if before == 0.0:
                now_unforced += 1
                print("    Now Unforced")
            else:
                print(f"    Before: {before}")
                print(f"    After:  {after}")
        else:
            unimproved += 1
            print("No Improvements")
            if after == 0.0:
                both_forced += 1
                print("    Still Forced")
        print()

    print(f"Number of graphs = {n}")
    print(f"{both_forced     = }")
    print(f"{now_unforced    = }")
    print(f"{unimproved      = }")
    print(f"{improved        = }")


def main():
    # Initial Parameters
    target_count = 10
    graphx = 40
    graphy = 40

    def factory():
        s, targets = random_points(target_count)

        G = form_grid_graph(s, targets, graphx, graphy)
        # G = form_grid_graph(s, targets, graphx, graphy, triangulate=False)
        # G = form_hex_graph(s, targets, graphx, graphy, 1.0)
        # G = form_triangle_graph(s, targets, graphx, graphy, 1.0)

        round_targets_to_graph(G, s, targets)
        targets = [f"target {i}" for i in range(target_count)]
        s = "start"
        nx.set_node_attributes(G, 0, "paths")
        return G, s, targets

    bench_count = 1
    for i in range(bench_count):
        os.makedirs(f"images/current/{i}")
    benchmark_many(bench_count, factory, float("inf"), loc="images/current")


if __name__ == "__main__":
    main()
