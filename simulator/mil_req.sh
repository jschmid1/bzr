url=localhost
port=5000
tool=http
for o in {1..100}; do
    for i in {1..5}; do
        ${tool} ${url}:${port}/users
        ${tool} ${url}:${port}/basegoods
        ${tool} ${url}:${port}/producables
        ${tool} ${url}:${port}/users/$i/inventory
        ${tool} ${url}:${port}/users/$i/buildqueue
        ${tool} ${url}:${port}/producables/$i/blueprint
        ${tool} ${url}:${port}/basegoods/$i/capabilities
        ${tool} ${url}:${port}/producables/$i action=buy
        ${tool} ${url}:${port}/producables/$i action=produce
        ${tool} ${url}:${port}/producables/$i action=sell
        ${tool} ${url}:${port}/basegoods/$i action=sell
        ${tool} ${url}:${port}/basegoods/$i action=buy
    done
done
