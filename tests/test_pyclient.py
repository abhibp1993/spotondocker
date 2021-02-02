# import os
# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pytest
import networkx as nx
import spotondocker.client as client


def test_import():
    try:
        import spot
    except ImportError:
        import spotondocker.client as client
        spot = client.SpotOnDockerClient()

def test_functions():
    import spotondocker.client as client
    spot = client.SpotOnDockerClient()

    # Manna-Pnueli class
    assert spot.mp_class('G(a -> Fb)') == "recurrence"
    
    # Translate to automaton
    aut = spot.translate("(p1 W 0) | Gp2")
    assert aut.number_of_nodes() == 4
    assert aut.number_of_edges() == 9

    # Containment and equivalence
    assert spot.contains('Fa', 'Ga') ==  True
    assert spot.equiv('Fa', 'Ga') == False

    # Get APs
    assert spot.get_ap('Fa & Gb') == ["a", "b"] or spot.get_ap('Fa & Gb') == ["b", "a"]

