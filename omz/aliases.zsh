# make a symlink of this file in your zsh custom directory
# ln -s ~/.config/omz/aliases.zsh ~/.oh-my-zsh/custom/aliases.zsh
gs()  { echo '> git status'       && git status; }
gf()  { echo '> git fetch'        && git fetch; }
gp()  { echo '> git push'         && git push; }
gm()  { echo "> git merge $*"     && git merge "$@"; }
gmo() { echo '> git merge origin/main' && git merge origin/main; }
alias dad="curl -H 'Accept: application/json' https://icanhazdadjoke.com/ | jq '.joke'"
update() {
  echo '> brew update'   && brew update   && \
  echo '> brew upgrade --no-ask'  && brew upgrade --no-ask  && \
  echo '> claude update' && claude update && \
  echo '> gcloud components update' && gcloud components update
}

