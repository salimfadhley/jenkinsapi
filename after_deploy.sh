#!/bin/bash

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
  git remote set-url origin https://${GH_TOKEN}@github.com/pycontribs/jenkinsapi > /dev/null 2>&1
}

bump() {
  python bump_version.py
}

commit() {
  git add next_version.txt
  git commit --message "[skip ci] Increment version after release"
}

push() {
  git push origin master
}

setup_git
bump
commit
push
