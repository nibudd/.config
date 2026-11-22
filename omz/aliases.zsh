alias dad="curl -H 'Accept: application/json' https://icanhazdadjoke.com/ | jq '.joke'"
update() {
  if [[ $OSTYPE == darwin* ]]; then
    echo '> brew update'   && brew update   && \
    echo '> brew upgrade --no-ask'  && brew upgrade --no-ask
  else
    echo '> sudo apt update' && sudo apt update && \
    echo '> sudo apt upgrade -y' && sudo apt upgrade -y
  fi && \
  echo '> claude update' && claude update
  if (( $+commands[gcloud] )); then
    echo '> gcloud components update' && gcloud components update
    if [[ $OSTYPE == darwin* ]]; then
      echo '> gcloud components update-macos-python' && gcloud components update-macos-python
    fi
  fi
}
gauth() {
  echo '> gcloud auth application-default' && gcloud auth application-default login && \
  echo '> gcloud auth login' && gcloud auth login
}

