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
File: client.py
Description: 
    The file defines `SpotClient` class which wraps the server-client communication 
    with a Docker container with a proper installation of spot (see: https://spot.lrde.epita.fr/).

Author: Abhishek N. Kulkarni <ankulkarni@wpi.edu>
"""

import contextlib 
import docker
import json
import networkx as nx
import os
import socket
import time
import zmq


class SpotOnDockerError(Exception):
    pass


class SpotClient(object):
    """
    Wraps the server-client communication with a Docker container with a proper installation of spot (see: https://spot.lrde.epita.fr/).
    
    Functionality:
        - Creates a new docker container and launches `SpotServer` on it.
        - Manages communication with SpotServer. 
        - Exposes "some" of the spot functionality. 

    """
    def __init__(self, container_name=None, port=None, client_wait_time=2000):
        """ 
        Creates docker container, zmq client and runs a test-query 
        Default name of container is `spotondocker.pyclient.<port#>`.
        """
        
        # Internal parameters: docker container 
        self.dclient = docker.from_env() 
        self.port = self._find_free_port() if port is None else port
        self.container_name = f"spotondocker.pyclient.{self.port}" if container_name is None else container_name
        self.container = None
        
        # Internal parameters: pyzmq client 
        self.client_wait_time = client_wait_time
        self.context = zmq.Context()
        self.zclient = self.context.socket(zmq.PAIR)

        # Create docker container 
        self._create_docker_container()
        self._create_zmq_client()
        
        # Test query
        query = {
            "query": "spot.mp_class", 
            "params": {
                "formula": str("Fa")
            }
        }

        rep = self._send_query(query)

        # print(rep["status-code"], rep["result"]) 

    def __del__(self):
        self._stop_zmq_client()
        self._stop_docker_container()
    
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
        print("Launching docker container... might take a few seconds.")
        self.container = self.dclient.containers.run(image="abhibp1993/spotondocker:latest",
                                    auto_remove=True,
                                    detach=True,
                                    ports={self.port:self.port},
                                    name=self.container_name,
                                    volumes={os.path.dirname(os.path.realpath(__file__)): {'bind': "/home/server", "mode": 'rw'}},
                                    # volumes={os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "docker_server"): {'bind': "/home/server", "mode": 'rw'}},
                                    command=f"python3 /home/server/server.py * {self.port}"
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

    def _create_zmq_client(self):
        address = f"tcp://localhost:{self.port}"
        self.zclient.connect(address)
        self.zclient.RCVTIMEO = self.client_wait_time # in milliseconds
        # print("Created Zmw", self.zclient)

    def _stop_zmq_client(self):
        # Place holder for future. 
        # Presently, nothing needs to be done to disconnect zmq client.
        pass
        # print("Stopped zmq", self.zclient)

    def _send_query(self, query):
        """
        Sends the query to server and receives to response. 

        @param query: (dict) A json-friendly dictionary in following format.
            query: {
                "query": "spot.<function>",
                "params": {
                    ...
                }
            }
        """
        # Jsonify the query
        json_query = json.dumps(query)
        
        # Send to server
        self.zclient.send_string(json_query)

        # Wait for response
        rep = self.zclient.recv()

        # UnJsonify the response
        rep = json.loads(rep)

        # Return response
        return rep

    def _handle_error(self, rep):
        """
        Handles errors communicated by server during processing of query. 

        Remarks: 
            1. rep["response"] contains the query to which the response was sent.
            2. resp["result"] contains details about the error. 
            3. Code 400 = Invalid Query. 
            4. Code 500 = Exception/Error raised during running code.
        """
        if rep["status-code"] == 400:
            raise SpotOnDockerError(f"Code 400: Invalid Query. \n{rep['response']}")

        elif rep["status-code"] == 500:
            raise SpotOnDockerError(f"Code 500: Exception in spot service." 
                                    f"\nQuery: {rep['response']}"
                                    f"\nException: {rep['result']}"
                                    f"\nGuideline: Check if all parameters are correct. E.g. is the spot formula valid?"
                                    )

    def mp_class(self, formula):

        query = {
            "query": "spot.mp_class", 
            "params": {
                "formula": str(formula)
            }
        }

        rep = self._send_query(query)

        if rep["status-code"] == 200:
            return rep["result"]
        else:
            self._handle_error(rep)

    def translate(self, formula):

        query = {
            "query": "spot.translate", 
            "params": {
                "formula": str(formula)
            }
        }

        rep = self._send_query(query)

        # aut = nx.MultiDiGraph()
        if rep["status-code"] == 200:
            aut_str = rep["result"]
            aut = nx.readwrite.json_graph.node_link_graph(aut_str)
            return aut
        else:
            self._handle_error(rep)

    def contains(self, formula1, formula2):
        query = {
            "query": "spot.contains", 
            "params": {
                "formula1": str(formula1),
                "formula2": str(formula2),
            }
        }

        rep = self._send_query(query)

        if rep["status-code"] == 200:
            return bool(rep["result"])
        else:
            self._handle_error(rep)

    def equiv(self, formula1, formula2):
        query = {
            "query": "spot.equiv", 
            "params": {
                "formula1": str(formula1),
                "formula2": str(formula2),
            }
        }

        rep = self._send_query(query)

        if rep["status-code"] == 200:
            return bool(rep["result"])
        else:
            self._handle_error(rep)

    def rand_ltl(self, num_ap, seed=0):
        query = {
            "query": "spot.randLtl", 
            "params": {
                "numAP": num_ap,
                "seed": seed
            }
        }

        rep = self._send_query(query)

        if rep["status-code"] == 200:
            return rep["result"]
        else:
            self._handle_error(rep)

    def get_ap(self, formula):
        query = {
            "query": "spot.getAP", 
            "params": {
                "formula": str(formula)
            }
        }

        rep = self._send_query(query)

        if rep["status-code"] == 200:
            return rep["result"]
        else:
            self._handle_error(rep)

    def to_string_latex(self, formula):
        query = {
            "query": "spot.toStringLatex", 
            "params": {
                "formula": str(formula)
            }
        }

        rep = self._send_query(query)

        if rep["status-code"] == 200:
            return rep["result"]
        else:
            self._handle_error(rep)
  