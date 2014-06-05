# fish completion for svgplease

function __fish_svgplease_arguments
  set args (commandline -opc)
  set -e args[1]
  for i in (seq 1 (count $args)) 
      echo $args[$i]
  end
end

complete -f -c 'svgplease' -a '(svgplease --complete (__fish_svgplease_arguments))'
