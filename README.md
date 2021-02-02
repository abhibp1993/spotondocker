# SpotOnDocker

**SpotOnDocker** is a utility which exposes *some* of [spot's](spot.lrde.epita.fr) functions as a dockerized service. The functions can be called using client API provided in C++, Python, VB.NET and C#.

Note: In v0.1.0, only Python client API is available. 


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


### Python Client Setup

The following packages are required. 
- networkx
- docker
- thrift (Apache)

```
pip3 install docker networkx thrift
pip3 install spotondocker
```

    
## Example (Python Client API)

It is advisable to check if spot is available on system, if not use spotondocker. 
```python
try:
    import spot
except ImportError:
    import spotondocker.client as client
    spot = client.SpotOnDockerClient()
```

`SpotOnDockerClient()` creates a docker container and sets up the server to send requests to

Call the spot functions (only the supported ones!) as usual. For example, to get the class of formula `G(a -> Fb)` in Manna Pnueli hierarchy, we can call
```
spot.mp_class('G(a -> Fb)')
```
which will return a verbose like `safety`, `guarantee`, ... 


In case of translation, the `SpotClient.translate(..)` function returns a `networkx.MultiDiGraph`. 
```
nx_graph = spot.translate("(p1 W 0) | Gp2")
```

The returned graph has several graph properties. See `spotondocker.thrift` to see a list of properties associated with graph. 
The node and edge attributes of `nx_graph` contains information like `id` and `label`.

