import sys
sys.path.append('gen-py')
from spotondocker import SpotOnDocker

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

import argparse
import spot


class SpotOnDockerHandler:
    def __init__(self):
        self.log = {}
    
    def Ping(self):
        print("Ping()")

    def MpClass(self, formula):
        return spot.mp_class(formula, 'v')
    
    def Contains(self, formula1, formula2):
        f1 = spot.formula(formula1)
        f2 = spot.formula(formula2)
        return spot.contains(f1, f2)

    def IsEquivalent(self, formula1, formula2):
        f1 = spot.formula(formula1)
        f2 = spot.formula(formula2)
        return spot.are_equivalent(f1, f2)
        
    def RndLTL(self, numAP, rndSeed):
        f = spot.randltl(numAP, output='ltl', seed=rndSeed).relabel(spot.Abc).simplify()
        return next(f).to_str('spot')

    def GetAP(self, formula):
        f = spot.formula(formula)
        return [f.to_str('spot') for f in spot.atomic_prop_collect(f)]
        
    def ToLatexString(self, formula):
        return spot.formula(formula).to_str("sclatex")

    def Translate(self, formula):
        aut = spot.translate(formula, "BA", "High", "SBAcc", "Complete")
        bdict = aut.get_dict()

        autGraph = SpotOnDocker.TGraph()
        print(type(aut.get_acceptance()))
        autGraph.acceptance = str(aut.get_acceptance())
        autGraph.numAccSets = int(aut.num_sets())
        autGraph.numStates = int(aut.num_states())
        autGraph.initStates = [int(aut.get_init_state_number())]
        autGraph.apNames = [str(ap) for ap in aut.ap()]
        autGraph.formula = str(aut.get_name())
        autGraph.isDeterministic = bool(aut.prop_universal() and aut.is_existential())
        autGraph.isTerminal = bool(aut.prop_terminal())
        autGraph.hasStateBasedAcc = bool(aut.prop_state_acc())
        
        states = []
        edges = []
        for src in range(0, aut.num_states()):
            n = SpotOnDocker.TNode()
            n.id = int(src)

            for edge in aut.out(src):
                e = SpotOnDocker.TEdge()
                e.srcId = int(edge.src)
                e.dstId = int(edge.dst)
                e.label = str(spot.bdd_format_formula(bdict, edge.cond))
                n.isAcc = not (edge.acc is None)
                
                edges.append(e)
            
            states.append(n)
        
        autGraph.nodes = states
        autGraph.edges = edges

        return autGraph


if __name__ == '__main__':
    # Parse input args
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", type=str, nargs='?', default="*", help="IP address to connect to.")
    parser.add_argument("port", type=str, nargs='?', default="7159", help="Port to connect to.")
    args = parser.parse_args()

    # initialize server
    handler = SpotOnDockerHandler()
    processor = SpotOnDocker.Processor(handler)
    transport = TSocket.TServerSocket(host=args.ip, port=args.port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    try:
        server.serve()
    except KeyboardInterrupt:
        pass