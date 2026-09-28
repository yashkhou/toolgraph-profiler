import json,sys
from .core import parse,analyze,svg
sp=parse(json.load(open(sys.argv[1]))); print(json.dumps(analyze(sp),indent=2)); open('toolgraph.svg','w').write(svg(sp))
