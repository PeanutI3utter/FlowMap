import networkx as nx


#this is based on the assumption that the order of incoming edges always coincides with
#the order of the input variables in the onSet of a LUT
def merge_LUTs(subgraph: nx.DiGraph, graph: nx.DiGraph, k: int) -> nx.DiGraph: #k probably not needed
    nodes = list(nx.topological_sort(subgraph))
    #make list from set
    inputs = list({node for node in graph.nodes if graph.out_edges(node)[1] in nodes})

    onSets = nx.get_node_attributes(nodes, "onSet")
    extendedOnSets = []

    for node in range(len(nodes)):
        if len(list(subgraph.predecessors(nodes[node]))) == 0:
            onSet = onSets[node]
            incomingEdges = list(graph.in_edges(node, data = False))

            #determine which inputs are connected to the current (upper) LUT
            connectedPositions = [False] * len(inputs)
            for inEdge in incomingEdges:
                position = inputs.index(inEdge[1])
                connectedPositions[position] = True
            #extend truth table/onSet with DC based on connected positions
            newOnSet = []
            for cube in onSet:
                newCube = []
                offset = 0
                for i in range(len(inputs)):
                    if connectedPositions[i]:
                        #keep old cube value (which is at i - offset)
                        newCube.append(cube[i - offset])
                    else:
                        #add new DC value
                        newCube.append(inSymbol.DC)
                        offset += 1
                newOnSet.append(newCube)
            extendedOnSets.append(newOnSet)
            
            
    #merge the extendedOnSets based on onSet of lower LUT
    #todo: check if the order of inputs in the lower onSet is the same as the node order, otherwise use edges
    #to get the correct order and reorder the elements of extendedOnSets accordingly
    lowerOnSet = onSets[nodes[-1]]
    width = len(lowerOnSet[0]) 
    for cube in lowerOnSet:
        mergeOnSets(extendedOnSets, cube)

def mergeOnSets(onSets, cube):
    return
    
                
