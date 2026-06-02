"""
Graph-based schema reasoning using NetworkX.
Builds a relationship graph from foreign keys and discovers optimal JOIN paths
between tables automatically — no hardcoding needed.
"""
import networkx as nx
from database.enterprise_schema import SCHEMA_METADATA
from app.core.logging_config import logger

_graph: nx.DiGraph | None = None


def build_schema_graph() -> nx.DiGraph:
    global _graph
    G = nx.DiGraph()

    for table in SCHEMA_METADATA:
        G.add_node(
            table["table_name"],
            domain=table["domain"],
            description=table["description"],
            columns=[c["name"] for c in table["columns"]],
        )
        for col in table["columns"]:
            if col.get("fk"):
                target_table = col["fk"].split(".")[0]
                target_col = col["fk"].split(".")[1] if "." in col["fk"] else col["fk"]
                G.add_edge(
                    table["table_name"],
                    target_table,
                    via_col=col["name"],
                    target_col=target_col,
                    join_hint=f"{table['table_name']}.{col['name']} = {col['fk']}",
                )

    logger.info(f"Schema graph built: {G.number_of_nodes()} tables, {G.number_of_edges()} relationships")
    _graph = G
    return G


def get_schema_graph() -> nx.DiGraph:
    global _graph
    if _graph is None:
        _graph = build_schema_graph()
    return _graph


def discover_joins(table_names: list[str]) -> list[str]:
    """
    Given a list of relevant tables, find the JOIN conditions that
    connect them — autonomous join discovery via graph traversal.
    """
    G = get_schema_graph()
    G_undirected = G.to_undirected()
    join_hints = []
    seen = set()

    for i, t1 in enumerate(table_names):
        for t2 in table_names[i + 1:]:
            if t1 not in G or t2 not in G:
                continue
            try:
                path = nx.shortest_path(G_undirected, t1, t2)
                if len(path) <= 3:
                    for a, b in zip(path, path[1:]):
                        edge_key = tuple(sorted([a, b]))
                        if edge_key in seen:
                            continue
                        seen.add(edge_key)
                        # Check both directions for the edge
                        if G.has_edge(a, b):
                            hint = G[a][b]["join_hint"]
                        elif G.has_edge(b, a):
                            hint = G[b][a]["join_hint"]
                        else:
                            continue
                        join_hints.append(hint)
                        logger.debug(f"Join discovered: {hint}")
            except nx.NetworkXNoPath:
                pass

    return join_hints


def get_table_neighbors(table_name: str) -> list[str]:
    """Returns all tables directly related to this one."""
    G = get_schema_graph()
    if table_name not in G:
        return []
    return list(G.predecessors(table_name)) + list(G.successors(table_name))


def get_graph_summary() -> dict:
    G = get_schema_graph()
    return {
        "total_tables": G.number_of_nodes(),
        "total_relationships": G.number_of_edges(),
        "domains": list({G.nodes[n].get("domain") for n in G.nodes}),
        "most_connected": sorted(
            [(n, G.degree(n)) for n in G.nodes],
            key=lambda x: x[1], reverse=True
        )[:5],
    }
