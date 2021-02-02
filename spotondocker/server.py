# Copyright (c) 2020-2021, Abhishek N. Kulkarni <abhi.bp1993@gmail.com>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Project: spotondocker
URL: https://github.com/abhibp1993/spotondocker
File: server.py
Description: 
    The file defines `SpotOnDockerHandler` class which exposes some functionality from spot (see: https://spot.lrde.epita.fr/).
    It manages the communication via Apache Thrift server.

Author: Abhishek N. Kulkarni <abhi.bp1993@gmail.com>
"""

import sys
sys.path.append('genpy')
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