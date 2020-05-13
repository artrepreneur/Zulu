#!/usr/bin/env bash
if test "$0" != "./make_osx.sh"; then
  echo "make_osx.sh needs to be run from the local folder, i.e. ./make_osx.sh"
  exit 1
fi
PKT_OSX_PATH="$(pwd)/scripts/osx"
export PKT_OSX_PATH
if test "x$VERBOSE" != "x"; then
  bash -x "${PKT_OSX_PATH}/make_osx.sh"
else
  bash "${PKT_OSX_PATH}/make_osx.sh"
fi
