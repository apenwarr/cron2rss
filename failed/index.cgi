#!/bin/sh
export QUERY_STRING="q=failed"
cd .. && exec ./index.cgi "$@"
