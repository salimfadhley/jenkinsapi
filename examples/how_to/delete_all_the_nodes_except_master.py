import logging
logging.basicConfig()

from jenkinsapi.jenkins import Jenkins

j = Jenkins('http://localhost:8080')

for node_id, _ in j.get_nodes().iteritems():
    if not node_id == 'master':
        print(node_id)
        j.delete_node(node_id)

# Alternative way - this method will not delete 'master'
for node in j.nodes.keys():
    del j.nodes[node]
