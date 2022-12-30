# whattheversion

REST api to retrieve the latest available versions for git, docker images or helm charts.
See the open api docs for the available endpoints with examples: https://whattheversion.hutter.cloud



## development

### development ports
- http://localhost:4566: localstack dynamodb and eventbridge
- http://localhost:8001: dynamodb web interface
### requirements
- docker and docker-compose
- aws sam

### start local dev environment

```bash
make dev
```
