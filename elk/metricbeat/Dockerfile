ARG ELK_VERSION

# https://www.docker.elastic.co/
FROM docker.elastic.co/beats/metricbeat:${ELK_VERSION}

# NOTE: поменяйте, если меняете docker-compose.yml
ENV setup.kibana.host=kibana:5601
ENV output.elasticsearch.hosts=["elasticsearch:9200"]
ENV output.elasticsearch.username=["elastic"]
ENV output.elasticsearch.password=["changeme"]
