ps aux | grep "python process_buildqueue.py" | awk '{print $2}' | head -n1 | xargs kill -9
ps aux | grep "python server.py" | awk '{print $2}' | head -n1 | xargs kill -9
