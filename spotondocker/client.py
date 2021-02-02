import sys, os
# sys.path.append('gen-py')
dir_spotondocker = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_spotondocker)

from genpy.spotondocker import SpotOnDocker

import contextlib 
import docker
import networkx as nx
import os
import socket
import time

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


class SpotOnDockerClient:
    def __init__(self, container_name=None, port=None, client_wait_time=2000):
        # Internal parameters: docker container 
        self.dclient = docker.from_env() 
        self.port = self._find_free_port() if port is None else port
        self.container_name = f"spotondocker.pyclient.{self.port}" if container_name is None else container_name
        self.container = None
        self._create_docker_container()

        # Thrift Client initialize
        self.client = None
        self.transport = None
        self._start_thrift_client()


    def __del__(self):
        self._stop_docker_container()
        self.transport.close()
    
    @staticmethod
    def _find_free_port():
        """ 
        Finds a free port to use with ZMQ. 
        
        Code Reference: https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number 
        """
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]
    

    def _create_docker_container(self):
        # Create and run docker container
        # print("Launching docker container... might take a few seconds.")
        self.container = self.dclient.containers.run(image="abhibp1993/spotondocker:v0.3",
                                    auto_remove=True,
                                    detach=True,
                                    ports={self.port:self.port},
                                    name=self.container_name,
                                    #volumes={os.path.dirname(os.path.realpath(__file__)): {'bind': "/home/server", "mode": 'rw'}},
                                    # volumes={os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "docker_server"): {'bind': "/home/server", "mode": 'rw'}},
                                    command=f"python3 server.py * {self.port}"
                )

        # Allow the process to start
        time.sleep(0.5)

        # TODO: Check if python is running 
        # print("Created docker", self.container.status)

    def _stop_docker_container(self):
        try:
            self.container.kill()
        except Exception:
            pass
        # print("Killed docker")

    def _start_thrift_client(self):
        # Make socket
        self.transport = TSocket.TSocket('localhost', self.port)

        # Buffering is critical. Raw sockets are very slow
        self.transport = TTransport.TBufferedTransport(self.transport)

        # Wrap in a protocol
        protocol = TBinaryProtocol.TBinaryProtocol(self.transport)

        # Create a client to use the protocol encoder
        self.client = SpotOnDocker.Client(protocol)
        
        # Connect!
        self.transport.open()

    def ping(self):
        self.client.Ping()

    def mp_class(self, formula):
        return self.client.MpClass(formula)
    
    def contains(self, formula1, formula2):
        return self.client.Contains(formula1, formula2)

    def equiv(self, formula1, formula2):
        return self.client.IsEquivalent(formula1, formula2)
        
    def rand_ltl(self, numAP, rndSeed):
        return self.client.RndLTL(numAP, rndSeed)

    def get_ap(self, formula):
        return self.client.GetAP(formula)
        
    def to_string_latex(self, formula):
        return self.client.ToLatexString(formula)

    def translate(self, formula):
        thriftGraph = self.client.Translate(formula)
        aut = nx.MultiDiGraph(
                acc=thriftGraph.acceptance, 
                numAccSets=thriftGraph.numAccSets,
                numStates=thriftGraph.numStates,
                initStates=thriftGraph.initStates,
                apNames=thriftGraph.apNames,
                formula=thriftGraph.formula,
                isDeterministic=thriftGraph.isDeterministic,
                hasStateBasedAcc=thriftGraph.hasStateBasedAcc,
                isTerminal=thriftGraph.isTerminal
            )
        
        for tnode in thriftGraph.nodes:
            aut.add_node(tnode.id, isAcc=tnode.isAcc)
        
        for tedge in thriftGraph.edges:
            aut.add_edge(tedge.srcId, tedge.dstId, label=tedge.label)

        return aut


if __name__ == '__main__':
    spot = SpotOnDockerClient()
    print(spot.MpClass("Fa"))

