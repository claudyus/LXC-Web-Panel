from docutils import core
import sys

file_name = sys.argv[1]
source = open(file_name, 'r')

print core.publish_parts(source.read(), writer_name='html')['fragment']

source.close()
