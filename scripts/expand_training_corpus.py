"""
Script to expand training_corpus.py from 20 documents (200 samples)
to 100 documents (1,000 samples) while strictly preserving:
- Original TR_DOC_001 to TR_DOC_020 and TR_Q001 to TR_Q200
- Original VAL_DOC_001 to VAL_DOC_005 and VAL_Q001 to VAL_Q050
- 0% overlap with Phase 3.1 / 3.1.1
- get_training_corpus(max_docs=20) default returning 20 docs / 200 samples for existing tests
- get_scale_training_corpus(max_docs=100) returning up to 100 docs / 1000 samples
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# 80 additional technical documents with 5 factual sentences each and 10 QA pairs each
ADDITIONAL_DOCS = [
    {
        "doc_id": "TR_DOC_021",
        "title": "FlashAttention and IO-Aware Exact Attention",
        "context": (
            "Standard multi-head attention writes intermediate attention matrices of size sequence length squared to high-bandwidth memory. "
            "FlashAttention eliminates these memory transfers by tiling matrix multiplications within fast GPU SRAM. "
            "It computes softmax normalization incrementally using online softmax rescaling without materializing full attention matrices. "
            "In the backward pass, attention matrices are recomputed on the fly from SRAM rather than read from slow HBM. "
            "This IO-aware algorithm achieves substantial wall-clock speedups while computing mathematically exact attention outputs."
        ),
        "qa_pairs": [
            ("Where does standard attention write intermediate matrices?", "to high-bandwidth memory (HBM)"),
            ("How does FlashAttention avoid writing full attention matrices?", "by tiling matrix multiplications within fast GPU SRAM"),
            ("How is softmax normalization computed in FlashAttention?", "incrementally using online softmax rescaling"),
            ("What happens during the FlashAttention backward pass?", "attention matrices are recomputed on the fly from SRAM"),
            ("Are FlashAttention outputs approximate or exact?", "mathematically exact attention outputs"),
            ("What memory tier is utilized for tiling in FlashAttention?", "GPU SRAM"),
            ("Why does recomputing attention in SRAM improve speed?", "it avoids reading large intermediate matrices from slow HBM"),
            ("What mathematical technique enables incremental softmax?", "online softmax rescaling"),
            ("What primary bottleneck does FlashAttention address?", "memory IO between GPU SRAM and HBM"),
            ("What is the computational nature of the FlashAttention algorithm?", "IO-aware exact attention computation"),
        ]
    },
    {
        "doc_id": "TR_DOC_022",
        "title": "Rotary Position Embeddings and Angle Rotations",
        "context": (
            "Rotary Position Embedding (RoPE) encodes relative positional information by rotating query and key representations. "
            "Instead of adding absolute positional vectors, RoPE applies a 2D rotation matrix to paired coordinate dimensions. "
            "The inner product between rotated query and key vectors naturally decays as relative token distance increases. "
            "RoPE exhibits strong length extrapolation properties when fine-tuned with position interpolation techniques. "
            "Modern open-weight architectures universally adopt RoPE over absolute learned positional embeddings."
        ),
        "qa_pairs": [
            ("How does RoPE encode relative positional information?", "by rotating query and key representations"),
            ("What does RoPE apply to paired coordinate dimensions?", "a 2D rotation matrix"),
            ("What happens to query-key inner products as relative token distance increases?", "they naturally decay"),
            ("How can length extrapolation be improved in RoPE models?", "when fine-tuned with position interpolation techniques"),
            ("Do modern open-weight architectures prefer RoPE or absolute embeddings?", "they universally adopt RoPE over absolute embeddings"),
            ("What does RoPE stand for?", "Rotary Position Embedding"),
            ("Does RoPE add vectors to token representations?", "No, it rotates coordinate dimensions instead of additive vectors"),
            ("Which vectors are rotated in self-attention with RoPE?", "query and key representations"),
            ("What property allows models with RoPE to handle longer sequences?", "length extrapolation properties"),
            ("How are dimensions paired in RoPE transformations?", "into 2D coordinate pairs"),
        ]
    },
    {
        "doc_id": "TR_DOC_023",
        "title": "Speculative Decoding and Target Verification",
        "context": (
            "Autoregressive generation is fundamentally memory-bandwidth bound due to loading parameters for each individual token. "
            "Speculative decoding utilizes a lightweight draft model to generate candidate token sequences rapidly. "
            "A larger target language model evaluates all candidate draft tokens concurrently in a single forward pass. "
            "A modified rejection sampling scheme accepts draft tokens that align with the target distribution without altering outputs. "
            "Accepted draft sequences accelerate inference latency by two to three times while preserving exact output distributions."
        ),
        "qa_pairs": [
            ("Why is standard autoregressive generation slow?", "it is fundamentally memory-bandwidth bound due to per-token parameter loading"),
            ("What model generates candidate sequences in speculative decoding?", "a lightweight draft model"),
            ("How does the target model evaluate candidate draft tokens?", "concurrently in a single forward pass"),
            ("What sampling scheme is used to verify draft tokens?", "a modified rejection sampling scheme"),
            ("How much speedup does speculative decoding typically achieve?", "two to three times acceleration"),
            ("Does speculative decoding change the target model's output distribution?", "No, it preserves exact output distributions"),
            ("How many forward passes does the target model execute per draft chunk?", "a single forward pass"),
            ("What condition determines draft token acceptance?", "alignment with the target model distribution via rejection sampling"),
            ("Which component is smaller, draft or target model?", "the draft model is lightweight and smaller"),
            ("What latency metric is improved by speculative decoding?", "autoregressive inference latency"),
        ]
    },
    {
        "doc_id": "TR_DOC_024",
        "title": "Grouped-Query Attention and Memory Bandwidth Savings",
        "context": (
            "Multi-Head Attention maintains independent key and value heads for every individual query attention head. "
            "Multi-Query Attention drastically reduces KV cache size by sharing a single key-value head across all query heads. "
            "Grouped-Query Attention (GQA) interpolates between both extremes by dividing query heads into distinct groups. "
            "Each group of query heads shares a common key and value projection pair during generation. "
            "GQA achieves inference speed and memory footprint close to MQA while retaining the modeling quality of MHA."
        ),
        "qa_pairs": [
            ("What does Multi-Head Attention maintain for each query head?", "independent key and value heads"),
            ("How does Multi-Query Attention minimize KV cache size?", "by sharing a single key-value head across all query heads"),
            ("How does Grouped-Query Attention group query heads?", "by dividing query heads into distinct groups sharing KV projection pairs"),
            ("What does each query group share in GQA?", "a common key and value projection pair"),
            ("How does GQA compare in quality and speed to MHA and MQA?", "retains MHA modeling quality while achieving MQA inference speed and memory footprint"),
            ("What does GQA stand for?", "Grouped-Query Attention"),
            ("What resource footprint is minimized by GQA during inference?", "KV cache memory footprint and bandwidth"),
            ("Is GQA a discrete alternative or an interpolation?", "an interpolation between MHA and MQA"),
            ("Which attention variant has only one KV head across all query heads?", "Multi-Query Attention (MQA)"),
            ("Why is KV cache reduction important for long-sequence serving?", "it alleviates memory bandwidth bottlenecks on GPUs"),
        ]
    },
    {
        "doc_id": "TR_DOC_025",
        "title": "Direct Preference Optimization and Gated Implicit Rewards",
        "context": (
            "Traditional reinforcement learning from human feedback requires fitting a separate reward model and running PPO optimization. "
            "Direct Preference Optimization (DPO) mathematically reparameterizes the reward function directly in terms of model policy probabilities. "
            "This formulation allows optimizing pairwise human preferences using a simple binary cross-entropy objective. "
            "DPO eliminates the training instability and high memory overhead associated with multi-model reinforcement learning loops. "
            "An implicit reference policy prevents the fine-tuned model from drifting excessively far from the base distribution."
        ),
        "qa_pairs": [
            ("What components are required in traditional RLHF that DPO avoids?", "a separate reward model and PPO optimization"),
            ("How does DPO formulate the reward function?", "directly in terms of model policy probabilities"),
            ("What loss function is used in DPO optimization?", "a simple binary cross-entropy objective"),
            ("What instability is eliminated by using DPO?", "training instability and high memory overhead of multi-model RL loops"),
            ("What prevents the fine-tuned model from drifting excessively?", "an implicit reference policy"),
            ("What does DPO stand for?", "Direct Preference Optimization"),
            ("On what type of human feedback data does DPO operate?", "pairwise preference data"),
            ("Does DPO require generating rollout completions during training?", "No, it optimizes directly over pre-collected pairs"),
            ("How is policy drift constrained in the DPO objective?", "via KL regularization relative to the implicit reference policy"),
            ("Why is DPO computationally advantageous over PPO?", "it requires fewer active models in GPU memory"),
        ]
    },
]

# Generate remaining 75 documents programmatically with high technical realism
TOPIC_SPECS = [
    ("TR_DOC_026", "Activation-aware Weight Quantization (AWQ)", "quantization", "AWQ protects salient weights by observing activation magnitudes rather than weight values. Salient channels containing large activation norms are preserved in higher precision. Non-salient weights are quantized to 4-bit integer values without significant perplexity degradation. Per-channel scaling factors minimize quantization error across linear projection layers. AWQ enables running large models on consumer GPUs with minimal latency overhead."),
    ("TR_DOC_027", "FP8 Floating Point Representation in Deep Learning", "numerical formats", "FP8 formats allocate 8 bits into sign, exponent, and mantissa fields for accelerated tensor operations. The E4M3 format provides higher precision suitable for forward pass activations and weights. The E5M2 format offers wider dynamic range essential for gradient backpropagation. Delayed scaling factors adjust tensor scaling dynamically across training iterations. Hardware tensor cores achieve double the compute throughput of FP16 when using FP8 arithmetic."),
    ("TR_DOC_028", "Sliding Window Attention and Local Contexts", "attention mechanisms", "Sliding window attention restricts each token to attend only to a local window of neighboring positions. Higher transformer layers indirectly aggregate distant tokens through stacked receptive field expansion. This local attention pattern reduces self-attention complexity from quadratic to linear with sequence length. Periodic global attention tokens can be added to route long-range cross-window information. Sliding window mechanisms are especially effective in streaming document generation tasks."),
    ("TR_DOC_029", "Mixture of Depths and Dynamic Compute Allocation", "dynamic compute", "Standard transformers allocate identical compute capacity to every token regardless of semantic difficulty. Mixture of Depths dynamically routes tokens to either execute transformer blocks or bypass them via residual connections. A router predicts scalar gating scores that select the top-k tokens eligible for layer computation. Tokens that bypass layer operations maintain their hidden representations unchanged through identity mappings. This selective execution achieves identical downstream performance while reducing floating point operations by half."),
    ("TR_DOC_030", "Multi-Head Latent Attention in DeepSeek Architectures", "attention architectures", "Multi-Head Latent Attention (MLA) compresses key and value heads into low-rank latent vectors. During generation, only compressed latent vectors are stored in the KV cache rather than unprojected heads. Decoupled rotary position embeddings preserve positional sensitivity while enabling aggressive KV rank reduction. At runtime, key and value projections are reconstructed on the fly during attention computation. MLA reduces KV cache memory consumption by over seventy percent compared to standard multi-head attention."),
    ("TR_DOC_031", "Activation Steering and Representation Vectors", "model interpretability", "Activation steering intervenes directly on residual stream vectors during forward model inference. Steering vectors are derived by taking differences between mean activations of contrasting prompt pairs. Adding a positive steering vector induces desired behavioral traits such as truthfulness or domain expertise. Subtracting steering vectors suppresses undesirable behaviors without modifying underlying model weights. This technique provides controllable generation with zero computational overhead at test time."),
    ("TR_DOC_032", "Sparse Autoencoders for Feature Disentanglement", "mechanistic interpretability", "Standard neural network activations exhibit polysemanticity where individual neurons respond to unrelated concepts. Sparse autoencoders reconstruct hidden representations using high-dimensional overcomplete latent spaces. An L1 sparsity penalty enforces that only a tiny fraction of latent features activate for any given input. These extracted dictionary features correspond to interpretable, monosemantic concepts such as specific entities or grammatical patterns. Sparse autoencoders provide fine-grained visibility into transformer internal computation."),
    ("TR_DOC_033", "Representation Engineering and Cognitive Probing", "probing methods", "Representation engineering treats neural activations as readable and editable cognitive state spaces. Linear probes trained on intermediate hidden states accurately predict factual veracity and confidence. Non-linear probes uncover hierarchical semantic taxonomies encoded within deep transformer layers. Interventional probing validates whether detected representations causally drive downstream token generation. These techniques bridge the gap between empirical model behavior and internal circuit analysis."),
    ("TR_DOC_034", "Induction Heads and In-Context Copying Circuits", "transformer circuits", "Induction heads are two-layer attention circuits that implement pattern completion in language models. The first head records the token preceding the current position in the sequence. The second head attends back to historical instances of that token and copies the subsequent completion. The emergence of induction heads coincides with a sharp transition in in-context learning capability. These specialized circuits explain how models perform few-shot adaptation without parameter updates."),
    ("TR_DOC_035", "Chinchilla Compute-Optimal Scaling Laws", "scaling laws", "Original scaling laws suggested allocating compute growth primarily to increasing model parameter count. The Chinchilla formulation demonstrated that model parameters and training tokens should scale in equal proportions. For compute-optimal performance, a model should be trained on approximately twenty tokens per parameter. Many historical models were significantly undertrained relative to their parameter capacity. Modern pretraining regimens emphasize token volume over parameter scale for optimal inference efficiency."),
    ("TR_DOC_036", "MinHash LSH and Pretraining Data Deduplication", "data preprocessing", "Web-scraped pretraining corpora contain massive volumes of redundant and duplicated documents. MinHash Locality-Sensitive Hashing compresses text documents into compact sets of integer hash signatures. Document pairs sharing high Jaccard similarity are clustered into duplicate buckets using banding techniques. Deduplication removes redundant web mirrors, boilerplate templates, and low-quality syndicated content. Training on deduplicated data accelerates convergence and reduces memorization of verbatim text."),
    ("TR_DOC_037", "PagedAttention and Continuous Virtual Memory", "inference serving", "Standard serving systems allocate contiguous physical memory buffers based on maximum sequence lengths. This static allocation results in severe memory fragmentation and wasted GPU VRAM capacity. PagedAttention divides the KV cache into fixed-size blocks mapped through a page table structure. Virtual memory pages are allocated dynamically as generation proceeds without requiring contiguous physical memory. PagedAttention enables near-zero memory waste and supports higher serving throughput through prompt sharing."),
    ("TR_DOC_038", "Contrastive Vision-Language Alignment (CLIP)", "multimodal models", "CLIP trains image and text encoders jointly using symmetric cross-entropy contrastive loss. A batch of image-text pairs produces an NxN cosine similarity matrix across normalized embeddings. The objective maximizes diagonal entry similarities while penalizing off-diagonal negative pairs. The learned multimodal embedding space enables zero-shot classification via natural language text prompts. CLIP representations serve as foundational visual backbones for multimodal generative pipelines."),
    ("TR_DOC_039", "Bi-Encoder vs Cross-Encoder Retrieval Trade-offs", "retrieval architectures", "Bi-encoders encode queries and passages independently into dense vectors for fast inner-product search. Cross-encoders feed query and passage pairs together into full self-attention for joint contextual interaction. Bi-encoders achieve sub-millisecond retrieval latencies across billions of passages using vector index lookups. Cross-encoders achieve significantly higher ranking precision but suffer from prohibitive computational latency. Modern retrieval pipelines combine both by retrieving top candidates with bi-encoders and reranking with cross-encoders."),
    ("TR_DOC_040", "ColBERT Late Interaction Scoring Architecture", "late interaction", "ColBERT preserves token-level embeddings for both queries and passages rather than collapsing into single vectors. It computes relevance via late interaction using a MaxSim operator that sums maximum cosine similarities. Query tokens independently retrieve their best-matching passage token representations in parallel. This design retains the latency benefits of precomputed offline passage indexes. ColBERT significantly outperforms single-vector dense retrieval on complex multi-hop question answering."),
    ("TR_DOC_041", "SPLADE Sparse Lexical Expansion Models", "sparse retrieval", "SPLADE utilizes a masked language model backbone to predict sparse vocabulary term weights. Documents and queries are mapped into high-dimensional sparse vectors indexed via traditional inverted lists. The model learns to perform query expansion and term reweighting end-to-end through contrastive loss. An explicit L1 sparsity regularizer controls the average number of non-zero terms per document vector. SPLADE combines the interpretability and efficiency of inverted indexes with neural semantic generalization."),
    ("TR_DOC_042", "Knowledge Distillation via Logit Matching", "model compression", "Knowledge distillation transfers knowledge from a large teacher model to a compact student network. The student is trained to match the smoothed probability distribution of the teacher across target tokens. A temperature parameter softens output logits to expose rich dark knowledge and inter-class correlations. The training objective linearly combines distillation cross-entropy with standard ground-truth supervised loss. Distilled student models retain high task accuracy while reducing latency and hardware memory footprint."),
    ("TR_DOC_043", "Model Merging via Spherical Linear Interpolation", "model merging", "Model merging combines multiple fine-tuned models derived from a common pretrained base without retraining. Linear weight averaging often degrades performance when parameter trajectories diverge into non-convex valleys. Spherical Linear Interpolation (SLERP) interpolates weights along high-dimensional spherical arcs rather than straight lines. SLERP preserves gradient norms and directional alignment between disparate task expert models. Merged models demonstrate strong multi-task performance without consuming additional compute resources."),
    ("TR_DOC_044", "Task Vectors and Weight Space Arithmetic", "weight arithmetic", "A task vector is computed by subtracting base model weights from task-specific fine-tuned weights. Adding task vectors enables zero-shot multi-task composition across diverse skill domains. Negating a task vector removes specific undesirable capabilities such as toxic language generation. Scaling task vectors with continuous multipliers modulates the intensity of domain-specific behaviors. Weight arithmetic provides modular and reversible model editing without running optimization loops."),
    ("TR_DOC_045", "Test-Time Compute Scaling and Verification Sampling", "reasoning scaling", "Allocating additional compute at inference time improves model performance on complex reasoning tasks. Best-of-N sampling generates multiple independent candidate solutions and ranks them with a verifier. Process-supervised reward models evaluate the correctness of intermediate reasoning steps rather than final answers. Monte Carlo tree search guides token rollouts toward high-probability deductive verification paths. Test-time search exhibits power-law accuracy scaling on challenging mathematical and coding benchmarks."),
    ("TR_DOC_046", "Chain-of-Thought Prompting and Step-by-Step Inference", "prompting methods", "Standard prompting directly maps complex input questions to final answer token distributions. Chain-of-thought prompting elicits intermediate rationales that decompose multi-step problems into sequential deductions. Generating step-by-step reasoning tokens allows transformers to allocate additional working memory via residual states. This mechanism dramatically boosts mathematical accuracy, algorithmic reasoning, and logical deduction. Few-shot exemplars with transparent derivations guide models to structure complex answers systematically."),
    ("TR_DOC_047", "Self-Consistency Decoding over Diverse Reasoning Paths", "decoding strategies", "Greedy decoding on complex reasoning problems frequently commits to early deductive missteps. Self-consistency samples multiple distinct reasoning chains using temperature-based stochastic generation. The final answer is determined by taking a majority vote over all completed derivation paths. This approach effectively marginalizes over diverse reasoning strategies to isolate consensus answers. Self-consistency improves reasoning robustness without requiring external reward models or verifiers."),
    ("TR_DOC_048", "Tree of Thoughts and Deliberate Problem Solving", "tree search", "Tree of Thoughts generalizes chain-of-thought by framing problem solving as search over a thought tree. The model generates multiple candidate next thoughts at each branching decision point. A self-evaluator module scores the promise of each thought branch using heuristic rubrics. Search algorithms like breadth-first search and depth-first search explore and backtrack through candidate trajectories. Tree of Thoughts enables deliberate planning, lookahead, and error recovery on complex puzzle benchmarks."),
    ("TR_DOC_049", "ReAct Framework: Synergizing Reasoning and Acting", "agent architectures", "The ReAct framework alternates between generating verbal reasoning thoughts and executing environment actions. Reasoning thoughts help the model formulate plans, track state changes, and handle exceptions. Actions interface with external APIs such as search engines, calculators, and database query engines. Environmental observations returned by actions are appended back into context for subsequent deductions. This synergy between reasoning and acting mitigates hallucination and produces grounded problem-solving trajectories."),
    ("TR_DOC_050", "Tool Use and Structured Function Calling", "function calling", "Language models can be fine-tuned to emit structured JSON function calls matching schema declarations. When a user query requires external capabilities, the model formats function arguments instead of text. An execution environment invokes the designated tool and returns structured output payloads. The model processes returned tool outputs to synthesize natural language answers for users. Function calling enables language models to act as deterministic orchestrators across complex software systems."),
    ("TR_DOC_051", "Long-Term Episodic Memory Consolidation", "dialogue systems", "Interactive dialogue agents require persistent memory across multi-session conversations. Episodic memory modules extract salient user facts, preferences, and events from raw dialogue turns. Key-value stores index consolidated memory facts with vector embeddings for semantic retrieval. Memory decay algorithms gradually discount obsolete user preferences while reinforcing stable facts. Episodic consolidation provides personalized, context-aware interactions without inflating context windows."),
    ("TR_DOC_052", "Semantic Caching for LLM Inferences", "caching architectures", "Exact string caching fails to match semantically equivalent user queries phrased with different words. Semantic caching embeds incoming queries and searches a vector store of historical cached responses. If the cosine similarity exceeds a strict threshold, the cached completion is returned immediately. Semantic caching reduces API query costs and eliminates inference latency for frequent queries. Cache invalidation policies purge stale entries when underlying reference documentation updates."),
    ("TR_DOC_053", "Learned Index Structures vs Traditional B-Trees", "database systems", "Traditional B-trees index sorted keys using hierarchical tree pointer structures with logarithmic lookup. Learned index structures treat indexing as a regression problem solved by cumulative distribution functions. Multi-stage neural models predict physical record memory addresses directly from search key values. Learned indexes achieve higher memory density and faster lookup times than conventional B-trees. They optimize hardware cache utilization by eliminating pointer chasing through multiple memory levels."),
    ("TR_DOC_054", "Log-Structured Merge Trees in Modern Key-Value Stores", "storage engines", "Log-Structured Merge (LSM) trees optimize write throughput by transforming random writes into sequential writes. Incoming updates are buffered in an in-memory MemTable and appended to an append-only commit log. When the MemTable fills, it flushes to immutable Sorted String Table (SSTable) files on disk. Background compaction merges overlapping SSTables and purges deleted or obsolete record versions. LSM trees provide high write performance at the expense of read amplification."),
    ("TR_DOC_055", "Raft Distributed Consensus and Leader Election", "distributed systems", "Raft achieves distributed consensus by decomposing replication into leader election and log replication. Nodes transition between follower, candidate, and leader roles based on randomized heartbeat timeouts. A candidate wins an election when it receives votes from a strict majority of cluster nodes. The leader accepts client write commands and replicates append entries RPCs across follower logs. Raft guarantees safety by ensuring that committed log entries survive subsequent leader elections."),
    ("TR_DOC_056", "Paxos Consensus and State Machine Replication", "consensus protocols", "Paxos guarantees safe state machine replication across unreliable distributed networks with node failures. The protocol executes in two phases: prepare-promise for leader proposal and accept-accepted for commitment. Proposers broadcast proposal numbers to establish ballot order without requiring centralized synchronization. Acceptors promise not to accept proposals numbered lower than highest observed ballot IDs. Paxos guarantees that only a single value is chosen even under asynchronous network partitions."),
    ("TR_DOC_057", "Vector Distance Metrics: Cosine, Dot Product, and L2", "vector search", "Vector distance metrics determine similarity between embeddings in high-dimensional representation spaces. Dot product measures both directional alignment and vector magnitude across corresponding coordinates. Cosine similarity normalizes vector lengths to evaluate purely directional angular alignment. Euclidean distance measures straight-line spatial distance between points in multi-dimensional space. When embedding vectors are unit normalized, cosine similarity and dot product become mathematically equivalent."),
    ("TR_DOC_058", "Inverted Index Posting Lists and Skip Pointers", "information retrieval", "Inverted indexes map vocabulary terms to posting lists containing document IDs and term frequencies. Posting lists are stored in sorted order to facilitate fast intersection and union operations. Skip pointers allow posting list intersection algorithms to skip non-matching document blocks. Variable-byte and Elias-Fano encoding compress sorted posting list integer sequences efficiently. Inverted indexes remain the gold standard for high-throughput lexical document search."),
    ("TR_DOC_059", "HNSW Multi-Layer Proximity Graph Traversal", "approximate search", "Hierarchical Navigable Small World (HNSW) graphs construct layered networks for vector search. Top layers contain sparse long-range highway edges that enable rapid global navigation. Lower layers contain progressively denser local connections that refine nearest neighbor searches. Greedy routing traverses nodes by selecting neighbors that minimize distance to the query vector. HNSW achieves logarithmic search complexity with high recall across diverse vector datasets."),
    ("TR_DOC_060", "Product Quantization and Vector Space Partitioning", "vector compression", "Product Quantization (PQ) decomposes high-dimensional vector spaces into Cartesian products of sub-spaces. Each sub-space vector segment is quantized into a cluster centroid defined in a codebook. High-dimensional float vectors are compressed into compact byte arrays of centroid indices. Asymmetric distance computation evaluates query-to-centroid distances via fast lookup tables. PQ enables searching billions of vector embeddings directly within limited system RAM."),
    ("TR_DOC_061", "ZeRO Memory Partitioning across Distributed GPUs", "distributed training", "Zero Redundancy Optimizer (ZeRO) eliminates redundant memory consumption across data-parallel training ranks. ZeRO Stage 1 partitions optimizer states across all participating GPUs without communication overhead. ZeRO Stage 2 partitions both optimizer states and gradient tensors across data-parallel ranks. ZeRO Stage 3 partitions model parameters, fetching required layer weights dynamically during forward passes. ZeRO enables training trillion-parameter models on standard clusters without tensor model parallelism."),
    ("TR_DOC_062", "Tensor Parallelism and Intra-Node Matrix Splitting", "parallel training", "Tensor parallelism splits individual weight matrices across GPUs within a single server node. Column-parallel linear layers split the first projection matrix along columns to distribute hidden states. Row-parallel linear layers split the second projection matrix along rows to produce partial sums. An all-reduce communication primitive synchronizes partial sums across GPUs before residual addition. Tensor parallelism reduces per-GPU memory footprint while maintaining high compute utilization."),
    ("TR_DOC_063", "Pipeline Parallelism and 1F1B Scheduling", "pipeline training", "Pipeline parallelism partitions consecutive transformer layers across sequential GPU pipeline stages. To prevent execution idle time termed pipeline bubbles, mini-batches are divided into micro-batches. The One-Forward-One-Backward (1F1B) schedule interleaves forward and backward micro-batch passes. 1F1B maintains a steady state that caps activation memory to the number of pipeline stages. Pipeline parallelism enables scaling model depth across hundreds of distinct GPU worker nodes."),
    ("TR_DOC_064", "Ring Attention and Sequence Parallelism Topologies", "sequence parallelism", "Standard self-attention requires all tokens in a sequence to reside on a single GPU device. Ring Attention distributes sequence tokens across GPUs arranged in a virtual ring topology. Devices compute block attention locally while passing key and value blocks around the ring. Communication and computation overlap completely, eliminating GPU memory limits for sequence length. Ring Attention scales context windows to millions of tokens across distributed cluster nodes."),
    ("TR_DOC_065", "Gradient Checkpointing and Activation Rematerialization", "memory optimization", "During deep network forward passes, intermediate activations are cached for backward pass calculations. Storing activations across all layers dominates GPU VRAM capacity during long-sequence training. Gradient checkpointing caches activations only at designated checkpoint boundaries across the model. Non-cached intermediate activations are recomputed on the fly during the backward pass. This trade-off saves up to seventy percent of activation memory at the cost of thirty percent compute overhead."),
    ("TR_DOC_066", "Label Smoothing in Cross-Entropy Loss Functions", "loss formulation", "Standard cross-entropy loss targets one-hot vectors that encourage models to output infinite logits. This behavior leads to overconfident predictions and poor calibration on out-of-distribution data. Label smoothing blends ground-truth one-hot targets with a uniform distribution over all vocabulary tokens. Penalizing overconfident predictions regularizes model parameters and prevents representation collapse. Label smoothing improves generalization and task accuracy across machine translation benchmarks."),
    ("TR_DOC_067", "Weight Decay vs L2 Regularization in Adaptive Optimizers", "optimization theory", "In standard SGD, L2 weight regularization is mathematically equivalent to weight decay. In adaptive optimizers like Adam, L2 regularization scales gradients by moving average moments. This interaction causes parameters with large historical gradients to experience less decay. Decoupled weight decay (AdamW) applies weight decay directly to parameter weights rather than gradients. AdamW restores proper regularization behavior and significantly improves transformer training stability."),
    ("TR_DOC_068", "Cosine Annealing and Learning Rate Warmup Schedules", "learning schedules", "Starting optimization with large learning rates can destabilize randomly initialized attention weights. Linear warmup gradually ramps learning rates from near zero to peak values over initial steps. Following warmup, cosine annealing decays the learning rate along a cosine curve toward a minimum. Cosine schedules facilitate exploration in early training and fine-grained convergence in late training. Proper scheduling prevents early divergence and yields lower validation perplexity across LLM pretraining."),
    ("TR_DOC_069", "Exponential Moving Average of Model Weights", "model averaging", "Gradient descent produces noisy weight trajectories as optimization traverses complex loss surfaces. Exponential Moving Average (EMA) maintains a running average of model weights across training steps. Shadow weights are updated at each step using a decay factor typically set between 0.999 and 0.9999. Evaluating EMA shadow weights consistently yields lower validation error than final checkpoint weights. EMA effectively smooths out high-frequency parameter oscillations and improves out-of-domain robustness."),
    ("TR_DOC_070", "Monte Carlo Dropout and Epistemic Uncertainty Estimation", "uncertainty estimation", "Standard neural networks output point estimates without calibrated measures of epistemic uncertainty. Monte Carlo dropout activates dropout masks during inference across multiple forward pass iterations. The variance across stochastic predictions quantifies model uncertainty regarding unfamiliar inputs. High prediction variance signals out-of-distribution inputs or contradictory training evidence. MC dropout provides uncertainty estimation without requiring ensemble training of multiple models."),
    ("TR_DOC_071", "Root Mean Square Normalization (RMSNorm) Efficiency", "normalization layers", "Layer Normalization standardizes activations by subtracting mean values and dividing by standard deviations. Calculating mean statistics across hidden dimensions requires reduction passes that add latency. Root Mean Square Normalization (RMSNorm) simplifies this by scaling activations purely by root mean square. RMSNorm enforces scaling invariance while eliminating mean centering computational steps. RMSNorm achieves identical training stability and convergence speed while reducing per-layer latency."),
    ("TR_DOC_072", "SwiGLU Activation Functions in Gated Linear Units", "activation functions", "Gated Linear Units (GLU) multiply linear projections element-wise with gated non-linear activation branches. SwiGLU replaces traditional ReLU or GELU gates with the Swish activation function. The multiplicative gating interaction allows the network to dynamically filter intermediate feature components. Transformers utilizing SwiGLU consistently outperform standard MLP feed-forward networks on language modeling. SwiGLU is widely adopted as the standard feed-forward layer in modern LLM architectures."),
    ("TR_DOC_073", "BFloat16 vs Float16 Numerical Stability in Training", "floating point", "Float16 allocates five exponent bits and ten mantissa bits, providing narrow dynamic range. BFloat16 allocates eight exponent bits and seven mantissa bits, matching the dynamic range of Float32. The expanded exponent range of BFloat16 prevents gradient underflow and overflow during training. Models trained with BFloat16 do not require loss scaling heuristics to maintain numerical stability. BFloat16 has become the default precision format for large-scale transformer pretraining."),
    ("TR_DOC_074", "Nesterov Accelerated Gradient and Momentum Dynamics", "momentum optimizers", "Standard momentum updates accumulate velocity vectors based on gradients computed at current positions. Nesterov Accelerated Gradient computes gradients at predicted lookahead positions along velocity vectors. This lookahead mechanism acts as an anticipatory correction that damps parameter oscillations. NAG accelerates convergence when traversing long narrow ravines in high-dimensional loss landscapes. It provides theoretical convergence rate improvements over standard stochastic gradient descent."),
    ("TR_DOC_075", "Adafactor: Memory-Efficient Optimization with Factored Moments", "efficient optimizers", "Adam maintains two floating-point state tensors per parameter, tripling model training memory footprint. Adafactor factors second moment matrices into low-rank row and column vector representations. This factorization reduces optimizer memory consumption from quadratic to sublinear in layer dimensions. Adafactor also eliminates first moment velocity tracking by using update clipping heuristics. Adafactor enables pretraining large language models on memory-constrained hardware clusters."),
    ("TR_DOC_076", "Lion Optimizer and Sign-Based Gradient Updates", "sign optimizers", "The Lion optimizer tracks momentum using exponential moving averages and updates parameters using sign operations. Taking the sign of momentum vectors ensures that all parameter updates have uniform magnitude. Lion uses less memory than Adam by storing only a single momentum state tensor per parameter. The sign operation acts as implicit regularizer that promotes flatter loss landscape minima. Lion demonstrates strong performance on language pretraining and vision transformer tasks."),
    ("TR_DOC_077", "Self-Instruct: Bootstrapping Instruction Datasets", "synthetic data", "Instruction fine-tuning requires diverse prompt-response pairs that are expensive to curate manually. Self-Instruct prompts a base language model to generate novel task instructions from seed exemplars. The model then generates input instances, expected outputs, and filters out low-quality duplicates. Bootstrapped datasets cover diverse tasks including code generation, summarization, and creative writing. Training on synthetic self-instruct datasets bridges the capability gap with human-annotated instruction corpora."),
    ("TR_DOC_078", "Reinforcement Learning from Human Feedback via PPO", "alignment algorithms", "RLHF aligns language models with human intentions through reinforcement learning optimization. A reward model scores candidate model responses based on pairwise human preference rankings. Proximal Policy Optimization (PPO) updates model weights to maximize reward while penalizing distribution drift. A clipped surrogate objective prevents destructive policy updates between optimization epochs. RLHF significantly improves model helpfulness and harmlessness across interactive user evaluations."),
    ("TR_DOC_079", "Constitutional AI and Self-Correction Protocols", "safety alignment", "Constitutional AI replaces human feedback with AI-driven critique based on constitutional principles. The model generates initial responses and subsequently critiques them against explicit ethical rules. A revision step rewrites responses to eliminate detected harms while maintaining helpfulness. A final model is fine-tuned on self-corrected completions using reinforcement learning or supervised loss. Constitutional AI reduces human annotation burden while enforcing consistent behavioral boundaries."),
    ("TR_DOC_080", "Semantic Entropy and Hallucination Detection", "hallucination metrics", "Standard perplexity measures syntactic token confidence rather than semantic truthfulness. Semantic entropy clusters multiple stochastic generations into distinct semantic meaning classes. If diverse generations express identical semantic meanings, the model is confident in the answer. High semantic entropy indicates conflicting generated claims, signaling potential model hallucination. Semantic entropy reliably detects factual errors without requiring external reference knowledge bases."),
    ("TR_DOC_081", "Entity Disambiguation in Domain Knowledge Graphs", "knowledge graphs", "Named entities in natural language text frequently exhibit lexical ambiguity and polysemy. Entity disambiguation maps detected entity mentions to unambiguous nodes in knowledge graphs. Graph neural networks aggregate neighborhood topological context to resolve ambiguous entity mentions. Dense entity linking matches contextual mention embeddings against candidate entity descriptions. Grounding entities to canonical knowledge graph nodes improves factual consistency in downstream QA."),
    ("TR_DOC_082", "Coreference Resolution in Scientific Corpora", "linguistic parsing", "Coreference resolution identifies all expressions in text that refer to the same real-world entity. Scientific texts contain complex entity chains involving pronouns, nominal phrases, and acronyms. Modern coreference systems evaluate span pair representations using pairwise scoring networks. Antecedent ranking selects the highest-scoring preceding mention for each candidate referring expression. Accurate coreference resolution improves passage retrieval and multi-hop fact verification."),
    ("TR_DOC_083", "Abstractive Summarization and Coverage Penalties", "summarization models", "Abstractive summarization synthesizes concise overviews by paraphrasing source document content. Models often suffer from repetition loops and omission of critical source facts. Coverage mechanisms maintain an accumulated attention history vector to penalize repeated attention focus. Length penalties regulate output verbosity to match target summary conciseness constraints. Contrastive evaluation metrics like ROUGE and BERTScore measure n-gram overlap and semantic fidelity."),
    ("TR_DOC_084", "Siamese Transformer Encoders for Text Similarity", "embedding models", "Siamese transformer networks process two sentence inputs through shared encoder weights. Pooling layers derive fixed-size sentence vectors from contextual token representations. Cosine similarity between pooled vectors measures semantic relatedness between sentence pairs. Triplet loss functions train models to minimize anchor-positive distance while maximizing anchor-negative distance. Siamese encoders provide efficient semantic search across massive sentence embedding indexes."),
    ("TR_DOC_085", "Document Layout Analysis and Visual Block Detection", "document processing", "Unstructured documents such as PDF files encode text without explicit structural hierarchy. Document layout analysis detects visual bounding boxes for titles, sections, tables, and figures. Multi-modal layout models integrate optical character recognition text with visual 2D spatial features. Detecting reading order ensures that multi-column texts are serialized into coherent linear sequences. Proper layout parsing prevents fragmented chunking in downstream retrieval-augmented generation."),
    ("TR_DOC_086", "Token Pruning in Vision and Multimodal Transformers", "efficiency methods", "Vision transformers generate hundreds of patch tokens that contain redundant background information. Token pruning identifies and drops uninformative tokens across intermediate transformer layers. Significance scores computed from attention weights determine which tokens to retain. Dropping background tokens reduces quadratic self-attention computation by over forty percent. Token pruning accelerates inference throughput while maintaining competitive multimodal classification accuracy."),
    ("TR_DOC_087", "Prefix Tuning: Continuous Virtual Token Optimization", "prompt tuning", "Prefix tuning prepends learnable continuous virtual key and value vectors to each attention layer. Unlike discrete prompts, virtual prefix vectors are continuous embeddings optimized via gradient descent. The pretrained language model backbone remains completely frozen during prefix optimization. Only the prefix parameters are stored and swapped per task, minimizing storage overhead. Prefix tuning achieves competitive performance with full fine-tuning on table-to-text generation."),
    ("TR_DOC_088", "AdapterFusion: Compositional Multi-Task Representations", "modular adaptation", "AdapterFusion combines multiple task-specific adapters into a unified multi-task architecture. Individual adapters are trained independently on distinct source tasks while the backbone remains frozen. A fusion layer employs attention mechanisms to dynamically combine adapter outputs for target tasks. This two-stage learning prevents catastrophic forgetting across diverse task distributions. AdapterFusion enables zero-shot task transfer and modular composition of specialized skills."),
    ("TR_DOC_089", "Differentiable Architecture Search via Continuous Relaxation", "neural architecture search", "Neural architecture search automates the design of high-performing deep neural network topologies. DARTS formulates the discrete candidate operation selection as a continuous softmax relaxation. Architecture parameters and model weights are optimized jointly using bi-level gradient optimization. Once search converges, discrete operations with the largest architectural weights are retained. Continuous relaxation reduces architecture search computation from thousands of GPU days to hours."),
    ("TR_DOC_090", "Sparse Matrix Formats (CSR and CSC) in Deep Neural Networks", "sparse formats", "Pruned neural network weight matrices contain high percentages of zero-valued entries. Compressed Sparse Row (CSR) encodes non-zero values, column indices, and row pointer offsets. Compressed Sparse Column (CSC) transposes this layout to optimize column-wise matrix traversals. These sparse formats reduce memory footprint and avoid multiplying by zero values on hardware accelerators. Specialized sparse tensor cores accelerate sparse matrix-vector multiplications during inference."),
    ("TR_DOC_091", "StreamingLLM: Efficient Streaming with Attention Sinks", "streaming generation", "Deploying language models on infinite streaming inputs causes performance collapse when contexts exceed window limits. StreamingLLM discovers that models allocate disproportionate attention mass to initial sequence tokens. These initial tokens act as attention sinks that preserve softmax normalization stability. Keeping initial sink tokens alongside a sliding local window enables infinite text streaming without fine-tuning. StreamingLLM maintains constant memory consumption and stable perplexity across millions of streaming tokens."),
    ("TR_DOC_092", "Chunked Prefill and Interleaved Decoding in Serving", "serving optimization", "Serving engines handle two distinct phases: compute-bound prompt prefill and memory-bound token decoding. Long prompt prefills introduce significant latency spikes that delay ongoing decoding requests. Chunked prefill divides long input prompts into manageable token chunks processed across multiple cycles. Interleaving chunked prefill with active decoding steps stabilizes serving latency and improves hardware utilization. This scheduling strategy maximizes serving throughput while maintaining low tail latency."),
    ("TR_DOC_093", "Memory-Augmented Neural Networks and External Addressing", "neural memory", "Standard recurrent networks compress historical information into fixed-dimensional latent state vectors. Memory-augmented neural networks couple a controller network to an external read-write memory matrix. Read and write operations are executed via soft attention addressing over memory locations. Content-based addressing locates memories by vector similarity, while location-based addressing handles sequential access. External memory allows neural networks to solve algorithmic tasks requiring explicit variable storage."),
    ("TR_DOC_094", "Differentiable Neural Computers and Dynamic Allocation", "advanced memory", "Differentiable Neural Computers (DNC) extend neural Turing machines with dynamic memory allocation. A usage vector tracks memory location availability to prevent overwriting active variable slots. Temporal linkage matrices record the sequential order of written memory representations. Read heads traverse temporal links to recall sequences in chronological or reverse chronological order. DNCs demonstrate strong capability in graph traversal, shortest path finding, and algorithmic reasoning."),
    ("TR_DOC_095", "Longformer: Local Dilated Windows and Global Anchors", "long context attention", "Standard self-attention quadratic complexity prevents scaling transformers to long documents. Longformer combines local sliding window attention with dilated gaps and global token anchors. Sliding windows attend to neighboring tokens, while dilation expands receptive fields without extra compute. Selected global tokens attend to all sequence positions and allow all tokens to attend back. This hybrid pattern reduces complexity to linear while capturing both local syntax and global document context."),
    ("TR_DOC_096", "BigBird: Sparse Attention with Random, Window, and Global Links", "sparse graph attention", "BigBird constructs a sparse attention mechanism modeled after random graph connectivity theory. Each token attends to a local window of neighbors, a set of random tokens, and global anchors. Theoretical analysis proves that this sparse graph preserves universal approximation and Turing completeness. The self-attention computational complexity scales linearly with sequence length instead of quadratically. BigBird enables processing sequence lengths up to eight times longer than standard transformers."),
    ("TR_DOC_097", "Reformer: Locality-Sensitive Hashing for Attention Bucketing", "efficient transformers", "Reformer replaces standard full self-attention with Locality-Sensitive Hashing (LSH) attention. LSH hashes query and key vectors into discrete angular buckets so similar vectors share hash codes. Attention is computed only between tokens that fall within the same hash bucket. Reversible residual layers eliminate the need to store intermediate activations for backward passes. Reformer drastically reduces memory consumption and enables training on extremely long input sequences."),
    ("TR_DOC_098", "Performer: Fast Attention via Orthogonal Random Features", "kernel attention", "Performer approximates softmax attention kernels without computing explicit NxN attention matrices. Fast Attention Via Positive Orthogonal Random features (FAVOR+) decomposes softmax via random feature maps. This kernel decomposition allows reordering matrix multiplications to compute attention in linear time. Positive random feature projections guarantee unbiased kernel estimation with low variance. Performer maintains high fidelity to standard attention without requiring custom GPU hardware kernels."),
    ("TR_DOC_099", "Fast-dLLM: Speculative Drafting via Distilled Student Models", "speculative drafting", "Fast-dLLM optimizes speculative decoding by distilling draft models specifically on target model token distributions. The small assistant model learns to predict multi-token draft blocks conditioned on target hidden states. Confidence thresholds dynamically modulate draft sequence lengths to avoid generating unverified tail tokens. High acceptance rates allow the target model to verify and commit several tokens per inference step. Fast-dLLM achieves significant throughput gains on high-concurrency production serving workloads."),
    ("TR_DOC_100", "Rejection Sampling Fine-Tuning for Mathematical Problem Solving", "reasoning alignment", "Mathematical problem solving requires exact step-by-step correctness without deductive flaws. Rejection sampling fine-tuning samples hundreds of reasoning candidate solutions for each math problem. An automated code execution environment or ground-truth answer parser filters out incorrect derivations. The language model is then fine-tuned on the verified correct reasoning trajectories via supervised cross-entropy. This synthetic bootstrap process substantially elevates mathematical and algorithmic benchmark performance."),
]

def generate_qa_pairs_for_spec(doc_id, title, context):
    sentences = [s.strip() for s in context.split(". ") if s.strip()]
    qa_list = []
    # 10 factual questions directly based on the context
    qa_list.append((f"What is the primary topic of document {doc_id}?", title))
    qa_list.append((f"What does the first sentence state regarding {title}?", sentences[0] + ("." if not sentences[0].endswith(".") else "")))
    qa_list.append((f"According to document {doc_id}, what key mechanism is described?", sentences[1] + ("." if not sentences[1].endswith(".") else "")))
    qa_list.append((f"How does {title} address computational or representation challenges?", sentences[2] + ("." if not sentences[2].endswith(".") else "")))
    qa_list.append((f"What detail is specified in the fourth sentence of document {doc_id}?", sentences[3] + ("." if not sentences[3].endswith(".") else "")))
    qa_list.append((f"What is the concluding finding or benefit of {title}?", sentences[4] + ("." if not sentences[4].endswith(".") else "")))
    qa_list.append((f"Which document ID corresponds to {title}?", doc_id))
    qa_list.append((f"Is {title} discussed in {doc_id}?", f"Yes, {doc_id} focuses on {title}"))
    qa_list.append((f"What architecture or method is analyzed in {doc_id}?", title))
    qa_list.append((f"What operational aspect is emphasized in {doc_id}?", sentences[2] + ("." if not sentences[2].endswith(".") else "")))
    return qa_list


def main():
    import json
    from src.training.training_corpus import get_training_corpus, get_validation_corpus

    # 1. Existing 20 docs
    existing = get_training_corpus()
    existing_docs = existing["documents"]
    print(f"Loaded {len(existing_docs)} existing training docs")

    all_docs = list(existing_docs)

    # 2. Add DOC 021 to 025
    for d in ADDITIONAL_DOCS:
        all_docs.append(d)

    # 3. Add DOC 026 to 100
    for doc_id, title, category, context in TOPIC_SPECS:
        qa_pairs = generate_qa_pairs_for_spec(doc_id, title, context)
        all_docs.append({
            "doc_id": doc_id,
            "title": title,
            "context": context,
            "qa_pairs": qa_pairs,
        })

    print(f"Total documents prepared: {len(all_docs)}")
    assert len(all_docs) == 100, f"Expected 100 docs, got {len(all_docs)}"

    # Generate complete Python code for training_corpus.py
    code_lines = [
        '"""',
        'Training & Validation Corpus for Phase 3.2 & 3.2.1 SA-CMS Adapter Pilot & Scale Audits.',
        '',
        'Strict isolation guarantee:',
        '- 0% overlap with Phase 3.1 / Phase 3.1.1 evaluation documents (DOC001, DOC002, DOC003)',
        '- 0% overlap with Phase 3.1 evaluation questions (Q001-Q100)',
        '- 0% overlap with QASPER benchmark test documents (Docs 0-9)',
        '',
        'Structure:',
        '- 100 Training Documents (TR_DOC_001 to TR_DOC_100) with 10 QA pairs each = 1,000 Training QA pairs',
        '- Pilot 100: TR_Q001 to TR_Q100 (100 samples from TR_DOC_001 to TR_DOC_010)',
        '- Pilot 200: TR_Q001 to TR_Q200 (200 samples from TR_DOC_001 to TR_DOC_020)',
        '- Pilot 500: TR_Q001 to TR_Q500 (500 samples from TR_DOC_001 to TR_DOC_050)',
        '- Pilot 1000: TR_Q001 to TR_Q1000 (1000 samples from TR_DOC_001 to TR_DOC_100)',
        '- 5 Validation Documents (VAL_DOC_001 to VAL_DOC_005) with 10 QA pairs each = 50 Validation QA pairs',
        '"""',
        '',
        'from typing import List, Dict, Any, Optional',
        '',
        '',
        'ALL_TRAIN_DOCS = [',
    ]

    for d in all_docs:
        code_lines.append('    {')
        code_lines.append(f'        "doc_id": {json.dumps(d["doc_id"])},')
        code_lines.append(f'        "title": {json.dumps(d["title"])},')
        code_lines.append(f'        "context": {json.dumps(d["context"])},')
        code_lines.append('        "qa_pairs": [')
        for q, a in d["qa_pairs"]:
            code_lines.append(f'            ({json.dumps(q)}, {json.dumps(a)}),')
        code_lines.append('        ]')
        code_lines.append('    },')

    code_lines.extend([
        ']',
        '',
        '',
        'def get_training_corpus(max_docs: Optional[int] = 20) -> Dict[str, Any]:',
        '    """',
        '    Returns training documents and QA samples.',
        '    Default max_docs=20 returns 20 documents and 200 samples for existing tests.',
        '    If max_docs=100 or None, returns all 100 documents and 1,000 samples.',
        '    """',
        '    selected_docs = ALL_TRAIN_DOCS if max_docs is None else ALL_TRAIN_DOCS[:max_docs]',
        '    qa_samples = []',
        '    q_counter = 1',
        '    for doc in selected_docs:',
        '        d_id = doc["doc_id"]',
        '        ctx = doc["context"]',
        '        for q_text, a_text in doc["qa_pairs"]:',
        '            qa_samples.append({',
        '                "sample_id": f"TR_Q{q_counter:03d}",',
        '                "document_id": d_id:',
        '                "context": ctx,',
        '                "question": q_text,',
        '                "answer": a_text,',
        '                "formatted_text": f"Context: {ctx}\\nQuestion: {q_text}\\nAnswer: {a_text}",',
        '            })',
        '            q_counter += 1',
        '',
        '    if max_docs == 20:',
        '        assert len(qa_samples) == 200, f"Expected 200 training samples, got {len(qa_samples)}"',
        '    return {',
        '        "documents": selected_docs,',
        '        "samples": qa_samples,',
        '    }',
        '',
        '',
        'def get_scale_training_corpus(target_samples: int = 1000) -> Dict[str, Any]:',
        '    """',
        '    Returns training subset matching target sample size (100, 200, 500, 1000).',
        '    """',
        '    num_docs = min(100, max(1, (target_samples + 9) // 10))',
        '    corpus = get_training_corpus(max_docs=num_docs)',
        '    samples = corpus["samples"][:target_samples]',
        '    return {',
        '        "documents": corpus["documents"][:num_docs],',
        '        "samples": samples,',
        '    }',
        '',
        '',
        'def get_validation_corpus() -> Dict[str, Any]:',
        '    """',
        '    Returns 5 distinct validation documents with 10 QA pairs each (total 50 QA samples).',
        '    Zero overlap with training set or Phase 3.1 evaluation documents.',
        '    """',
    ])

    # Re-use validation docs from get_validation_corpus()
    val_corpus = get_validation_corpus()
    val_docs = val_corpus["documents"]

    code_lines.append('    val_docs = [')
    for d in val_docs:
        code_lines.append('        {')
        code_lines.append(f'            "doc_id": {json.dumps(d["doc_id"])},')
        code_lines.append(f'            "title": {json.dumps(d["title"])},')
        code_lines.append(f'            "context": {json.dumps(d["context"])},')
        code_lines.append('            "qa_pairs": [')
        for q, a in d["qa_pairs"]:
            code_lines.append(f'                ({json.dumps(q)}, {json.dumps(a)}),')
        code_lines.append('            ]')
        code_lines.append('        },')
    code_lines.extend([
        '    ]',
        '',
        '    val_samples = []',
        '    q_counter = 1',
        '    for doc in val_docs:',
        '        d_id = doc["doc_id"]',
        '        ctx = doc["context"]',
        '        for q_text, a_text in doc["qa_pairs"]:',
        '            val_samples.append({',
        '                "sample_id": f"VAL_Q{q_counter:03d}",',
        '                "document_id": d_id,',
        '                "context": ctx,',
        '                "question": q_text,',
        '                "answer": a_text,',
        '                "formatted_text": f"Context: {ctx}\\nQuestion: {q_text}\\nAnswer: {a_text}",',
        '            })',
        '            q_counter += 1',
        '',
        '    assert len(val_samples) == 50, f"Expected 50 validation samples, got {len(val_samples)}"',
        '    return {',
        '        "documents": val_docs,',
        '        "samples": val_samples,',
        '    }',
        '',
    ])

    # Fix syntax error in sample_id line
    code_text = "\n".join(code_lines).replace('"document_id": d_id:', '"document_id": d_id,')
    target_path = ROOT_DIR / "src" / "training" / "training_corpus.py"
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(code_text)
    print(f"Successfully wrote expanded corpus to {target_path}")


if __name__ == "__main__":
    main()

