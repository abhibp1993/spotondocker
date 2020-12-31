# Copyright (c) 2020-2021, Abhishek N. Kulkarni
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
    The file defines `SpotServer` class which exposes some functionality from spot (see: https://spot.lrde.epita.fr/).
    It manages the communication via ZMQ server.

Author: Abhishek N. Kulkarni <ankulkarni@wpi.edu>
"""

import argparse 
import json
import networkx as nx
import spot 
import zmq


class SpotServer(object):
    """
    Wraps the communication with a (python/C++/VB.net/C#) client on a machine without spot (see: https://spot.lrde.epita.fr/).
    
    Functionality:
        - Manages communication with SpotClient. 
        - Exposes "some" of the spot functionality. 
    """
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server = None
        
        self._server_connect()

    def _server_connect(self):
        address = f"tcp://{self.ip}:{self.port}"
    
        # Configure ZMQ as PAIR-Client 
        context = zmq.Context()
        self.server = context.socket(zmq.PAIR)
        self.server.bind(address)

    def listen(self):
        """
        Waits for incoming queries from client (contains "while-1" loop).
        """
        try:
            while True:
                recv_msg = self.server.recv()
                recv_msg = json.loads(recv_msg)
                
                send_msg = self.respond(recv_msg)
                send_msg = json.dumps(send_msg)

                self.server.send_string(send_msg)
            
        except KeyboardInterrupt:
            pass
        
    def respond(self, msg):
        """
        Runs the spot query and responds with the outcome. 
        
        @param msg: (dict) The dictionary containing the query in the following format  
            query: {
                "query": "spot.<function>",
                "params": {
                    ...
                }
            }
        """
        
        res = {
            "response": msg,
            "status-code": 200,      # 200: OK, 400: Invalid query, 500: Exception raised while processing. Try again.
            "result": None
        }

        try:
            if msg["query"] == "spot.mp_class":
                res["result"] = self.mp_class(msg["params"]["formula"])

            elif msg["query"] == "spot.translate":
                res["result"] = self.translate(msg["params"]["formula"])

            elif msg["query"] == "spot.contains":
                res["result"] = self.contains(msg["params"]["formula1"], msg["params"]["formula2"])

            elif msg["query"] == "spot.equiv":
                res["result"] = self.equiv(msg["params"]["formula1"], msg["params"]["formula2"])

            elif msg["query"] == "spot.randLtl":
                res["result"] = self.rand_ltl(msg["params"]["numAP"], msg["params"]["seed"])

            elif msg["query"] == "spot.getAP":
                res["result"] = self.get_ap(msg["params"]["formula"])

            elif msg["query"] == "spot.toStringLatex":
                res["result"] = self.to_string_latex(msg["params"]["formula"])

            else:
                res["status-code"] = 400
                res["result"] = f"{msg['query']} functionality is not supported."
        
        except Exception as err:
            res["status-code"] = 500
            res["result"] = repr(err)

        finally:
            return res

    def mp_class(self, formula):
        classname = spot.mp_class(formula, 'v')
        return classname

    def translate(self, formula):
        # Translate to automaton
        aut = spot.translate(formula, "BA", "High", "SBAcc", "Complete")

        # Get dot representation of automaton
        aut_str = aut.to_str('dot')
        
        # Convert to graphml
        #   Patch: I currently don't know a better way than to convert dot output
        #          to networkx graph and use it to convert between formats.
        g = nx.MultiDiGraph()
        with open(f"{formula}.dot", 'wb') as file:
            file.write(aut_str.encode('utf-8'))
        
        with open(f"{formula}.dot", 'rb') as file:
            g = nx.drawing.nx_agraph.read_dot(file) 

        json_msg = nx.readwrite.json_graph.node_link_data(g)
        return json_msg

    def contains(self, formula1, formula2):
        f1 = spot.formula(formula1)
        f2 = spot.formula(formula2)
        return spot.contains(f1, f2)
        
    def equiv(self, formula1, formula2):
        f1 = spot.formula(formula1)
        f2 = spot.formula(formula2)
        return spot.are_equivalent(f1, f2)
        
    def rand_ltl(self, num_ap, seed):
        f = spot.randltl(num_ap, output='ltl', seed=seed).relabel(spot.Abc).simplify()
        return next(f).to_str('spot')
        
    def get_ap(self, formula):
        f = spot.formula(formula)
        return [f.to_str('spot') for f in spot.atomic_prop_collect(f)]
        
    def to_string_latex(self, formula):
        return spot.formula(formula).to_str("sclatex")


if __name__ == "__main__":
    
    # Parse input args
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", type=str, nargs='?', default="*", help="IP address to connect to.")
    parser.add_argument("port", type=str, nargs='?', default="7159", help="Port to connect to.")
    args = parser.parse_args()

    # Initialize ZMQ server
    spotserv = SpotServer(args.ip, args.port)

    # Loop indefinitely
    try:
        spotserv.listen()
    except Exception as err:
        print(err)


    