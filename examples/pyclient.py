# Add spotondocker to path
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import networkx as nx
import spotondocker.client as client


if __name__ == "__main__":
    try:
        import spot
    except ImportError:
        import spotondocker.client as client
        spot = client.SpotOnDockerClient()
    
    
    print(f"1. mp_class(G(a -> Fb)): {spot.mp_class('G(a -> Fb)')}")

    aut = spot.translate("(p1 W 0) | Gp2")
    print(f"2. aut = spot.translate('a'): {type(aut)}, {aut.number_of_nodes()}, {aut.number_of_edges()}")
    
    print(f"3. spot.contains(Fa, Ga): {spot.contains('Fa', 'Ga')}")

    print(f"4. spot.equiv(Fa, Ga): {spot.equiv('Fa', 'Ga')}")

    print(f"5. spot.rand_ltl(3, 90): {spot.rand_ltl(3, rndSeed=90)}")

    print(f"6. spot.get_ap(Fa & Gb): {spot.get_ap('Fa & Gb')}")

    print(f"7. spot.to_string_latex(Fa & Gb & c U d & Xe): {spot.to_string_latex('Fa & Gb & c U d & Xe')}")

