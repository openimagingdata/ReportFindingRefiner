ollama serve &
server_pid=$!
sleep 5

echo "Pulling llama3.2"
ollama pull llama3.2
pull_status=$?


if [ $pull_status -eq 0 ]; then
    echo "Model pull completed successfully"
    # Run the test script
    uv run scripts/test_ollama.py
else
    echo "Model pull failed"
    exit 1
fi

# Kill the server after test completes
kill $server_pid