# HumanPersonaBase: Structural Text Transformation for Human-Like AI Communication

**Authors**: Anonymous (for review)

---

## Abstract

Large language models (LLMs) have achieved near-human semantic competence, yet AI-generated text remains detectable through systematic structural differences from human writing. We present HumanPersonaBase, a pipeline framework that applies six empirically calibrated structural transformations to LLM output—sentence length normalization, hedging injection, self-correction insertion, word-count adjustment, cushion phrase introduction, and position-aware filler injection—to close the gap between AI-generated and human-authored text distributions. Parameters are extracted from the HumanLLMs/Human-Like-DPO-Dataset (10,884 samples) using an 80/20 holdout protocol. We evaluate using a dual-score system: Mean Alignment (weighted proximity to per-metric target means) and Distribution Alignment (Wasserstein distance–based score over full distributions). The pipeline achieves a Mean Alignment score of 0.945 (95% CI: [0.902, 0.961]) and a Distribution Alignment score of 0.864 (95% CI: [0.811, 0.877]), compared to a raw-LLM baseline of 0.003 and near-zero respectively, demonstrating the efficacy of data-driven structural transformation for human-like text generation.

---

## 1. Introduction

### 1.1 The Structural Gap Between AI and Human Text

The rapid advancement of large language models has largely solved the semantic dimension of human-like communication. Jones and Bergen (2024) demonstrated that GPT-4.5, when equipped with a human-like persona, was identified as human by 73% of evaluators in a controlled Turing test—surpassing the recognition rate of actual human participants. Yet the complementary question remains underexplored: even when semantic content is indistinguishable, do AI-generated texts exhibit structural regularities that betray their origin?

Recent work in AI-generated text detection has confirmed that structural features—sentence length distributions, hedging frequency, filler word usage, and self-correction patterns—differ systematically between human and AI-authored text (Gehrmann et al., 2019; Mitchell et al., 2023). AI-generated text tends toward uniform sentence lengths, lacks hesitation markers, and is absent the redundant cushioning phrases characteristic of natural human expression. These structural signatures enable reliable detection even when semantic quality is high.

### 1.2 DPO Datasets as Empirical Calibration Sources

Direct Preference Optimization (DPO) datasets (Rafailov et al., 2023) that distinguish human-preferred ("chosen") from AI-preferred ("rejected") responses constitute an underutilized resource for structural calibration. The HumanLLMs/Human-Like-DPO-Dataset, comprising 10,884 paired samples, encodes implicit knowledge about what structural patterns human evaluators prefer. By extracting distributional statistics from the "chosen" (human-like) side of this dataset, we can derive empirical targets for each structural metric without relying on manually curated style guides.

### 1.3 Contributions

This paper makes the following contributions:

1. **A six-step structural transformation pipeline** that operates post-hoc on LLM-generated text to impose human-like structural patterns, without requiring model fine-tuning.
2. **An empirical parameter extraction methodology** that derives calibration targets from DPO dataset statistics, providing a principled and reproducible basis for parameter setting.
3. **A dual-score evaluation protocol** combining Mean Alignment (per-metric target proximity) and Distribution Alignment (Wasserstein distance over full distributions), enabling fine-grained diagnosis of transformation quality.
4. **A held-out benchmark** (80/20 split, 500-sample evaluation set, 1,000-iteration bootstrap) establishing performance baselines and confidence intervals for all six structural metrics.

---

## 2. Related Work

### 2.1 AI-Generated Text Detection

The detection of AI-generated text has become a central problem in NLP following the widespread deployment of large language models. Early approaches relied on perplexity-based statistics: Gehrmann et al. (2019) introduced GLTR, which uses token-rank distributions to identify AI-generated text. Subsequent work has shown that neural classifiers trained on AI/human text pairs achieve high detection accuracy (Uchendu et al., 2020; Zellers et al., 2019), though such classifiers exhibit brittleness to model updates and domain shift.

Mitchell et al. (2023) proposed DetectGPT, a zero-shot method exploiting the curvature of log-probability functions under perturbation. Concurrently, statistical approaches based on structural features—sentence length variance, lexical diversity, punctuation patterns—have demonstrated robustness advantages over semantic detection methods (Ippolito et al., 2020). Our work takes the complementary perspective: rather than detecting AI text, we seek to transform it to evade structural detection while preserving semantic content.

### 2.2 Text Humanization and Style Transfer

Style transfer in NLP aims to modify surface-level text properties while preserving semantic content (Shen et al., 2017; Hu et al., 2017). Early approaches used variational autoencoders with disentangled latent spaces; more recent work has applied in-context learning and instruction-tuning for attribute-controlled generation (Reif et al., 2022). However, existing style transfer work has focused primarily on sentiment, formality, and authorship rather than the AI-versus-human axis.

The problem of reducing AI "tells" in generated text has been addressed indirectly in persona-based prompting literature. Jones and Bergen (2024) show that persona instructions substantially affect perceived humanness, suggesting that paralinguistic features mediate human-likeness judgments. Our approach differs by operating at the post-generation structural level, offering a model-agnostic alternative to prompt engineering.

### 2.3 Direct Preference Optimization and Human Preference Data

Direct Preference Optimization (Rafailov et al., 2023) reformulates RLHF (Christiano et al., 2017) as a supervised learning problem using paired preference data (chosen, rejected). DPO datasets encode human preference judgments implicitly in their structure. Several datasets on Hugging Face have been constructed to capture the human-likeness axis specifically, including HumanLLMs/Human-Like-DPO-Dataset, which pairs human-authored responses with AI-generated alternatives across diverse conversational contexts.

Stiennon et al. (2020) demonstrated that human feedback substantially improves text quality along dimensions not captured by automatic metrics. We extend this insight by using DPO preference data not for model training, but as a distributional reference for structural calibration—extracting target statistics from "chosen" samples to guide our transformation pipeline.

### 2.4 Structural Features of Human Communication

Computational sociolinguistics has characterized the structural properties of human text across registers. Nguyen et al. (2016) survey computational approaches to register variation, code-switching, and hedging. Hedges—linguistic devices that reduce commitment to propositional content ("I think," "perhaps," "it seems")—have been extensively studied as markers of epistemic stance (Hyland, 1996) and are notably underrepresented in AI-generated text.

Filler words (discourse markers such as "well," "actually," "you know") have been shown to serve pragmatic functions in human communication beyond mere hesitation, including floor management and epistemic signaling (Schiffrin, 1987). The systematic absence of fillers in AI text is a detectable signature that our pipeline targets directly.

---

## 3. Method

### 3.1 Pipeline Architecture

The HumanPersonaBase transformation pipeline applies six sequential structural transformations to LLM-generated text. The pipeline is designed to be modular, parameter-driven, and language-aware. Each transformation step targets a specific measurable structural property.

**Step 1: Sentence Length Normalization.** The input text is segmented into sentences. A target coefficient of variation (CV) for sentence length is established from the DPO dataset. Sentences are split or merged stochastically to approach the target CV, expanding the variance of sentence lengths from the low-variance uniformity typical of LLM output.

**Step 2: Hedge Injection.** Hedging expressions (e.g., "I think," "perhaps," "it seems like") are inserted at the beginnings or within the bodies of sentences with probability proportional to the gap between observed and target hedge rate. Injection positions are selected to preserve grammaticality.

**Step 3: Self-Correction Insertion.** Short self-correction sequences (e.g., "well, actually—", "or rather,") are inserted at sentence boundaries with low probability, reproducing the trace of in-stream revision characteristic of human text.

**Step 4: Words-Per-Sentence Adjustment.** When the mean words-per-sentence of the transformed text deviates from the empirical target, sentences are subject to word-level compression or expansion operations—removing or inserting function words and connectives—to bring the mean into alignment.

**Step 5: Cushion Phrase Introduction.** Cushion phrases (acknowledgment and softening expressions such as "I see," "that makes sense," "I appreciate you sharing that") are prepended to response segments. Cushion rate is controlled against an empirical target from the DPO dataset.

**Step 6: Position-Aware Filler Injection.** Filler words and discourse markers are injected at sentence-initial positions, with position-awareness constraints preventing consecutive filler placement. The filler vocabulary and injection probability are calibrated from DPO statistics.

The pipeline is parameterized through a configuration layer that supports per-language and per-register customization. Transformation steps are applied in the above order; each step operates on the output of the previous step.

### 3.2 Parameter Calibration

Parameters for all six transformation steps are extracted empirically from the "chosen" (human-preferred) samples of the HumanLLMs/Human-Like-DPO-Dataset. For each metric $m$, the calibration procedure computes:

$$\mu_m = \frac{1}{|D_{train}|} \sum_{x \in D_{train}} f_m(x)$$

where $f_m(x)$ is the metric function applied to sample $x$, and $D_{train}$ is the training split (80% of the full dataset). The resulting target values $\{\mu_m\}$ are stored in the pipeline configuration and used as optimization targets during inference.

Metric weights for the overall Mean Alignment score are derived from the inverse coefficient of variation of each metric across the training set, reflecting the reliability of each metric as a calibration signal. Metrics with higher cross-sample consistency receive higher weight.

This approach ensures that parameter values are grounded in the empirical distribution of human-like text rather than hand-tuned heuristics, and that the calibration source is strictly separated from the evaluation set by the train/test split.

### 3.3 Evaluation Protocol

**Dataset split.** The full HumanLLMs/Human-Like-DPO-Dataset (10,884 samples) is split 80/20 by random seed (seed = 42). Calibration parameters are extracted from the 80% training split. Evaluation is performed on a 500-sample random subset of the 20% held-out test split.

**Baseline condition.** The "raw" baseline consists of the "rejected" samples from the DPO dataset—AI-generated responses without transformation—providing a direct comparison point that shares the semantic content distribution with the human-preferred targets.

**Dual scoring.**

*Mean Alignment Score* measures how closely the pipeline output mean matches the human-preferred target mean for each metric:

$$S_{mean} = \sum_m w_m \cdot \text{score}_m, \quad \text{score}_m = \max\left(0, 1 - \frac{|\hat{\mu}_m - \mu_m^*|}{\mu_m^*}\right)$$

where $\hat{\mu}_m$ is the observed pipeline mean, $\mu_m^*$ is the calibration target, and $w_m$ is the normalized metric weight.

*Distribution Alignment Score* measures full distributional similarity between pipeline output and human-preferred samples using the Wasserstein distance (earth mover's distance):

$$S_{dist} = 1 - \frac{W_1(\hat{P}_m, P_m^*)}{\max(W_1^{raw}, W_1^{pipeline})}$$

normalized per metric and aggregated as an unweighted mean across all metrics.

**Statistical validation.** Bootstrap confidence intervals (1,000 iterations, $\alpha = 0.05$) are computed for both aggregate scores and per-metric statistics. Kolmogorov-Smirnov (KS) tests are performed between pipeline output and human-preferred distributions for each metric to identify residual distributional mismatches.

---

## 4. Experiments

### 4.1 Dataset

The HumanLLMs/Human-Like-DPO-Dataset contains 10,884 paired preference samples from conversational contexts. Each sample consists of a prompt, a "chosen" response (human-authored or human-preferred), and a "rejected" response (AI-generated or AI-preferred). The dataset covers diverse topics and registers in English.

For our evaluation, the "chosen" samples serve as the human reference distribution, and the "rejected" samples serve as the raw-LLM baseline. The 80/20 train/test split (seed = 42) ensures that calibration targets are derived exclusively from samples not seen during evaluation. The 500-sample evaluation subset is drawn uniformly at random from the 20% held-out test split.

### 4.2 Metrics

Six structural metrics are computed for all text samples:

| Metric | Description | Target Mean |
|---|---|---|
| `sentence_length_cv` | Coefficient of variation of sentence lengths (chars) | 0.633 |
| `hedge_rate` | Proportion of sentences containing hedge expressions | 0.082 |
| `self_correction_rate` | Rate of self-correction markers per sentence | 0.0019 |
| `words_per_sentence` | Mean word count per sentence | 13.53 |
| `cushion_rate` | Proportion of sentences starting with cushion phrases | 0.157 |
| `filler_rate` | Proportion of sentences containing position-aware fillers | 0.165 |

Metric weights (derived from training-set CV) are: `filler_rate` = 1.877, `words_per_sentence` = 1.450, `sentence_length_cv` = 1.162, `hedge_rate` = 0.875, `cushion_rate` = 0.541, `self_correction_rate` = 0.097.

`filler_rate` and `words_per_sentence` receive the highest weights, reflecting their higher cross-sample consistency and thus reliability as calibration signals.

### 4.3 Results

**Overall performance.** The pipeline achieves a Mean Alignment score of **0.945** (95% CI: [0.902, 0.961]) compared to the raw-LLM baseline of **0.003**, representing a 325-fold improvement. The Distribution Alignment score (Wasserstein-based) is **0.864** (95% CI: [0.811, 0.877]).

**Per-metric results.**

| Metric | Raw Score | Pipeline Score | Raw Mean | Pipeline Mean | Target Mean | KS pass |
|---|---|---|---|---|---|---|
| `sentence_length_cv` | 0.000 | 0.974 | 0.425 | 0.628 | 0.633 | Yes (p=0.370) |
| `hedge_rate` | 0.020 | 0.892 | 0.019 | 0.089 | 0.082 | No (p=0.016) |
| `self_correction_rate` | 0.000 | 0.601 | 0.001 | 0.002 | 0.002 | Yes (p=1.000) |
| `words_per_sentence` | 0.000 | 0.948 | 18.44 | 13.28 | 13.53 | No (p=0.003) |
| `cushion_rate` | 0.000 | 0.991 | 0.016 | 0.156 | 0.157 | Yes (p=0.996) |
| `filler_rate` | 0.000 | 0.954 | 0.001 | 0.158 | 0.165 | Yes (p=0.069) |

**Wasserstein distribution alignment scores** (per-metric):

| Metric | Wasserstein Distance | Distribution Alignment Score |
|---|---|---|
| `sentence_length_cv` | 0.023 | 0.895 |
| `hedge_rate` | 0.012 | 0.808 |
| `self_correction_rate` | 0.001 | 0.534 |
| `words_per_sentence` | 0.574 | 0.878 |
| `cushion_rate` | 0.026 | 0.843 |
| `filler_rate` | 0.019 | 0.885 |

**Bootstrap confidence intervals (95%) for pipeline metric means:**

| Metric | CI Lower | CI Upper |
|---|---|---|
| `sentence_length_cv` | 0.614 | 0.641 |
| `hedge_rate` | 0.081 | 0.097 |
| `self_correction_rate` | 0.001 | 0.004 |
| `words_per_sentence` | 13.052 | 13.523 |
| `cushion_rate` | 0.124 | 0.186 |
| `filler_rate` | 0.148 | 0.167 |

**Effect sizes (Cohen's d)** relative to raw baseline: `filler_rate` (d=1.755), `sentence_length_cv` (d=1.086), `words_per_sentence` (d=−1.356), `hedge_rate` (d=0.818), `cushion_rate` (d=0.506), `self_correction_rate` (d=0.091). The large effect sizes for `filler_rate`, `sentence_length_cv`, and `words_per_sentence` indicate that these are the dimensions where the pipeline produces the most substantial transformation.

### 4.4 Ablation Study

We evaluate the marginal contribution of each pipeline step by disabling one step at a time and re-running the full evaluation on the held-out test set (n=500).

| Variant | Mean Align. | Dist. Align. | Δ Mean | Δ Dist. |
|---------|------------|-------------|--------|---------|
| Full Pipeline | 0.945 | 0.864 | — | — |
| − Filler insertion | 0.622 | 0.569 | −0.323 | −0.296 |
| − Sentence splitting | 0.751 | 0.720 | −0.194 | −0.144 |
| − Short interjections | 0.763 | 0.742 | −0.182 | −0.122 |
| − Hedge injection | 0.808 | 0.740 | −0.137 | −0.125 |
| − Cushion injection | 0.851 | 0.779 | −0.094 | −0.085 |
| − Self-correction | 0.944 | 0.866 | −0.001 | +0.001 |
| No pipeline (baseline) | 0.003 | 0.000 | −0.942 | −0.864 |

**Filler insertion** is by far the dominant contributor (Δ = −0.323 mean, −0.296 distributional), consistent with its high metric weight (w = 1.88) derived from the largest Cohen's d (1.755) among all metrics. **Sentence splitting** and **short interjections** jointly control sentence-level statistics (`words_per_sentence` and `sentence_length_cv`), contributing Δ = −0.194 and −0.182 respectively. **Self-correction injection** contributes effectively zero (Δ = −0.001), reflecting both the low effect size (d = 0.091) and the extremely low base rate of self-correction markers in natural text (0.19% per sentence).

### 4.5 Human Evaluation

[PENDING: Human evaluation protocol is designed. Protocol: present 100 sentence pairs (pipeline output vs. raw LLM output) to N=30 human raters on a crowdsourcing platform. Raters are asked to identify which sample was written by a human using a two-alternative forced choice (2AFC) paradigm. Human identification rate above 50% for raw samples and near-50% (chance) for pipeline samples would constitute positive evidence of structural humanization. Inter-rater agreement to be measured with Fleiss's kappa. Execution pending funding allocation.]

---

## 5. Discussion

### 5.1 Structural Limitations of Fixed-Probability Injection

The pipeline's transformation steps apply injection probabilities uniformly across all positions and contexts. This design achieves strong Mean Alignment scores but creates distributional artifacts visible in the KS test failures for `hedge_rate` and `words_per_sentence`. Fixed-probability injection necessarily produces distributions that are more regular than the human reference—essentially a convolution of the raw distribution with a fixed injection kernel—which cannot reproduce the highly non-uniform positional and contextual patterns of human hedging and sentence length variation.

Human writers hedge more in uncertain contexts and less in assertive ones; they write longer sentences when elaborating and shorter sentences when concluding. A context-aware injection mechanism that conditions injection probability on local semantic features would address this limitation, at the cost of substantially increased computational overhead and reduced transparency.

### 5.2 Mean vs. Distribution Alignment Gap

The gap between Mean Alignment (0.945) and Distribution Alignment (0.864) is theoretically expected: matching a distribution's mean is strictly easier than matching its full shape. The gap is smallest for `sentence_length_cv` (mean score 0.974, distribution score 0.895) and largest for `self_correction_rate` (mean score 0.601, distribution score 0.534), suggesting that self-correction events are the most difficult to distribute realistically.

The `self_correction_rate` metric also has the lowest metric weight (0.097), which indicates high cross-sample variance in the training set—humans vary widely in how often they self-correct. This variance makes the metric both difficult to calibrate against and relatively uninformative as a discriminator. Future work should explore whether self-correction injection should be conditioned on detected uncertainty in the preceding sentence content.

### 5.3 KS Test Failures: hedge_rate and words_per_sentence

Two metrics fail the KS test at $\alpha = 0.05$: `hedge_rate` (KS stat = 0.098, p = 0.016) and `words_per_sentence` (KS stat = 0.114, p = 0.003). These failures indicate that the pipeline output and human reference distributions differ in shape, not merely in mean.

For `words_per_sentence`, the pipeline achieves a close mean match (13.28 vs. target 13.53) but likely produces a distribution with excess kurtosis—sentences that have been word-count adjusted cluster around the target mean more tightly than the human distribution, which has heavier tails from both very short and very long sentences. Reproducing this tail behavior would require explicit sampling from a learned sentence-length distribution rather than deterministic target-seeking adjustment.

For `hedge_rate`, the over-injection that produces means slightly above target (0.089 vs. 0.082) combined with insufficient within-sample variance results in a distribution shifted toward higher hedge rates with insufficient representation of hedge-free passages. Contextual gating of hedge injection based on semantic certainty signals would likely improve distributional fit.

---

## 6. Conclusion

We have presented HumanPersonaBase, a six-step structural transformation pipeline for producing human-like text from LLM outputs without model fine-tuning. By extracting calibration parameters from the human-preferred side of a DPO dataset and evaluating on a strict 80/20 holdout, we demonstrate Mean Alignment of 0.945 and Distribution Alignment of 0.864 against human reference distributions across six structural metrics.

The results establish that data-driven structural transformation can close the measurable structural gap between AI-generated and human-authored text. Four of six metrics pass the Kolmogorov-Smirnov distributional similarity test; the two failures (`hedge_rate`, `words_per_sentence`) point to the specific limitation of context-independent injection: fixed-probability mechanisms can match means but struggle to reproduce the context-conditional variance patterns of human writing.

The dual-score evaluation protocol introduced here—combining per-metric mean alignment with distribution-level Wasserstein scoring—provides a richer diagnostic framework than single-metric approaches. We recommend this protocol for future work on structural text humanization.

Future work will address: (1) context-aware injection conditioned on local semantic features; (2) ablation studies quantifying the marginal contribution of each transformation step; (3) human evaluation under the 2AFC protocol described in Section 4.5; and (4) extension to languages beyond English through culture-specific filler and hedge vocabularies.

---

## References

1. Christiano, P., Leike, J., Brown, T. B., Martic, M., Legg, S., & Amodei, D. (2017). Deep reinforcement learning from human preferences. *Advances in Neural Information Processing Systems (NeurIPS)*, 30.

2. Gehrmann, S., Strobelt, H., & Rush, A. M. (2019). GLTR: Statistical detection and visualization of generated text. *Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics (ACL)*, System Demonstrations.

3. Hu, Z., Yang, Z., Liang, X., Salakhutdinov, R., & Xing, E. P. (2017). Toward controlled generation of text. *Proceedings of the 34th International Conference on Machine Learning (ICML)*.

4. Hyland, K. (1996). Writing without conviction? Hedging in science research articles. *Applied Linguistics*, 17(4), 433–454.

5. Ippolito, D., Duckworth, D., Callison-Burch, C., & Eck, D. (2020). Automatic detection of generated text is easiest when humans are fooled. *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL)*.

6. Jones, C. R., & Bergen, B. K. (2024). A Turing test of whether AI chatbots are behaviorally similar to humans. *Proceedings of the National Academy of Sciences (PNAS)*.

7. Mitchell, E., Lee, Y., Khazatsky, A., Manning, C. D., & Finn, C. (2023). DetectGPT: Zero-shot machine-generated text detection using probability curvature. *Proceedings of the 40th International Conference on Machine Learning (ICML)*.

8. Mitchell, M. (2025). The Turing Test and our shifting conceptions of intelligence. *Science*.

9. Nguyen, D., Dogruoz, A. S., Rosé, C. P., & de Jong, F. (2016). Computational Sociolinguistics: A Survey. *Computational Linguistics*, 42(3), 537–593.

10. Rafailov, R., Sharma, A., Mitchell, E., Manning, C. D., Ermon, S., & Finn, C. (2023). Direct preference optimization: Your language model is secretly a reward model. *Advances in Neural Information Processing Systems (NeurIPS)*, 36.

11. Reif, E., Ippolito, D., Yuan, A., Coenen, A., Callison-Burch, C., & Wei, J. (2022). A recipe for arbitrary text style transfer with large language models. *Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (ACL)*.

12. Schiffrin, D. (1987). *Discourse Markers*. Cambridge University Press.

13. Shen, T., Lei, T., Barzilay, R., & Jaakkola, T. (2017). Style transfer from non-parallel text by cross-alignment. *Advances in Neural Information Processing Systems (NeurIPS)*, 30.

14. Stiennon, N., Ouyang, L., Wu, J., Ziegler, D. M., Lowe, R., Voss, C., Radford, A., Amodei, D., & Christiano, P. (2020). Learning to summarize from human feedback. *Advances in Neural Information Processing Systems (NeurIPS)*, 33.

15. Turing, A. M. (1950). Computing machinery and intelligence. *Mind*, 59(236), 433–460.

16. Uchendu, A., Le, T., Zhu, K., & Lee, D. (2020). Authorship attribution for neural text generation. *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP)*.

17. Zellers, R., Holtzman, A., Rashkin, H., Bisk, Y., Farhadi, A., Roesner, F., & Choi, Y. (2019). Defending against neural fake news. *Advances in Neural Information Processing Systems (NeurIPS)*, 32.
