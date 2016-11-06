for o in {1..100000}; do
    for i in {1..10}; do
        http localhost:5000/users
        http localhost:5000/basegoods
        http localhost:5000/producables
        http localhost:5000/users/$i/inventory
        http localhost:5000/users/$i/buildqueue
        http PUT localhost:5000/producables/$i action=buy
        http PUT localhost:5000/producables/$i action=produce
        http PUT localhost:5000/producables/$i action=sell
        http PUT localhost:5000/basegoods/$i action=sell
        http PUT localhost:5000/basegoods/$i action=buy
    done
    echo "run $o"
done
