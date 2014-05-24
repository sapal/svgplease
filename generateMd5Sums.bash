#!/bin/bash
cd deb
:>DEBIAN/md5sums
find usr -type f | while read file ; do
	md5sum "$file" >> DEBIAN/md5sums
done
cd ..
