import networkx as nx

class OffshoreGraph:

    def __init__(self):
        self.graph = nx.Graph()
        self.build_network()

    def build_network(self):
        edges = [
            ("BASE", "A0", 5),
            ("A0", "A1", 8),
            ("A1", "A2", 4),
            ("A2", "A3", 7),
            ("A3", "A4", 6),
            ("A4", "A5", 9),
        ]

        for u, v, w in edges:
            self.graph.add_edge(u, v, weight=w)

    def route_distance(self, source, target):
        if not nx.has_path(self.graph, source, target):
            raise ValueError(f"No path between {source} and {target}")

        return nx.shortest_path_length(
            self.graph,
            source=source,
            target=target,
            weight="weight"
        )