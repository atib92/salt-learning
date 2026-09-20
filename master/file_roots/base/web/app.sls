app_directory:
  file.directory:
    - name: /opt/salt-learning

app_info:
  file.managed:
    - name: /opt/salt-learning/info.txt
    - contents: |
        Application: {{ pillar['app']['name'] }}
        Environment: {{ pillar['app']['environment'] }}