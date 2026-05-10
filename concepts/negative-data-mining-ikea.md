---
title: Negative Data Mining for Dense Retrieval at IKEA
created: 2026-05-05
updated: 2026-05-05
type: concept
tags:
- retrieval
- embedding
- training
- benchmark
- recommendation
sources:
- raw/papers/2026/05/2605.00353.md
---

# Negative Data Mining for Contrastive Learning in Dense Retrieval at IKEA.com

## Core Problem Definition

Contrastive learning is a core component of modern dense retrieval systems, but its effectiveness heavily relies on the quality of **negative examples** used during training. While hard negative mining (HNM) consistently improves offline metrics, a fundamental question remains: **do offline gains translate to improved user experiences and business outcomes?**

**Research Questions**:
- **RQ1**: How do different hard negative mining strategies affect dense retrieval performance for product search?
- **RQ2**: What factors contribute to the generalization gap between synthetic and real user queries?
- **RQ3**: How do offline retrieval metrics correlate with online user engagement and purchase intent?

**Formal Statement**: Given a query q, document collection D, and contrastive loss L, hard negative mining selects negatives N_hard ⊂ D that are semantically similar to q but irrelevant, as opposed to random negatives N_random. The question is whether the offline metric improvement Δ_offline(N_hard) predicts online metric improvement Δ_online(N_hard).

## Method: Structured Negative Sampling + LLM Relevance Evaluation

### Training Data Generation Pipeline

**Stage 1: Category Feature Extraction**
- LLM extracts category-specific attributes from product catalog (373 leaf categories)
- For each category: sample products with names, descriptions, common search terms, metadata
- LLM identifies visual (colors), material, size, activity-based, and user-need attributes
- Ensures category-appropriate attributes (e.g., "solid wood" for furniture, not textiles)

**Stage 2: Synthetic Query Generation**
- LLM generates 50 search queries per category across complexity tiers:
  - Simple (30%): 1-2 words (e.g., "grey sofa")
  - Medium (35%): 3-4 words combining attributes (e.g., "grey velvet corner sofa")
  - Complex (35%): 5+ words (e.g., "small grey corner sofa bed with storage")
- Also generates intent-based: activity-based, situational, product-name queries
- Total: 6,300 unique queries

**Stage 3: Training Dataset Labeling**
- LLM scores query-product relevance on 1-5 scale
- Positives: score ≥ 4; Negatives: score ≤ 2; Score 3 excluded for clear separation
- Produces 448,073 triplets classified into:
  - **Attribute-only** (244K): Same category, different attribute (e.g., query "white sofa", negative is black sofa)
  - **Cross-category** (105K): Matching attribute, wrong category (e.g., query "white sofa", negative is white table)
  - **Multi-attribute** (93K): Queries with multiple attributes where each negative violates exactly one

### Data Mixtures

| Mixture | Triplets | Description |
|---------|----------|-------------|
| Baseline | 7.2M | Random negative sampling |
| HNM | 7.9M | Baseline + 448K LLM-labeled hard negatives |
| HNM + QE | 8.3M | HNM + 450K query expansion triplets |
| HNM + QE Full | 8.8M | HNM + QE + 897K exhaustive expansion |

### Model Architecture

Late-interaction retrieval model (ColBERT-style):

```
S(q,d) = Σ_{i∈|E_q|} max_{j∈|E_d|} E_{q_i} · E_{d_j}^T
```

where E_q and E_d are contextualized token embeddings for query and document.

### Training Configuration

- Learning rate: 3 × 10^{-6}
- Batch size: 32
- Max document length: 512 tokens
- Max training steps: 500,000 with early stopping on validation loss
- Hardware: NVIDIA A100 GPUs, ~18 hours per configuration
- Statistical robustness: 5 random seeds per configuration, report mean ± std

### Evaluation Framework

**Synthetic Query Benchmark**: 70 LLM-generated evaluation queries (held-out categories), stratified by complexity
**Real Query Benchmark**: 100 queries from production search logs (35 single-attribute, 35 multi-attribute, 30 product-name)
**Online A/B Test**: 2-week production deployment, 50/50 traffic split, focused on long-tail queries (≥3 words)

**Category Accuracy@K (Cat@K)**:
```
Cat@K = |{p ∈ Retrieved@K : cat(p) ∈ C_q}| / K
```
where C_q is the set of leaf categories from relevant ground truth products.

## Experimental Results

### Offline Evaluation

| Model | Synthetic R@10 | Synthetic Cat@10 | Synthetic Cat@50 | Real R@10 | Real Cat@10 | Real Cat@50 |
|-------|---------------|-----------------|-----------------|-----------|------------|------------|
| Baseline | 44.9±0.1 | 76.5±0.6 | 47.5±0.1 | 41.2±0.9 | 73.4±0.4 | 62.1±0.4 |
| +HNM | 49.1±0.4 | 80.8±0.3 | 48.7±0.2 | 41.2±0.4 | 76.0±0.7 | 64.6±0.3 |
| +HNM+QE | 48.2±0.5 | 79.8±1.0 | 48.1±0.5 | 38.3±0.9 | 76.0±1.0 | 64.2±0.3 |
| +HNM+QE Full | 47.6±0.4 | 79.8±0.4 | 48.9±0.5 | 39.8±0.9 | 74.1±0.7 | 63.6±0.3 |

**Key findings**:
1. HNM improves Cat@10 by +4.3% on synthetic queries but R@10 on real queries remains unchanged
2. QE variants **do not outperform HNM** despite 900K more triplets — data quality > data quantity
3. Real queries span **7x more categories** than synthetic (12.5 vs 1.7), explaining the generalization gap

### Online A/B Test Results

**No statistically significant differences** between HNM and baseline across all user engagement metrics (click-through rate, add-to-cart rate, search interaction rate; p > 0.05).

The +2.6% average category accuracy improvement observed offline **did not translate to measurable changes in user behavior**.

### User Behavior Analysis Explaining the Gap

- 44.7% of queries are broad category searches where baseline already performs well
- **67% of popular searches exhibit zero-click rates above 50%** — users frequently satisfy needs from search results page without clicking
- When majority of sessions end without clicks regardless of ranking quality, retrieval improvements have limited room to influence engagement metrics
- Long-tail query restriction (≥3 words) limited statistical power

## Comparison with Related Work

| Study | Offline Gain | Online Gain | Key Finding |
|-------|-------------|-------------|-------------|
| Amazon (Wang et al. 2023) | Various | Up to 97% directional agreement | NDCG discriminative power >99% |
| AliExpress (Huzhang et al. 2021) | Yes | Inconsistent | Context effects matter |
| Walmart (Lin et al. 2024) | Yes | Needed extra relevance filtering | False positives invisible offline |
| **IKEA (this work)** | **+2.6% Cat@10** | **None (p>0.05)** | **Zero-click behavior explains gap** |

## Critical Analysis

### Strengths
1. **Honest reporting of negative results**: The A/B test showed no improvement, and the paper thoroughly explains why — this is valuable for the community
2. **Rigorous three-stage evaluation**: Synthetic → Real → Online provides a complete picture
3. **Quantified the zero-click problem**: 67% zero-click rate on popular searches is a critical insight for e-commerce search
4. **Identified the intent breadth gap**: Real queries span 7x more categories than synthetic — this explains why HNM on narrow synthetic queries doesn't generalize
5. **Data quality > quantity finding**: HNM+QE Full (8.8M) underperforms HNM (7.9M), a clear demonstration that more data isn't always better

### Weaknesses / Questions
1. **LLM label quality**: Ground truth is LLM-generated (1-5 scale), validated by 93% human agreement. But LLM labels may have systematic biases (leniency) that affect both training and evaluation.
2. **Limited online test scope**: Only long-tail queries (≥3 words), 2-week duration. Short-head queries where most revenue occurs were excluded.
3. **Single market**: Only Canada market tested. Cross-market generalization unknown.
4. **No interleaving experiment**: Standard A/B tests lack sensitivity for ranking improvements compared to interleaving (Bi et al. 2022).
5. **Single architecture**: Only late-interaction model tested. Results may not generalize to bi-encoder or cross-encoder architectures.
6. **No analysis of position bias**: Offline evaluation ignores position bias which is known to affect online metrics.

### Implications for Our Work
- The **offline-online gap** is a critical lesson: improving embedding quality in isolation may not improve end-user metrics
- **Zero-click behavior** means click-based metrics are insufficient — need alternative signals (scroll depth, wishlist, filter interactions)
- The **intent breadth gap** (synthetic vs real queries) suggests training data should match the actual query distribution
- For [[retrieval]] systems, this work is a cautionary tale: always validate offline improvements with online experiments
- The **structured negative sampling** approach (taxonomy-aware) is sound but needs to be paired with real-query distribution matching

## Related

- [[retrieval]] — Dense retrieval methods
- [[embedding]] — Embedding models for search
- [[training]] — Training methodologies for retrieval
