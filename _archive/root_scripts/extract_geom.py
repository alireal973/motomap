with open('api/services/route_preview.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_coords = '''                        path_nodes = res["secilen_rota"]["nodes"]
                        coords = [{"lat": graph.nodes[n]['y'], "lng": graph.nodes[n]['x']} for n in path_nodes]'''

new_coords = '''                        path_nodes = res["secilen_rota"]["nodes"]
                        coords = []
                        for i in range(len(path_nodes)-1):
                            u = path_nodes[i]
                            v = path_nodes[i+1]
                            edge_data = graph.get_edge_data(u, v)
                            # Get the best edge (shortest) if parallel edges exist
                            best_edge = min(edge_data.values(), key=lambda e: e.get('length', float('inf')))
                            
                            if i == 0:
                                coords.append({"lat": graph.nodes[u]['y'], "lng": graph.nodes[u]['x']})
                                
                            if 'geometry' in best_edge:
                                for lon, lat in best_edge['geometry'].coords:
                                    coords.append({"lat": lat, "lng": lon})
                            else:
                                coords.append({"lat": graph.nodes[v]['y'], "lng": graph.nodes[v]['x']})
                                
                        if not coords and path_nodes:
                            coords = [{"lat": graph.nodes[n]['y'], "lng": graph.nodes[n]['x']} for n in path_nodes]'''

text = text.replace(old_coords, new_coords)

with open('api/services/route_preview.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated route_preview.py to use edge geometries")
