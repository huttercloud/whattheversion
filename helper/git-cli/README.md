# git-cli

The git event lambda requires the git binary installed.
To achieve this a lambda layer is required. The Dockerfile installs git and
collects the binary and all its libraries into a zip which can be distributed as layer.