#!/usr/bin/env python3
import ipaddress
from scapy.layers.inet import traceroute
import tkinter as tk
import networkx as nx
import matplotlib.pyplot as plt


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_form()

    def create_form(self):
        self.formFrame = tk.Frame(self)
        self.formFrame.pack()
        self.IPLabel = tk.Label(self.formFrame, text='IP')
        self.IPLabel.grid(row=0, column=0)
        self.IPEntry = tk.Entry(self.formFrame)
        self.IPEntry.grid(row=0, column=1)
        self.MaskLabel = tk.Label(self.formFrame, text='Mask')
        self.MaskLabel.grid(row=0, column=2)
        self.MaskEntry = tk.Entry(self.formFrame)
        self.MaskEntry.grid(row=0, column=3)
        self.topologyButtonText = tk.StringVar()
        self.topologyButtonText.set('Show topology')
        self.topologyButton = tk.Button(self, textvariable=self.topologyButtonText, command=self.get_topology)
        self.topologyButton.pack()

    def cleanup_figure(self):
        if hasattr(self, 'fig'):
            plt.close(self.fig)
        self.fig = plt.figure(figsize=(8, 6), dpi=100)

    def get_topology(self):
        self.cleanup_figure()
        self.generate_figure()
        plt.show(block=False)

    def generate_figure(self):
        edges = self.trace_route()
        network_graph = nx.Graph()
        network_graph.add_edges_from(edges)
        node_size = [float(network_graph.degree(v))*50 for v in network_graph]
        node_color = [1-1/(1+float(network_graph.degree(v))) for v in network_graph]
        nx.draw(network_graph, node_size=node_size, node_color=node_color, width=0.5, with_labels=True)

    def trace_route(self):
        edges = set()
        try:
            network = list(ipaddress.IPv4Network(self.IPEntry.get() + '/' + self.MaskEntry.get()))

            res, _ = traceroute(list(map(lambda x: str(x), network)))
            if not hasattr(self, 'res'):
                self.res = res
            else:
                self.res = self.res + res

            tr_dict = dict()
            help_dict = dict()

            for r in self.res:
                if r[0].dst in tr_dict:
                    if r[1].src in help_dict[r[0].dst]:
                        continue
                    tr_dict[r[0].dst][r[0].ttl] = r[1].src
                    help_dict[r[0].dst].add(r[1].src)
                else:
                    tr_dict[r[0].dst] = {r[0].ttl: r[1].src}
                    help_dict[r[0].dst] = {r[1].src}

            for ttl_dict in tr_dict.values():
                last_src = 'localhost'
                for ttl in sorted(ttl_dict.keys()):
                    edges.add((last_src, ttl_dict[ttl]))
                    last_src = ttl_dict[ttl]

        except Exception as e:
            print(e)
            edges.add(('localhost', 'localhost'))

        return edges


if __name__ == '__main__':
    app = Application(master=tk.Tk())
    app.master.title('Network Topology Viewer')
    app.mainloop()
