class GraphEngine:
    @staticmethod
    def build_graph(schema):
        return {
            "nodes": {node.id: node for node in schema.nodes},
            "edges": schema.edges
        }
