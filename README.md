# SpotOnDocker

**SpotOnDocker** is a utility which exposes *some* of [spot's](spot.lrde.epita.fr) functions as a service. The functions can be called using client API provided in C++, Python, VB.NET and C#.

Note: In v0.1, only Python client API is available). 


Supported `spot` Functions:
- `mp_class`: Returns class of LTL formula in Manna-Pnueli hierarchy.
- `translate`: Translates LTL formula to Buchi automaton.
- `contains`: Checks if the language of an LTL formula is contained within another's.
- `equiv`: Checks of the language of two LTL formulas is equivalent.
- `rand_ltl`: Generates a random LTL formula.
- `get_ap`: Gets the atomic propositions from given LTL formula.
- `to_string_latex`: LaTeX-friendly writing of LTL formula.


## Installation Instructions

### Server Setup

1. Install [Docker](https://docs.docker.com/get-docker/). Skip if already installed. 

2. Get the latest version of spotondocker image. 
    ```
    docker pull abhibp1993/spotondocker
    ```

3. Download the latest release of source code from [https://github.com/abhibp1993/spotondocker/releases](https://github.com/abhibp1993/spotondocker/releases) and unzip it. 


### Python Client Setup

The following packages are required. 
- networkx
- pyzmq

```
pip3 install pyzmq networkx
```

    
## Example (Python Client API)

Add the path of unzipped `spotondocker` folder to the python file. 
```python
import os
import sys
sys.path.append('path.to.spotondocker.folder')
```

Create a `SpotClient` instance. This will create a docker container and initialize the communication. 
```
spot = SpotClient()
```


Call the spot functions (only the supported ones!) as usual. For example, to get the class of formula `G(a -> Fb)` in Manna Pnueli hierarchy, we can call
```
spot.mp_class('G(a -> Fb)')
```
which will return a verbose like `safety`, `guarantee`, ... 


In case of translation, the `SpotClient.translate(..)` function returns a `networkx.MultiDiGraph`. 
```
nx_graph = spot.translate("(p1 W 0) | Gp2")
```

**Note:** The returned digraph contains an extra node, named `I`. This is **not** a node of automaton. It's a dummy node to represent `initial` state. 

**Note:** The node and edge attributes of `nx_graph` contains information like name, visibility etc. 



## Tips

1. The ZMQ client wait time for receiveing server response is set using `SpotClient.client_wait_time` variable. For larger LTL formulas, if connection is dropping, try increasing the wait time (default is 2 seconds). 