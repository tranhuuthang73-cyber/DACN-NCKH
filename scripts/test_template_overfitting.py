"""
Phase 2.5 Task 5: MK-NIAH Failure Analysis - Template Overfitting Hypothesis Test.
Evaluates whether repeated template structure causes SA-CMS retrieval failure.

Three controlled conditions:
A. Original Repeated Template: Identical phrasing for all needles.
B. Multiple Paraphrased Templates: Distinct phrasing per needle from a curated pool.
C. Randomized Sentence Structure: Variable syntactic order and formatting.

Compares:
- Accuracy (%)
- Target Probability
- Target Rank (in vocab)
- Top-5 Token Predictions
"""

import math
import os
import random
import sys
from typing import Dict, Any, List, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer

from src.hope_attention.sa_cms import StructureAlignedHopeLM
from src.document_structure.parser import DocumentStructureParser


class TemplateControlledMKNIAH:
    """
    Generator for MK-NIAH under 3 controlled template conditions.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.entity_keys = [
            "quasar", "pulsar", "supernova", "magnetar", "nebula",
            "asteroid", "comet", "galaxy", "exoplanet", "meteor",
            "photon", "neutrino", "lepton", "hadron", "baryon",
        ]
        self.haystack_sentences = [
            "In modern theoretical physics, quantum field theory describes the dynamics of subatomic particles.",
            "Gravitational wave observatories have detected numerous black hole mergers across distant cosmic structures.",
            "High resolution spectroscopy provides critical measurements of stellar chemical abundance and redshift.",
            "Astronomical surveys map the cosmic microwave background to constrain cosmological parameters.",
            "The formation of galactic halos depends strongly on the distribution of dark matter particles.",
            "Electromagnetic radiation spans a wide frequency continuum from radio waves to energetic gamma rays.",
            "Stellar nucleosynthesis synthesizes heavy elements during supernova explosions in massive stars.",
            "Orbital resonance within planetary systems causes periodic gravitational perturbations over long epochs.",
        ]

        self.paraphrase_templates = [
            ("The designated access token assigned to {k} is {v}.", "What is the designated access token assigned to {k}? Answer:"),
            ("For entity {k}, the registered passcode is {v}.", "What is the registered passcode for {k}? Answer:"),
            ("The security identifier corresponding to {k} equals {v}.", "What is the security identifier corresponding to {k}? Answer:"),
            ("Record indicates {k} is cataloged under ID {v}.", "What ID is {k} cataloged under? Answer:"),
            ("System database assigns code {v} to entity {k}.", "What code does the system assign to {k}? Answer:"),
        ]

        self.random_syntax_templates = [
            ("{v} serves as the authentication string for {k}.", "Which authentication string serves for {k}? Answer:"),
            ("In our central registry, {k} maps directly to value {v}.", "What does {k} map to in the registry? Answer:"),
            ("Entity {k} has been indexed with the code {v}.", "What code is entity {k} indexed with? Answer:"),
            ("The numerical parameter associated with {k} is recorded as {v}.", "What is the numerical parameter for {k}? Answer:"),
        ]

    def generate_sample(
        self,
        sample_idx: int,
        condition: str,  # 'A_repeated', 'B_paraphrased', 'C_random_syntax'
        num_keys: int = 3,
    ) -> Dict[str, Any]:
        rng = random.Random(self.seed + sample_idx * 31)
        chosen_keys = rng.sample(self.entity_keys, num_keys)

        needles = {}
        for k in chosen_keys:
            code = str(rng.randint(10000, 99999))
            needles[k] = code

        queried_key = rng.choice(chosen_keys)
        expected_val = needles[queried_key]

        needle_texts = []
        query_prompt = ""

        if condition == "A_repeated":
            for k, v in needles.items():
                needle_texts.append(f"The secret identification code for {k} is {v}.")
            query_prompt = f"What is the secret identification code for {queried_key}? Answer:"

        elif condition == "B_paraphrased":
            shuffled_templates = rng.sample(self.paraphrase_templates, len(self.paraphrase_templates))
            for i, (k, v) in enumerate(needles.items()):
                t_needle, t_query = shuffled_templates[i % len(shuffled_templates)]
                needle_texts.append(t_needle.format(k=k, v=v))
                if k == queried_key:
                    query_prompt = t_query.format(k=k)

        elif condition == "C_random_syntax":
            shuffled_templates = rng.sample(self.random_syntax_templates, len(self.random_syntax_templates))
            for i, (k, v) in enumerate(needles.items()):
                t_needle, t_query = shuffled_templates[i % len(shuffled_templates)]
                needle_texts.append(t_needle.format(k=k, v=v))
                if k == queried_key:
                    query_prompt = t_query.format(k=k)
        else:
            raise ValueError(f"Unknown condition: {condition}")

        # Build context
        full_parts = []
        h_idx = 0
        for n_text in needle_texts:
            full_parts.append(self.haystack_sentences[h_idx % len(self.haystack_sentences)])
            h_idx += 1
            full_parts.append(n_text)
        while h_idx < len(self.haystack_sentences):
            full_parts.append(self.haystack_sentences[h_idx])
            h_idx += 1

        context_text = " ".join(full_parts)
        prompt_text = f"{context_text} {query_prompt}"

        return {
            "sample_idx": sample_idx,
            "condition": condition,
            "context_text": context_text,
            "prompt_text": prompt_text,
            "queried_key": queried_key,
            "expected_val": expected_val,
        }


def run_template_overfitting_analysis(num_samples: int = 30, device: str = "cuda"):
    print("=" * 80)
    print("TASK 5: MK-NIAH FAILURE ANALYSIS — TEMPLATE OVERFITTING HYPOTHESIS TEST")
    print("=" * 80)

    dtype = torch.float16 if device == "cuda" else torch.float32
    model = StructureAlignedHopeLM(
        model_name_or_path="HuggingFaceTB/SmolLM2-135M",
        num_levels=2,
        device=device,
        torch_dtype=dtype,
    )
    tokenizer = model.tokenizer
    bench = TemplateControlledMKNIAH(seed=42)

    conditions = ["A_repeated", "B_paraphrased", "C_random_syntax"]
    methods = [
        ("ICL (No Memory Update)", None),
        ("Fixed-Token CMS (Equal Budget)", "fixed_token"),
        ("SA-CMS (Equal Budget)", "structure"),
        ("Random Boundary (Equal Budget)", "random"),
    ]

    results_summary = {}

    for cond in conditions:
        print(f"\n>>> Running Condition: {cond} ({num_samples} samples) <<<")
        results_summary[cond] = {}

        for method_name, sched_mode in methods:
            correct = 0
            target_probs = []
            target_ranks = []
            top1_predictions = []

            for idx in range(num_samples):
                sample = bench.generate_sample(idx, condition=cond)
                prompt = sample["prompt_text"]
                context = sample["context_text"]
                expected_val = sample["expected_val"]
                queried_key = sample["queried_key"]

                prompt_enc = tokenizer(prompt, return_tensors="pt").to(model.device)
                prompt_ids = prompt_enc.input_ids
                target_token_id = tokenizer.encode(f" {expected_val}", add_special_tokens=False)[0]

                # Online ingestion under equal update budget
                if sched_mode is not None and model.cms is not None:
                    model.reset_memory()
                    model.clear_event_log()
                    model.ingest_structured_document(
                        document_text=context,
                        schedule_mode=sched_mode,
                        seed=42 + idx * 7,
                    )

                with torch.no_grad():
                    logits, _ = model.forward(prompt_ids)
                    last_logits = logits[0, -1, :]
                    probs = F.softmax(last_logits, dim=-1)

                    target_prob = probs[target_token_id].item()
                    target_probs.append(target_prob)

                    sorted_ids = torch.argsort(last_logits, descending=True)
                    target_rank = (sorted_ids == target_token_id).nonzero(as_tuple=True)[0].item() + 1
                    target_ranks.append(target_rank)

                    top1_id = sorted_ids[0].item()
                    top1_tok = tokenizer.decode([top1_id]).strip()
                    top1_predictions.append(top1_tok)

                    # Autoregressive generation up to 6 tokens
                    curr_ids = prompt_ids.clone()
                    for _ in range(6):
                        cur_logits, _ = model.forward(curr_ids)
                        next_tok = torch.argmax(cur_logits[:, -1, :], dim=-1, keepdim=True)
                        curr_ids = torch.cat([curr_ids, next_tok], dim=1)
                        if next_tok.item() == tokenizer.eos_token_id:
                            break

                    gen_answer = tokenizer.decode(
                        curr_ids[0, prompt_ids.size(1):], skip_special_tokens=True
                    ).strip()

                    is_correct = (expected_val in gen_answer) or gen_answer.startswith(expected_val)
                    if is_correct:
                        correct += 1

                if sched_mode is not None and model.cms is not None:
                    model.reset_memory()

            acc = (correct / num_samples) * 100.0
            mean_prob = sum(target_probs) / max(1, len(target_probs))
            mean_rank = sum(target_ranks) / max(1, len(target_ranks))
            top_common = max(set(top1_predictions), key=top1_predictions.count)

            results_summary[cond][method_name] = {
                "accuracy": acc,
                "target_prob": mean_prob,
                "target_rank": mean_rank,
                "most_frequent_top1": top_common,
            }

            print(
                f"  [{method_name:30s}] Acc: {acc:5.1f}% | "
                f"Target Prob: {mean_prob:.5f} | "
                f"Target Rank: {mean_rank:6.1f} | "
                f"Top-1 Token: '{top_common}'"
            )

    print("\n" + "=" * 80)
    print("TASK 5 EXPERIMENT COMPLETE - SUMMARY TABLE")
    print("=" * 80)
    print(f"{'Condition':18s} | {'Method':30s} | {'Acc (%)':7s} | {'Target Prob':11s} | {'Target Rank':11s}")
    print("-" * 85)
    for cond, methods_dict in results_summary.items():
        for m_name, metrics in methods_dict.items():
            print(
                f"{cond:18s} | {m_name:30s} | {metrics['accuracy']:7.1f} | "
                f"{metrics['target_prob']:11.5f} | {metrics['target_rank']:11.1f}"
            )

    return results_summary


if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    run_template_overfitting_analysis(num_samples=30, device=device)
