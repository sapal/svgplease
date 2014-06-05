#!/bin/bash

i=0
cat names | while read name; do
  svgplease open card.svg then select '#name' then change text to "$name" then save to "card-${i}.svg" 
  i="$((i + 1))"
done

svgplease open card-*.svg then tile on a5 page then save to cards.svg
