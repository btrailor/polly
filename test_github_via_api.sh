#!/bin/bash

echo "Testing GitHub repository query via API..."
echo ""

curl -X POST http://localhost:11436/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What GitHub repositories do you see?",
    "conversation_id": "test-github-debug",
    "use_rag": true
  }' | jq .

echo ""
echo "Check the server console output for debug logs showing:"
echo "  - GitHub document count in filtered_search_results"
echo "  - Sample of rag_context content"
