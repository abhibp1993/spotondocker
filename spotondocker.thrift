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

/******************************************************************************
* Project: spotondocker
* URL: https://github.com/abhibp1993/spotondocker
* File: spotondocker.thrift
* Description: 
*     Defines the communication interface used by dockerized service. 
* 
* Author: Abhishek N. Kulkarni <abhi.bp1993@gmail.com>
******************************************************************************/

namespace cpp spotondocker
namespace py spotondocker


/* Node structure of an automaton node. */
struct TNode {
    1: i32 id,
    2: bool isAcc,
}

/* Edge structure of an automaton edge. */
struct TEdge {
    1: i32 srcId,
    2: i32 dstId,
    3: string label,
}

/* Automaton graph. */
struct TGraph {
    1: string acceptance,
    2: i32 numAccSets,
    3: i32 numStates,
    4: list<i32> initStates,
    5: list<string> apNames,
    6: string formula,
    7: bool isDeterministic,
    8: bool hasStateBasedAcc,
    9: bool isTerminal,
    10: list<TNode> nodes,
    11: list<TEdge> edges,
}

/* Functionality provided by SpotOnDocker service. */
service SpotOnDocker {
    void Ping(),
    string MpClass(1:string formula),
    bool Contains(1:string formula1, 2:string formula2),
    bool IsEquivalent(1:string formula1, 2:string formula2),
    string RndLTL(1:i32 numAP, 2:i32 rndSeed),
    list<string> GetAP(1:string formula),
    string ToLatexString(1:string formula),
    TGraph Translate(1:string formula),
}
