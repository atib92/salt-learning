app:
  name: salt-learning
  environment: development
  port: 8080

owner:
  name: atib
  team: infrastructure

nginx:
  port: 8080 # Change this from 8080 to ensure that state watches it and makes the changes in the minion.