from util import build_graph
import networkx as nx
import sys
from matplotlib import pyplot as plt
from benchmark import display_tree


def compute_SSSP(G, targets):
    # Compute the SSSP for each target using Dijkstra's
    target_paths = dict()
    for target in targets:
        target_paths[target] = nx.single_source_dijkstra(G, target)
    return target_paths


def build_stiener_seed(G, s, targets):
    # Build the seed MST and trim it.
    mst = nx.minimum_spanning_tree(G)
    pred = nx.dfs_predecessors(mst, s)

    # Mark paths from targets towards the source.
    for v in targets:
        while v != s:
            mst.nodes[v]["paths"] += 1
            v = pred[v]
    mst.nodes[s]["paths"] = len(targets)

    # Remove nodes past targets with no further targets.
    remove = []
    for v in mst.nodes():
        if mst.nodes[v]["paths"] == 0:
            remove.append(v)

    for v in remove:
        mst.remove_node(v)

    return mst


def compute_metric(mst, s, targets):
    # Determine Counterdeception metric, mark if the tree has a forced path.
    # TODO: Define forced path

    pred = nx.dfs_predecessors(mst, s)
    forced = False
    metric = mst.size(weight="weight")
    # min_target = None
    target_metrics = []

    for v in targets:
        cur = v
        curdist = 0
        while cur != s and mst.nodes[cur]["paths"] == 1:
            # print(cur)
            # print("see node:", mst.nodes[cur])
            if mst.nodes[cur]["paths"] == 1:
                curdist += mst.edges[cur, pred[cur]]["weight"]
            cur = pred[cur]
        if curdist == 0:
            forced = True
        else:
            target_metrics.append((curdist, v))
    target_metrics = sorted(target_metrics)
    metric = target_metrics[0][0]

    return forced, metric, target_metrics


def main():
    # Initial Parameters
    count = 10
    graphx = 50
    graphy = 50

    # Set up graph, seed tree, and metric values.
    G, s, targets = build_graph(count, graphx, graphy)
    target_paths = compute_SSSP(G, targets)
    mst = build_stiener_seed(G, s, targets)
    mstbench = mst.copy()
    forced, metric, target_list = compute_metric(mst, s, targets)
    metricbench = metric

    # budget = mst.size(weight="weight") * 5
    budget = float("inf")

    originalsize = mst.size(weight="weight")
    print("FORCED: ", forced)

    display_tree(G, mst)
    # print(nx.single_source_dijkstra(G, s))

    old_metric = metric + 1
    curcost = mst.size(weight="weight")
    print(mst.nodes())

    # Continue until we find no local improvement
    while old_metric != metric:
        old_metric = metric
        # Pick a target starting with the minimum contribution to the metric distance
        for dist, v in target_list:
            pred = nx.dfs_predecessors(mst, s)

            # Make a copy of the MST to remove the target and corresponding path from.
            mstprime = mst.copy()
            updated = False

            # Remove the target and its path from the tree.
            toremove = []
            cur = v
            while cur != s and mstprime.nodes[cur]["paths"] == 1:
                toremove.append(cur)
                cur = pred[cur]
            for node in toremove:
                mstprime.remove_node(node)

            # Compute Dijkstras from the target in the original graph
            dists, dijpath = nx.single_source_dijkstra(G, v)

            # For each node on the remaining tree:
            for potential in mstprime.nodes():
                # Retrieve the pred shortest path
                path = dijpath[potential]
                # Check if the path crosses any nodes in the tree
                sb = False
                # print(f"path {path}")
                for x in path[:-1]:
                    if x in mstprime.nodes():
                        sb = True
                if sb:
                    continue

                # Make a new tree to reattach the target to.
                mstcheck = mstprime.copy()
                # Add node and path to the tree
                for i in range(len(path) - 1):
                    mstcheck.add_node(path[i], paths=1, pos=G.nodes[path[i]]["pos"])
                    if path[i + 1] not in mstcheck.nodes():
                        mstcheck.add_node(
                            path[i + 1], paths=1, pos=G.nodes[path[i]]["pos"]
                        )
                    mstcheck.add_edge(
                        path[i],
                        path[i + 1],
                        weight=G.edges[path[i], path[i + 1]]["weight"],
                    )

                predcheck = nx.dfs_predecessors(mstcheck, s)
                nx.set_node_attributes(mstcheck, 0, "paths")
                for v in targets:
                    while v != s:
                        mstcheck.nodes[v]["paths"] += 1
                        v = predcheck[v]
                mstcheck.nodes[s]["paths"] = len(targets)
                # print("here")
                forcedp, metricp, target_listp = compute_metric(mstcheck, s, targets)
                if (
                    forcedp == False
                    and forced == True
                    or (metricp > metric and forcedp == forced)
                ):
                    if mstcheck.size(weight="weight") < budget:
                        print("update!")
                        print(
                            "old metric ",
                            metric,
                            "new metric ",
                            metricp,
                            "forced ",
                            forcedp,
                        )
                        # print(mstcheck.nodes())
                        print(nx.get_node_attributes(mstcheck, "paths"))
                        mst = mstcheck
                        forced = forcedp
                        metric = metricp
                        target_list = target_listp
                        updated = True
                        display_tree(G, mst)

                        break
            if updated:
                break

    print(
        f"budget: {budget} original mst: {mstbench} original metric: {metricbench} original size: {originalsize}"
    )
    print(
        f"final tree: {mst} final metric: {metric} final size: {mst.size(weight='weight')} forced: {forced}"
    )
    display_tree(G, mst)


if __name__ == "__main__":
    main()