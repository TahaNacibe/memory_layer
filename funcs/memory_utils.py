


def filter_with_fallback(ids, distances, threshold=1.65, fallback_k=5):
    for id in ids:
        print(f"{id} --- {distances}")
    filtered = [(i, d) for i, d in zip(ids, distances) if d < threshold]
    if filtered:
        return [i for i, _ in filtered]
    # fallback to top-k
    print("No close match found. Falling back to top-k.")
    return [i for i, _ in sorted(zip(ids, distances), key=lambda x: x[1])[:fallback_k]]
