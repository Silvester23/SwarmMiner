from itertools import chain, combinations
from treelib import Node, Tree

class SwarmFinder():
    def __init__(self, snapshots, min_o, min_t):
        self.snapshots = snapshots
        self.min_o = min_o
        self.min_t = min_t
        self.objects = frozenset([o for s in self.snapshots for c in s for o in c])
        self.object_sets = self.create_object_sets()

        self.tree = self.create_powerset_tree()
        self.tree.show()
        self.find_swarms(self.tree[self.tree.root])

    def find_swarms(self, node):
        for child_id in node.fpointer:
            if self.check_apriori_prune(child_id):
                if self.check_backward_prune(child_id):
                    self.find_swarms(self.tree[child_id])
                    if self.check_closure(child_id) and self.check_min_o(child_id):
                        print child_id, "is a closed swarm."
                else:
                    print "Backward-pruning", child_id
            else:
                print "Apriori-Pruning", child_id


    def powerset(self, iterable):
        s = list(iterable)
        return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

    def get_max_timeset(self, object_set):
        "Get the timestamps of all snapshots which contain a cluster that is a superset of object_set."
        return set(
            [index for (index, snapshot) in enumerate(self.snapshots) for c in snapshot if object_set.issubset(c)])

    def create_powerset_tree(self):
        tree = Tree(None)
        for idx, s in enumerate(self.object_sets):
            if idx == 0:
                tree.create_node((s, self.get_max_timeset(s)), s)
            else:
                parent_index = frozenset(sorted(list(s)[0:-1]))
                tree.create_node((s, self.get_max_timeset(s)), s, parent_index)
        return tree

    def create_object_sets(self):
        return map(frozenset, self.powerset(self.objects))

    def check_apriori_prune(self, node_index):
        return len(self.tree[node_index].tag[1]) >= self.min_t

    def check_min_o(self, object_set):
        return len(object_set) >= self.min_o

    def check_backward_prune(self, node_index):
        object_set = self.tree[node_index].tag[0]
        if not object_set:
            return True
        else:
            remaining_objects = [o for o in self.objects - object_set if o < max(object_set)]
            for o in remaining_objects:
                passes = False
                for t in self.get_max_timeset(object_set):
                    if not self.get_object_set_clusters(object_set, t).issubset(self.get_object_clusters(o, t)):
                        passes = True
                if not passes:
                    return False
        return True

    def check_closure(self, node_index):
        object_set = self.tree[node_index].tag[0]
        max_timeset = self.tree[node_index].tag[1]
        remaining_objects = [o for o in self.objects - object_set if o > max(object_set)]
        if not remaining_objects:
            return True
        else:
            for o in remaining_objects:
                if self.get_max_timeset(object_set | frozenset([o])) == max_timeset:
                    return False
        return True

    def get_object_clusters(self, o, timestamp):
        return set([c for c in self.snapshots[timestamp] if o in c])

    def get_object_set_clusters(self, object_set, timestamp):
        if len(object_set) > 0:
            return set.intersection(*[self.get_object_clusters(o, timestamp) for o in object_set])
        else:
            return set()


def main():
    snapshots = [[frozenset([1, 2, 3, 4, 5])],
                 [frozenset([1, 2]), frozenset([3, 4]), frozenset([5])],
                 [frozenset([1, 4]), frozenset([3, 5]), frozenset([2])],
                 [frozenset([1, 4]), frozenset([2, 3, 5])],
                 [frozenset([1, 4]), frozenset([2]), frozenset([3]), frozenset([5])]
    ]

    # snapshots = [
    #[frozenset([1,2,4]),frozenset([3])],
    #[frozenset([1,2,4]),frozenset([1,3])],
    #[frozenset([1]),frozenset([2,3,4])],
    #[frozenset([1,2,4]),frozenset([3])]
    #]

    s = SwarmFinder(snapshots, 2, 4)


if __name__ == "__main__":
    main()
