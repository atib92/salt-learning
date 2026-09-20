worker_demo:
  file.managed:
    - name: /tmp/worker.txt
    - contents: |
        This machine is a Salt-managed worker.