#!/usr/bin/env bash

cd $1
for f in $(find . -type f -wholename "*/trace.txt");
do
  echo "$f";
  DIR="$(dirname $f)"
  reaction $f -o "$DIR/reaction_times.csv" -c "s.s->s.f->c.s->c.f?a.s->a.f"
done