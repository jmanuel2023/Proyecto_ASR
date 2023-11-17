import networkx as nx
import matplotlib.pyplot as plt
from flask import Flask, send_file
from io import BytesIO
def generar_grafico(topologia):
    # Crear un grafo dirigido
    G = nx.DiGraph()

    # Conjunto para rastrear nodos únicos
    nodos_unicos = set()

    # Agregar enlaces al grafo y nodos únicos
    for dispositivos, conexiones in topologia.items():
        for conexion in conexiones:
            nodo_actual = conexion["Name"]
            # Si el nodo no está en el conjunto, agrégalo al grafo y al conjunto
            if nodo_actual not in nodos_unicos:
                G.add_node(nodo_actual)
                nodos_unicos.add(nodo_actual)
            # Agregar enlace al grafo
            G.add_edge(dispositivos, nodo_actual, link=conexion["Link"])

    # Dibujar el grafo
    pos = nx.shell_layout(G)
    nx.draw(G, pos, with_labels=True, font_weight='bold', node_size=1000, node_color="skyblue", font_size=8, font_color="black")

    # Agregar etiquetas de enlaces
    labels_enlaces = nx.get_edge_attributes(G, 'link')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels_enlaces, font_color="red")

    # Guardar la imagen en un BytesIO
    img_io = BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    plt.close()

    return img_io