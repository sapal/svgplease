# fish completion for svgplease

function __fish_svgplease_arguments
  commandline -opc | sed 's/\\\\\([# ]\)/\1/' | sed 's/^[\'"]//' | sed 's/[\'"]$//' 
end

complete -f -c 'svgplease' -a '(svgplease --complete (__fish_svgplease_arguments))'
