""" Increment version """

current = open('./.next_version.txt', 'r').read()
major, minor, release = current.split('.')
next_version = '%s.%s.%s' % (major, minor, int(release) + 1)
open('./.next_version.txt', 'w').write(next_version)
