alias dad="curl -H 'Accept: application/json' https://icanhazdadjoke.com/ | jq '.joke'"
update() {
  echo '> brew update'   && brew update   && \
  echo '> brew upgrade --no-ask'  && brew upgrade --no-ask  && \
  echo '> claude update' && claude update && \
  echo '> gcloud components update' && gcloud components update
}

