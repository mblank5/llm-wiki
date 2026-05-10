---
title: 'Tachiom: Efficient Multivector Retrieval with Token-Aware Clustering'
created: 2026-05-05
updated: 2026-05-05
type: concept
tags:
- retrieval
- embedding
- architecture
- inference
sources:
- raw/papers/2026/04/2604.28142.md
---

# Tachiom: Efficient Multivector Retrieval

## Core Problem Definition

**Formal Statement.** Multivector retrieval models (e.g., ColBERT) represent documents as sets of token-level embeddings $\{x_{d,1}, \dots, x_{d,n_d}\} \subset \mathbb{R}^d$. Relevance is computed via late interaction (MaxSim):

$$S(q, d) = \sum_{i=1}^{n_q} \max_{j \in [n_d]} \text{sim}(q_i, d_j)$$

The storage and computation cost of these token vectors is prohibitive at scale. State-of-the-art solutions use $\kappa$-means clustering to compress token vectors into centroids + residuals, but $\kappa$-means has two critical flaws:
1. **Scalability**: $O(I \cdot N \cdot \kappa \cdot d)$ per iteration — becomes intractable for millions of centroids on billions of vectors
2. **Token-blind**: Treats all vectors equally, so frequent tokens (stopwords) dominate the WCSS loss, starving rare but discriminative tokens of centroid representation

**Question:** Can we design a clustering algorithm that (a) scales to millions of centroids and (b) allocates centroids based on token importance?

## Method

### Token-Aware Clustering (Tac)

**Key observation.** Multivector collections exhibit strong correlation between token type and embedding distribution. On Ms Marco-v1, the top 100 most frequent tokens account for 41% of all vectors. Standard $\kappa$-means allocates centroids proportional to frequency, so common tokens get most centroids while rare domain-specific tokens (most discriminative for retrieval) get minimal representation.

**Tac's solution.** Decompose the global clustering problem into independent per-token subproblems with non-uniform centroid allocation.

**Four-stage pipeline:**

**Phase 1: Tail Handling.** Isolate very rare tokens (frequency < threshold $\mu=128$) to prevent complete marginalization.

**Phase 2: Damped Scoring.** Compute allocation weight for each token $j$:
$$w_j = f_j^{\alpha} \cdot v_j$$
where $f_j$ is the token frequency (with square-root damping, $\alpha=0.5$), and $v_j$ is the semantic variance. Damping suppresses the dominance of high-frequency tokens.

**Phase 3: Bounding.** Enforce:
- Hard floor: $\kappa_j \geq \varepsilon=4$ (minimum representation for all active tokens)
- Upper bound: $n_j / \kappa_j \geq \theta=39$ (at least $\theta$ vectors per centroid on average)

**Phase 4: Budget Reconciliation.** Redistribute surplus/deficit to exactly match global budget $\kappa$.

**Final step:** Perform independent $\kappa_j$-means clustering for each token $j$ with its assigned $\kappa_j$ centroids.

### Theoretical Speedup

Standard $\kappa$-means: $O(I \cdot N \cdot \kappa \cdot d)$ for $I$ iterations over $N$ vectors.

Tac: $O(I \cdot \sum_{j=1}^{N_T} n_j \cdot \kappa_j \cdot d)$ where $N_T$ is the number of distinct tokens.

The speedup is lower-bounded by:
$$\text{Speedup} \geq \frac{\sum_{j=1}^{N_T} w_j}{\max_{j=1}^{N_T} w_j}$$

This is the ratio of total weight to maximum single-token weight. With square-root damping, the maximum weight is strictly reduced, guaranteeing substantial speedup. Since cumulative vocabulary weight vastly exceeds any single token's weight, the speedup is significant.

### Residual Compression

After clustering, residuals (difference between token vector and assigned centroid) are compressed using **Product Quantization (PQ)** with $M=32$ subspaces and 8-bit codes per subspace. Residuals are normalized before compression since Tac's non-uniform allocation produces heterogeneous residual magnitudes.

### Tachiom Retrieval Architecture

Combines Tac clustering with a two-phase retrieval system:

**Phase 1: HNSW Graph-Based Gathering.**
- Build an HNSW proximity graph over centroids ($M=32$ neighbors, $ef_c=1500$)
- For query $q$ with tokens $\{q_1, \ldots, q_{n_q}\}$, find nearest centroids for each query token
- Approximate MaxSim score using only centroid-level interactions:
$$\tilde{S}(q, d) = \sum_{i=1}^{n_q} \tilde{s}_i(d)$$
- Truncate to top $\kappa_d$ documents using partial scores
- Apply Candidates Pruning (CP) with parameter $\alpha$

**Phase 2: PQ-Optimized Refine.**
- For pruned candidates, compute full MaxSim using centroids + PQ-compressed residuals
- Cache-optimized document layout: all centroid IDs stored contiguously, followed by all PQ codes
- SIMD-vectorized distance table computation

## Training Configuration

| Parameter | Value |
|-----------|-------|
| Implementation | Rust 1.92.0-nightly |
| Library | kANNolo |
| Hardware | Intel Xeon Silver 4314 @ 2.40GHz, 64 threads |
| Clustering iterations | 10 |
| Tail threshold $\mu$ | 128 |
| Tail cap $\tau$ | 256 |
| Min centroids $\varepsilon$ | 4 |
| Vectors/centroid $\theta$ | 39 |
| PQ subspaces | 32 |
| PQ bits per subspace | 8 |
| HNSW neighbors $M$ | 32 |
| HNSW $ef_c$ | 1500 |

## Experimental Results

### Datasets
- **Ms Marco-v1**: 2.4M passages, 266M token vectors, 2,931 queries
- **LoTTE**: Out-of-domain evaluation

### Clustering Speed (Figure 2)

| Method | 262K centroids | 4M centroids |
|--------|----------------|--------------|
| Faiss (MKL) | timeout (>24h for 131K) | — |
| Faiss (AVX2) | timeout (>24h for 131K) | — |
| FastKMeans-rs | timeout (>24h for 131K) | — |
| **Tac** | **8 minutes** | **102 minutes** |

**Speedup over $\kappa$-means:**
- Up to 84x vs. Faiss with MKL
- Up to 247x vs. Faiss (AVX2)
- Up to 230x vs. FastKMeans-rs

### Clustering Quality (MRR@10 on Ms Marco-v1, Figure 2 top)

At every centroid budget, Tac achieves equal or superior MRR@10 compared to $\kappa$-means, despite being dramatically faster. This validates that token-aware allocation improves centroid quality for retrieval.

### End-to-End Retrieval (Table/Figure 3)

**Centroid budgets:** LoTTE: ~2M centroids ($2^{21}$); Ms Marco: ~4M centroids ($2^{22}$)

**Search parameters:** $\kappa_c \in \{15,20,40,80,100,120\}$, $\kappa_d \in \{250,500,1000,2000,4000\}$, $\alpha \in \{0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70\}$

Tachiom achieves up to **9.8x faster end-to-end retrieval** compared to state-of-the-art systems (EMVB, Warp, IGP) while maintaining comparable or superior effectiveness (MRR@10 / Success@5).

## Comparison with Existing Systems

| System | Clustering | Gathering | Refine | Speedup vs. ColBERTv2 |
|--------|-----------|-----------|--------|----------------------|
| ColBERTv2 | $\kappa$-means | Inverted lists | Full residuals | 1x |
| Plaid | $\kappa$-means | Centroid interaction | PQ | ~3x |
| EMVB | $\kappa$-means | Bitvector prefilter | Optimized PQ | ~5x |
| Warp | $\kappa$-means | Centroid interaction + XTR | PQ | ~6x |
| IGP | $\kappa$-means | Graph over centroids | PQ | ~7x |
| **Tachiom** | **Tac (token-aware)** | **HNSW over centroids** | **Cache-optimized PQ** | **up to 9.8x** |

## Critical Analysis

### Strengths
1. **Massive speedup**: 247x faster clustering is not incremental — it fundamentally changes what's possible (millions of centroids in minutes)
2. **Theoretical grounding**: The speedup lower-bound proof is clean and insightful
3. **Token-aware design**: The frequency-weighted allocation directly addresses a real problem in multivector retrieval
4. **Open source**: Released on GitHub (https://github.com/TusKANNy/tachiom)
5. **End-to-end system**: Not just clustering — the full Tachiom architecture with HNSW + optimized PQ is practical

### Weaknesses and Open Questions
1. **Ms Marco-centric**: Primary evaluation on Ms Marco-v1; LoTTE evaluation is more limited. Need more diverse domain evaluation
2. **Fixed vocabulary assumption**: Tac relies on token identity, which assumes a fixed tokenizer. May not generalize to subword tokenizers with large vocabularies as well
3. **WCSS optimality gap**: Independent per-token clustering cannot capture cross-token relationships. The paper shows this doesn't hurt retrieval quality, but theoretical analysis is limited
4. **Comparison fairness**: Some competitors (EMVB, Warp) use different PQ variants; the speedup numbers may reflect implementation quality as much as algorithmic advantage
5. **Memory overhead of HNSW**: The graph index adds memory overhead not fully accounted for in the efficiency analysis
6. **Scalability to billion-scale**: Evaluated on 266M vectors; real-world systems may have billions

### Implications for Our Work
- **For [[retrieval]] systems**: Tachiom's approach could dramatically reduce the cost of multivector retrieval in RAG pipelines
- **For [[embedding]] research**: Demonstrates that token-level structure can be exploited for efficiency gains
- **For [[inference]] optimization**: The centroid-only gathering phase idea is analogous to early-exit strategies — cheap approximation first, expensive computation only for promising candidates
- **Practical consideration**: The Rust implementation and open-source release make this immediately deployable

## Related
- [[embedding]] — Text embedding methods and representations
- [[retrieval]] — Information retrieval paradigms
- [[inference]] — Inference optimization techniques
- [[qdrant-vector-search]] — Vector similarity search for RAG
