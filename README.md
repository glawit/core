cd glawit
export FLASK_APP=glawit.interface.flask
export AWS_PROFILE=personal AWS_DEFAULT_REGION=eu-central-1
flask run

curl -X POST -u kalrish:0acc99d2d44ea8178cb51371979e214fccc77890 -H 'Accept: application/vnd.git-lfs+json' -H 'Content-Type: application/vnd.git-lfs+json' --data '{"oid": "{oid}", "size": 10000}' http://127.0.0.1:5000/verify
