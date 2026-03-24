"""
Test script for NutriSoul RAG Service — Knowledge Retrieval Tests
Run: py test_rag_service.py
"""

import sys
import os
import math
import re
from collections import Counter

# Direct import of the knowledge base (no Django needed)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'user', 'services'))
from rag_knowledge_base import NUTRITION_KNOWLEDGE_BASE


def tokenize(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = text.split()
    stop_words = {
        'the', 'is', 'in', 'a', 'an', 'and', 'or', 'for', 'to', 'of',
        'with', 'on', 'at', 'by', 'it', 'as', 'be', 'are', 'was', 'that',
        'this', 'from', 'can', 'your', 'you', 'but', 'not', 'do', 'if',
        'has', 'have', 'will', 'may', 'all', 'its', 'per', 'also', 'more',
    }
    return [t for t in tokens if len(t) > 1 and t not in stop_words]


def build_index(documents):
    doc_texts = []
    for doc in documents:
        combined = f"{doc['title']} {doc['content']} {' '.join(doc.get('tags', []))}"
        doc_texts.append(combined)

    all_doc_tokens = [tokenize(text) for text in doc_texts]
    num_docs = len(all_doc_tokens)

    df = Counter()
    for tokens in all_doc_tokens:
        for token in set(tokens):
            df[token] += 1

    idf_cache = {term: math.log((num_docs + 1) / (freq + 1)) + 1 for term, freq in df.items()}

    doc_vectors = []
    for tokens in all_doc_tokens:
        tf = Counter(tokens)
        total = len(tokens) if tokens else 1
        vector = {term: (count / total) * idf_cache.get(term, 1.0) for term, count in tf.items()}
        doc_vectors.append(vector)

    return idf_cache, doc_vectors


def cosine_similarity(vec_a, vec_b):
    common = set(vec_a.keys()) & set(vec_b.keys())
    if not common:
        return 0.0
    dot = sum(vec_a[k] * vec_b[k] for k in common)
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def retrieve(query, documents, idf_cache, doc_vectors, top_k=3):
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    tf = Counter(query_tokens)
    total = len(query_tokens)
    query_vector = {term: (count / total) * idf_cache.get(term, 1.0) for term, count in tf.items()}

    query_token_set = set(query_tokens)
    scored = []

    for i, doc_vector in enumerate(doc_vectors):
        score = cosine_similarity(query_vector, doc_vector)
        doc_tags = set(documents[i].get('tags', []))
        tag_overlap = len(query_token_set & doc_tags)
        if tag_overlap > 0:
            score += 0.2 * min(tag_overlap / max(len(doc_tags), 1), 1.0)
        if score > 0.01:
            scored.append((i, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [(documents[i]['title'], round(score, 4)) for i, score in scored[:top_k]]


def run_tests():
    print("=" * 60)
    print("NutriSoul RAG Service - Retrieval Tests")
    print("=" * 60)
    print(f"\nKnowledge base: {len(NUTRITION_KNOWLEDGE_BASE)} documents\n")

    idf_cache, doc_vectors = build_index(NUTRITION_KNOWLEDGE_BASE)

    test_queries = [
        ("How much protein should I eat for muscle gain?", ["Protein"]),
        ("What foods are good for diabetes?", ["Diabetes"]),
        ("How many calories should I eat to lose weight?", ["Calorie Deficit", "Calories"]),
        ("What are good sources of iron?", ["Iron", "Anemia"]),
        ("What should I eat before a workout?", ["Meal Timing", "Post-Workout"]),
        ("I have PCOS, what diet should I follow?", ["PCOS"]),
        ("How much water should I drink daily?", ["Hydration", "Water"]),
        ("What are healthy Indian breakfast options?", ["Indian", "Meal"]),
        ("I can't sleep well, any food suggestions?", ["Sleep"]),
        ("What is the DASH diet?", ["Blood Pressure", "DASH"]),
        ("What supplements should vegetarians take?", ["Supplements", "Vegetarian"]),
        ("How to control cholesterol through diet?", ["Cholesterol", "Heart"]),
    ]

    passed = 0
    total = len(test_queries)

    for query, expected_keywords in test_queries:
        results = retrieve(query, NUTRITION_KNOWLEDGE_BASE, idf_cache, doc_vectors, top_k=3)

        found = False
        for title, score in results:
            for kw in expected_keywords:
                if kw.lower() in title.lower():
                    found = True
                    break
            if found:
                break

        status_icon = "PASS" if found else "FAIL"
        if found:
            passed += 1

        print(f"[{status_icon}] Q: \"{query}\"")
        for title, score in results:
            print(f"       -> {title} (score: {score})")
        print()

    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
