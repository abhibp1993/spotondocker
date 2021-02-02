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
File: client.py
Description: 
    The file defines `SpotOnDockerClient` class which wraps the server-client communication 
    with a Docker container containing a proper installation of spot (see: https://spot.lrde.epita.fr/).

Author: Abhishek N. Kulkarni <abhi.bp1993@gmail.com>
"""

import sys, os
dir_spotondocker = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_spotondocker)

from genpy.spotondocker import SpotOnDocker
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

import contextlib 
import docker
import networkx as nx
import os
import socket
import time


class SpotOnDockerClient:
     """
    Wraps the server-client communication with a Docker container with a proper installation of spot (see: https://spot.lrde.epita.fr/).
    
    Functionality:
        - Creates a new docker container and launches SpotOnDocker server on it.
        - Manages communication with SpotOnDocker server. 
        - Exposes "some" of the spot functionality. 

    """
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
        try:
            self._stop_docker_container()
        except:
            pass

        try:
            self.transport.close()
        except:
            pass
    
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
        self.container = self.dclient.containers.run(image="abhibp1993/spotondocker",
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
        """ 
        Return the class of f in the temporal hierarchy of Manna and Pnueli (PODC'90). 
        
        The class is indicated using a character among:
            - "bottom" safety properties that are also guarantee properties
            - "guarantee" properties that are not also safety properties
            - "safety" properties that are not also guarantee properties
            - "obligation" properties that are not safety or guarantee properties
            - "persistence" properties that are not obligations
            - "recurrence" properties that are not obligations
            - "top" properties that are not persistence or recurrence properties  
        
        Ref: https://spot.lrde.epita.fr/doxygen/group__tl__hier.html#ga9da740d4283ad977895d64b82d838ac2
        """
        return self.client.MpClass(formula)
    
    def contains(self, formula1, formula2):
        """
        Test if the language of right formula is included in that of left formula.

        Both arguments can be either formulas (string). 
        Formulas will be converted into automata.

        The inclusion check if performed by ensuring that the automaton associated 
        to right does not intersect the automaton associated to the complement of left. 
        It helps if left is a deterministic automaton or a formula (because in both 
        cases complementation is easier).

        Ref: https://spot.lrde.epita.fr/doxygen/group__containment.html#gaafb6ae0dc34a6d7ed1382ce5b8962a61
        """
        return self.client.Contains(formula1, formula2)

    def equiv(self, formula1, formula2):
        """
        Test if the language of left is equivalent to that of right.
        Both arguments can be either formulas (string). Formulas will be converted into automata.

        Ref: https://spot.lrde.epita.fr/doxygen/group__containment.html#ga30fcc11035f85051dee3d3decc4cc9c8
        """
        return self.client.IsEquivalent(formula1, formula2)
        
    def rand_ltl(self, numAP, rndSeed):
        """
        Create a random LTL generator using atomic propositions given number of APs and a random seed.
        Ref: https://spot.lrde.epita.fr/doxygen/classspot_1_1random__ltl.html
        """
        return self.client.RndLTL(numAP, rndSeed)

    def get_ap(self, formula):
        """
        Return the set of atomic propositions occurring in a formula.
        
        Ref: https://spot.lrde.epita.fr/doxygen/group__tl__misc.html#ga10d99d88d084d657ddba2bb69f22e75b
        """
        return self.client.GetAP(formula)
        
    def to_string_latex(self, formula):
        return self.client.ToLatexString(formula)

    def translate(self, formula):
        """
        Translates formula to a state-based Buchi automaton. 
        
        Spot's translate function is provided with following parameters (see reference 
        for descriptions of parameters):
        - "BA"
        - "High", 
        - "SBAcc", 
        - "Complete"

        Ref: https://spot.lrde.epita.fr/doxygen/classspot_1_1translator.html
        """
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
