#!/bin/sh

if [ ! -d "$1" ]; then
	echo Sorry, $0 requires a directory as an argument.
	exit
fi

dir=`hbshelper --realpath "$1"`

hbshelper --cut-filelists `hbshelper --get-files /var/lib/hbs FILELIST`|sed 's:/$::'|sort -u >/tmp/orphseek_all
find "${dir%/}" >/tmp/orphseek_subset
sort /tmp/orphseek_all /tmp/orphseek_subset|uniq -d >/tmp/orphseek_merged
sort /tmp/orphseek_merged /tmp/orphseek_subset|uniq -u
rm /tmp/orphseek_merged /tmp/orphseek_subset /tmp/orphseek_all

