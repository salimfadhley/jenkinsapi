from jenkinsapi.jenkins import Jenkins

J = Jenkins("http://localhost:8080")
node = J.get_node('example_node')

jobs = []
label_names = []

for label in node.get_labels():
    label_names.append(label.name)
    # add any jobs associated with the label
    jobs += label.jobs


for index, job in enumerate(jobs):
    # Filter out jobs that are not an exact match to one of a nodes labels
    if not J.get_job(job).get_label_expression() in label_names:
        jobs.pop(index)

print jobs