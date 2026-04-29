from Models.Graph import Graph
from Models.Airport import Airport
from Models.Route import Route


def build_sample_graph() -> Graph:
    # Aeropuertos de ejemplo
    bog = Airport("BOG", "El Dorado", "Bogota", "Colombia", "UTC-5", True, 55.0, 18.0)
    mde = Airport("MDE", "Jose Maria Cordova", "Medellin", "Colombia", "UTC-5", True, 45.0, 16.0)
    cal = Airport("CAL", "Alfonso Bonilla Aragon", "Cali", "Colombia", "UTC-5", False, 40.0, 15.0)
    ctg = Airport("CTG", "Rafael Nunez", "Cartagena", "Colombia", "UTC-5", False, 60.0, 20.0)

    # Rutas en ambos sentidos para que las conexiones queden claras
    bog.add_adjacencies(Route(mde, 216.0, 1, False, 120.0))
    mde.add_adjacencies(Route(bog, 216.0, 1, False, 120.0))

    bog.add_adjacencies(Route(cal, 279.0, 1, False, 95.0))
    cal.add_adjacencies(Route(bog, 279.0, 1, False, 95.0))

    bog.add_adjacencies(Route(ctg, 216.0, 1, False, 120.0))
    ctg.add_adjacencies(Route(bog, 216.0, 1, False, 120.0))

    mde.add_adjacencies(Route(ctg, 461.0, 1, False, 150.0))
    ctg.add_adjacencies(Route(mde, 461.0, 1, False, 150.0))

    cal.add_adjacencies(Route(ctg, 760.0, 1, True, 200.0))
    ctg.add_adjacencies(Route(cal, 760.0, 1, True, 200.0))

    graph = Graph()
    graph.set_airports([bog, mde, cal, ctg])
    return graph


if __name__ == "__main__":
    sample_graph = build_sample_graph()
    sample_graph.visualize()