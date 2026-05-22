import time
from app.rag.rag_pipeline import create_rag_pipeline


# -------- Accuracy Metrics -------- #

def precision_at_k(retrieved, relevant, k=3):
    retrieved_k = retrieved[:k]
    return len(set(retrieved_k) & set(relevant)) / k


def recall_at_k(retrieved, relevant, k=3):
    retrieved_k = retrieved[:k]
    return len(set(retrieved_k) & set(relevant)) / len(relevant)


# -------- Evaluation -------- #

def evaluate():
    qa = create_rag_pipeline()

    test_cases = [
        {
            "query": "What is the price?",
            "expected_keywords": ["50", "price"]
        },
        {
            "query": "Where is the parking located?",
            "expected_keywords": ["Bhubaneswar", "location"]
        }
    ]

    for case in test_cases:
        query = case["query"]
        expected = case["expected_keywords"]

        # Measure latency
        start = time.time()
        response = qa.run(query)
        latency = time.time() - start

        # Simulate retrieved keywords (simple approach)
        retrieved = response.lower().split()

        # Calculate metrics
        precision = precision_at_k(retrieved, expected)
        recall = recall_at_k(retrieved, expected)

        print(f"\nQuery: {query}")
        print(f"Response: {response}")
        print(f"Latency: {latency:.3f}s")
        print(f"Precision@K: {precision:.2f}")
        print(f"Recall@K: {recall:.2f}")


if __name__ == "__main__":
    evaluate()