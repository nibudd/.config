alias dad="curl -H 'Accept: application/json' https://icanhazdadjoke.com/ | jq '.joke'"
update() {
  echo '> brew update'   && brew update   && \
  echo '> brew upgrade --no-ask'  && brew upgrade --no-ask  && \
  echo '> claude update' && claude update && \
  echo '> gcloud components update' && gcloud components update
  echo '> gcloud components update-macos-python' && gcloud components update-macos-python
}
gauth() {
  echo '> gcloud auth application-default' && gcloud auth application-default login && \
  echo '> gcloud auth login' && gcloud auth login
}

