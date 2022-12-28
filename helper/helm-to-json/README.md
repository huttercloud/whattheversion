# helm-to-json

static go binary to download helm index.yaml and return it as json.
the binary was used ad interim as the pyyaml BaseLoader is very slow and takes 30+ seconds to parse
bigger index.yaml files!

As the parsing of the index.yaml is now moved to a dedicated event driven lambda the slowness doesnt matter
as the timeout is not limited to 30-60 seconds but the lambda can now run up to 15minutes in the background!


***TL;DR; the binary isnt used anymore!***