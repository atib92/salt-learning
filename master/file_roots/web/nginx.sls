nginx:
  pkg.installed: []

nginx_config:
  file.managed:
    - name: /etc/nginx/sites-available/salt-learning
    - source: salt://web/nginx.conf.jinja
    - template: jinja
    - require:
      - pkg: nginx

nginx_config_enabled:
  file.symlink:
    - name: /etc/nginx/sites-enabled/salt-learning
    - target: /etc/nginx/sites-available/salt-learning
    - require:
      - file: nginx_config

nginx_service:
  service.running:
    - name: nginx
    - enable: True
    - require:
      - pkg: nginx
    - watch:
      - file: nginx_config