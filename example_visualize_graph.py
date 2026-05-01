from Models.Graph import Graph
from Models.Airport import Airport
from Models.Aircraft import Aircraft
from Models.Route import Route


def build_sample_graph() -> Graph:
    # ── Aeropuertos ───────────────────────────────────────────────────────────
    bog = Airport("BOG", "El Dorado",         "Bogotá",       "Colombia", "UTC-5", True,  55.0, 18.0)
    mde = Airport("MDE", "José M. Córdova",   "Medellín",     "Colombia", "UTC-5", True,  45.0, 16.0)
    cal = Airport("CAL", "Alfonso Bonilla",   "Cali",         "Colombia", "UTC-5", False, 40.0, 15.0)
    ctg = Airport("CTG", "Rafael Núñez",      "Cartagena",    "Colombia", "UTC-5", True,  60.0, 20.0)
    baq = Airport("BAQ", "Ernesto Cortissoz", "Barranquilla", "Colombia", "UTC-5", False, 50.0, 17.0)
    bga = Airport("BGA", "Palonegro",         "Bucaramanga",  "Colombia", "UTC-5", False, 38.0, 14.0)
    pei = Airport("PEI", "Matecaña",          "Pereira",      "Colombia", "UTC-5", False, 35.0, 13.0)
    smr = Airport("SMR", "Simón Bolívar",     "Santa Marta",  "Colombia", "UTC-5", False, 42.0, 14.0)
    adz = Airport("ADZ", "Gustavo Rojas",     "San Andrés",   "Colombia", "UTC-5", False, 70.0, 22.0)
    let = Airport("LET", "Alfredo Vásquez",   "Leticia",      "Colombia", "UTC-5", False, 30.0, 12.0)

    # ── Aeronaves (id, tipo, costo_por_km, tiempo_por_km) ────────────────────
    # Bajo costo / lento  → bueno para minimizar costo, malo para minimizar tiempo
    a320_lc = Aircraft("A320-LC", "Airbus A320 Low-Cost",  0.06, 3)
    atr72   = Aircraft("ATR72",   "ATR 72 Turboprop",      0.07, 4)
    # Estándar / balanceado
    e190    = Aircraft("E190",    "Embraer E190",           0.09, 2)
    b737    = Aircraft("B737",    "Boeing 737",             0.11, 2)
    # Premium / rápido → malo para minimizar costo, bueno para minimizar tiempo
    b787    = Aircraft("B787",    "Boeing 787 Dreamliner",  0.20, 1)

    # ── Rutas ─────────────────────────────────────────────────────────────────
    # BOG ↔ MDE  216 km  | varios aviones → A320-LC elegido por costo, E190 por tiempo
    bog.add_adjacencies(Route(mde, 216.0, 1, False, 130.0, [a320_lc, b737, e190]))
    mde.add_adjacencies(Route(bog, 216.0, 1, False, 130.0, [a320_lc, b737, e190]))

    # BOG ↔ CAL  279 km
    bog.add_adjacencies(Route(cal, 279.0, 1, False,  95.0, [a320_lc, e190]))
    cal.add_adjacencies(Route(bog, 279.0, 1, False,  95.0, [a320_lc, e190]))

    # BOG ↔ CTG  1080 km | solo económico → barato pero lento
    bog.add_adjacencies(Route(ctg, 1080.0, 1, False, 350.0, [a320_lc]))
    ctg.add_adjacencies(Route(bog, 1080.0, 1, False, 350.0, [a320_lc]))

    # BOG → BAQ  980 km  | unidireccional y solo premium → rápido pero caro
    #   → Por costo preferirá: BOG→BGA→BAQ (A320-LC)
    #   → Por tiempo preferirá: directo (B787)
    bog.add_adjacencies(Route(baq, 980.0, 1, False, 400.0, [b787]))

    # BOG ↔ BGA  360 km
    bog.add_adjacencies(Route(bga, 360.0, 1, False, 120.0, [a320_lc, atr72]))
    bga.add_adjacencies(Route(bog, 360.0, 1, False, 120.0, [a320_lc, atr72]))

    # BOG ↔ PEI  200 km
    bog.add_adjacencies(Route(pei, 200.0, 1, False,  80.0, [atr72, e190]))
    pei.add_adjacencies(Route(bog, 200.0, 1, False,  80.0, [atr72, e190]))

    # BOG → ADZ  775 km  | unidireccional y solo premium → rápido pero caro
    #   → Por costo preferirá: BOG→CTG→ADZ (A320-LC)  = 1080*0.06 + 720*0.06 = 108.0
    #   → Por tiempo preferirá: directo (B787)         = 775*1     = 775
    bog.add_adjacencies(Route(adz, 775.0, 1, False, 310.0, [b787]))

    # BOG → LET  1100 km | unidireccional y solo premium
    #   → Por costo preferirá: BOG→CAL→LET (A320-LC)  = 279*0.06 + 1000*0.06 = 76.74
    #   → Por tiempo preferirá: directo (B787)         = 1100*1   = 1100
    bog.add_adjacencies(Route(let, 1100.0, 1, False, 450.0, [b787]))

    # MDE ↔ CTG  620 km
    mde.add_adjacencies(Route(ctg, 620.0, 1, False, 200.0, [a320_lc, b737]))
    ctg.add_adjacencies(Route(mde, 620.0, 1, False, 200.0, [a320_lc, b737]))

    # MDE ↔ PEI  120 km
    mde.add_adjacencies(Route(pei, 120.0, 1, False,  50.0, [atr72, e190]))
    pei.add_adjacencies(Route(mde, 120.0, 1, False,  50.0, [atr72, e190]))

    # MDE ↔ BGA  330 km
    mde.add_adjacencies(Route(bga, 330.0, 1, False, 110.0, [atr72, e190]))
    bga.add_adjacencies(Route(mde, 330.0, 1, False, 110.0, [atr72, e190]))

    # CAL ↔ PEI  80 km
    cal.add_adjacencies(Route(pei,  80.0, 1, False,  30.0, [atr72, e190]))
    pei.add_adjacencies(Route(cal,  80.0, 1, False,  30.0, [atr72, e190]))

    # CAL → LET  1000 km | unidireccional y solo económico
    cal.add_adjacencies(Route(let, 1000.0, 1, False, 320.0, [a320_lc]))

    # CTG ↔ BAQ  120 km
    ctg.add_adjacencies(Route(baq, 120.0, 1, False,  45.0, [atr72, e190]))
    baq.add_adjacencies(Route(ctg, 120.0, 1, False,  45.0, [atr72, e190]))

    # CTG ↔ SMR  210 km | solo turbohélice económico
    ctg.add_adjacencies(Route(smr, 210.0, 1, False,  70.0, [atr72]))
    smr.add_adjacencies(Route(ctg, 210.0, 1, False,  70.0, [atr72]))

    # CTG → ADZ  720 km | unidireccional y solo económico → ruta barata hacia San Andrés
    ctg.add_adjacencies(Route(adz, 720.0, 1, False, 230.0, [a320_lc]))

    # BAQ ↔ SMR  90 km
    baq.add_adjacencies(Route(smr,  90.0, 1, False,  35.0, [atr72, e190]))
    smr.add_adjacencies(Route(baq,  90.0, 1, False,  35.0, [atr72, e190]))

    # BAQ ↔ BGA  480 km | solo económico
    baq.add_adjacencies(Route(bga, 480.0, 1, False, 155.0, [a320_lc]))
    bga.add_adjacencies(Route(baq, 480.0, 1, False, 155.0, [a320_lc]))

    graph = Graph()
    graph.set_airports([bog, mde, cal, ctg, baq, bga, pei, smr, adz, let])
    return graph


def print_results(label: str, distances: dict, path: list) -> None:
    SEP = "=" * 62
    print(f"\n{SEP}")
    print(f"  {label}")
    print(f"{SEP}")
    print(f"  Ruta óptima  : {' → '.join(path)}")
    print(f"  Peso total   : {distances[path[-1]]:.2f}")
    print(f"\n  Distancias desde {path[0]}:")
    for code, dist in sorted(distances.items()):
        value  = "∞" if dist == float("inf") else f"{dist:.2f}"
        marker = " ◄ destino" if code == path[-1] else ""
        print(f"    {code}: {value}{marker}")


if __name__ == "__main__":
    graph = build_sample_graph()

    # ── Grafo completo ────────────────────────────────────────────────────────
    graph.visualize()

    # ── BOG → ADZ (San Andrés) ────────────────────────────────────────────────
    # Esperado  por COSTO : BOG→CTG→ADZ  (108.00  — A320-LC económico)
    # Esperado  por TIEMPO: BOG→ADZ      (775     — B787 directo)
    dist_cost, _, path_cost = graph.dijkstra_by_cost("BOG", "ADZ")
    dist_time, _, path_time = graph.dijkstra_by_time("BOG", "ADZ")
    print_results("Dijkstra por COSTO  — BOG → ADZ", dist_cost, path_cost)
    print_results("Dijkstra por TIEMPO — BOG → ADZ", dist_time, path_time)
    graph.visualize_with_route_by_cost(path_cost, title="Ruta más BARATA: BOG → ADZ")
    graph.visualize_with_route_by_time(path_time, title="Ruta más RÁPIDA: BOG → ADZ")

    # ── BOG → BAQ (Barranquilla) ──────────────────────────────────────────────
    # Esperado  por COSTO : BOG→BGA→BAQ  (50.40   — A320-LC por dos tramos cortos)
    # Esperado  por TIEMPO: BOG→BAQ      (980     — B787 directo)
    dist_cost, _, path_cost = graph.dijkstra_by_cost("BOG", "BAQ")
    dist_time, _, path_time = graph.dijkstra_by_time("BOG", "BAQ")
    print_results("Dijkstra por COSTO  — BOG → BAQ", dist_cost, path_cost)
    print_results("Dijkstra por TIEMPO — BOG → BAQ", dist_time, path_time)
    graph.visualize_with_route_by_cost(path_cost, title="Ruta más BARATA: BOG → BAQ")
    graph.visualize_with_route_by_time(path_time, title="Ruta más RÁPIDA: BOG → BAQ")

    # ── BOG → LET (Leticia) ───────────────────────────────────────────────────
    # Esperado  por COSTO : BOG→CAL→LET  (76.74   — A320-LC vía Cali)
    # Esperado  por TIEMPO: BOG→LET      (1100    — B787 directo)
    dist_cost, _, path_cost = graph.dijkstra_by_cost("BOG", "LET")
    dist_time, _, path_time = graph.dijkstra_by_time("BOG", "LET")
    print_results("Dijkstra por COSTO  — BOG → LET", dist_cost, path_cost)
    print_results("Dijkstra por TIEMPO — BOG → LET", dist_time, path_time)
    graph.visualize_with_route_by_cost(path_cost, title="Ruta más BARATA: BOG → LET")
    graph.visualize_with_route_by_time(path_time, title="Ruta más RÁPIDA: BOG → LET")
