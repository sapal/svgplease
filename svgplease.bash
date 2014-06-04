_svgplease() {
  COMPREPLY=( $(compgen -W "$(svgplease --complete ${COMP_WORDS[@]:1})" -- "${COMP_WORDS[COMP_CWORD]}") )
}
complete -F _svgplease svgplease
