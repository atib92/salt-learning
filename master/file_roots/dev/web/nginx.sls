nginx:
  pkg.installed: []

dev_marker:
  file.managed:
    - name: /etc/salt-learning-environment
    - contents: |
        This machine is managed using the DEV Salt environment.