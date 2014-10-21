#!/usr/bin/env python3

"Rewritten from scratch."

import os
import sys

def main(argv):
    dirname = argv[-1]
    contents = list(os.walk(dirname))
    text = """<!DOCTYPE RCC><RCC version="1.0">
<qresource>
%s
</qresource>
</RCC>"""
    l = []
    for subdir in contents:
        for j in subdir[-1]:
            l.append("    <file>" + os.path.join(subdir[0], j) + "</file>")
    f = open(dirname + ".qrc", "w")
    f.write(text % ("\n".join(l),))
    f.close()

if __name__ == "__main__":
    main(sys.argv)
