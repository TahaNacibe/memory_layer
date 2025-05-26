import datetime


def filter_with_fallback(ids, distances, threshold=1.65, fallback_k=5):
    filtered = [(i, d) for i, d in zip(ids, distances) if d < threshold]
    if filtered:
        return [i for i, _ in filtered]
    # fallback to top-k
    return [i for i, _ in sorted(zip(ids, distances), key=lambda x: x[1])[:fallback_k]]


def calculate_score(memory):
    attachment = memory[3]  # e.g. float
    weight = memory[4]          # e.g. float
    last_used = datetime.datetime.fromisoformat(memory[5])
    recency = (datetime.datetime.now() - last_used).total_seconds()

    # Lower recency is better (more recent), so we can use negative weight
    score = (attachment * 0.5) + (weight * 0.3) - (recency * 0.0001)
    return score

def second_level_filtering(memories):
    sorted_memories = sorted(memories, key=calculate_score, reverse=True)
    return sorted_memories