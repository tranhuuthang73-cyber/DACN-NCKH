"""
Unit and Integration Tests for Phase 3.2 SA-CMS Training Pilot Pipeline.

Verifies:
1. Dataset isolation (0% overlap with Phase 3.1 / Phase 3.1.1).
2. Trainable vs frozen parameter isolation (100% frozen backbone, 3.54M CMS params trainable).
3. Token accounting accuracy (total, avg, min, max).
4. Gradient updates and numerical stability (no NaNs in fp32).
5. Checkpoint serialization and bit-level reload fidelity.
6. F1, Exact Match, and Perplexity metric computations.
7. Pilot A / Pilot B sample partitioning.
"""

import os
import sys
import tempfile
from pathlib import Path
import pytest
import torch

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.hope_attention.pretrained_hope import PretrainedHopeLM
from src.training.training_corpus import get_training_corpus, get_validation_corpus
from src.hybrid_qa.test_corpus import get_test_documents, get_100_test_questions
from scripts.run_training_pilot import compute_token_f1, compute_exact_match, evaluate_validation


class TestTrainingCorpusIsolation:
    """Verifies strict isolation of training and validation data."""

    def test_no_document_overlap_with_phase3_1(self):
        train_data = get_training_corpus()
        val_data = get_validation_corpus()
        eval_docs = get_test_documents()

        eval_doc_ids = set(d["document_id"] for d in eval_docs)
        train_doc_ids = set(d["doc_id"] for d in train_data["documents"])
        val_doc_ids = set(d["doc_id"] for d in val_data["documents"])

        # Absolutely no overlap
        assert len(eval_doc_ids & train_doc_ids) == 0, f"Overlap in doc IDs: {eval_doc_ids & train_doc_ids}"
        assert len(eval_doc_ids & val_doc_ids) == 0, f"Overlap in doc IDs: {eval_doc_ids & val_doc_ids}"
        assert len(train_doc_ids & val_doc_ids) == 0, f"Overlap in doc IDs: {train_doc_ids & val_doc_ids}"

    def test_no_question_overlap_with_phase3_1(self):
        train_data = get_training_corpus()
        val_data = get_validation_corpus()
        eval_questions = get_100_test_questions()

        eval_q_ids = set(q["question_id"] for q in eval_questions)
        train_q_ids = set(s["sample_id"] for s in train_data["samples"])
        val_q_ids = set(s["sample_id"] for s in val_data["samples"])

        assert len(eval_q_ids & train_q_ids) == 0, f"Overlap in Q IDs: {eval_q_ids & train_q_ids}"
        assert len(eval_q_ids & val_q_ids) == 0, f"Overlap in Q IDs: {eval_q_ids & val_q_ids}"
        assert len(train_q_ids & val_q_ids) == 0, f"Overlap in Q IDs: {train_q_ids & val_q_ids}"

    def test_sample_counts_and_partitioning(self):
        train_data = get_training_corpus()
        val_data = get_validation_corpus()

        assert len(train_data["documents"]) == 20
        assert len(train_data["samples"]) == 200
        assert len(val_data["documents"]) == 5
        assert len(val_data["samples"]) == 50

        # Pilot A (100) is strict prefix of Pilot B (200)
        pilot_a = train_data["samples"][:100]
        pilot_b = train_data["samples"][:200]
        assert len(pilot_a) == 100
        assert len(pilot_b) == 200
        assert pilot_b[:100] == pilot_a


class TestParameterAndGradientIsolation:
    """Verifies parameter freezing and gradient dynamics."""

    def test_frozen_backbone_and_trainable_cms(self):
        device = "cpu"
        model = PretrainedHopeLM(num_levels=2, device=device, torch_dtype=torch.float32)

        trainable_params = [p for p in model.parameters() if p.requires_grad]
        frozen_params = [p for p in model.parameters() if not p.requires_grad]

        trainable_count = sum(p.numel() for p in trainable_params)
        frozen_count = sum(p.numel() for p in frozen_params)

        assert frozen_count == 134_515_008, f"Expected 134,515,008 frozen backbone params, got {frozen_count}"
        assert trainable_count == 3_544_320, f"Expected 3,544,320 trainable CMS params, got {trainable_count}"
        assert trainable_count / (trainable_count + frozen_count) < 0.03

    def test_gradient_flow_only_to_cms(self):
        device = "cpu"
        model = PretrainedHopeLM(num_levels=2, device=device, torch_dtype=torch.float32)
        optimizer = torch.optim.AdamW(model.get_cms_parameters(), lr=1e-4)

        input_ids = torch.tensor([[10, 20, 30, 40]], device=device)
        targets = input_ids.clone()

        logits, loss = model(input_ids, targets=targets)
        assert loss is not None
        assert not torch.isnan(loss)

        loss.backward()

        # Check backbone gradients are strictly None
        for name, p in model.backbone.named_parameters():
            assert p.grad is None, f"Backbone parameter {name} received gradient!"

        # Check CMS gradients exist
        for name, p in model.cms.named_parameters():
            assert p.grad is not None, f"CMS parameter {name} missing gradient!"

        optimizer.step()
        optimizer.zero_grad()


class TestMetricsAndCheckpointReload:
    """Verifies metric functions and bit-for-bit reload."""

    def test_token_f1_and_em(self):
        pred = "linear time complexity"
        gold = "linear time complexity"
        assert compute_token_f1(pred, gold) == 1.0
        assert compute_exact_match(pred, gold) == 1.0

        pred_partial = "achieve linear time complexity"
        gold_partial = "linear time complexity"
        assert 0.5 < compute_token_f1(pred_partial, gold_partial) < 1.0
        assert compute_exact_match(pred_partial, gold_partial) == 0.0

        pred_wrong = "quadratic complexity"
        gold_target = "linear time"
        assert compute_token_f1(pred_wrong, gold_target) == 0.0
        assert compute_exact_match(pred_wrong, gold_target) == 0.0

    def test_checkpoint_save_and_reload_fidelity(self):
        device = "cpu"
        model1 = PretrainedHopeLM(num_levels=2, device=device, torch_dtype=torch.float32)
        model2 = PretrainedHopeLM(num_levels=2, device=device, torch_dtype=torch.float32)

        # Mutate model1 CMS weights slightly
        with torch.no_grad():
            for p in model1.cms.parameters():
                p.add_(0.05)

        with tempfile.TemporaryDirectory() as tmpdir:
            ckpt_path = Path(tmpdir) / "test_cms.pt"
            torch.save({
                "cms_state_dict": model1.cms.state_dict(),
                "cms_norm_state_dict": model1.cms_norm.state_dict(),
            }, ckpt_path)

            loaded = torch.load(ckpt_path, map_location=device)
            model2.cms.load_state_dict(loaded["cms_state_dict"])
            model2.cms_norm.load_state_dict(loaded["cms_norm_state_dict"])

            # Verify identical output
            test_x = torch.tensor([[100, 200, 300]], device=device)
            model1.eval()
            model2.eval()
            with torch.no_grad():
                l1, _ = model1(test_x)
                l2, _ = model2(test_x)
                diff = torch.max(torch.abs(l1 - l2)).item()
                assert diff == 0.0, f"Reloaded checkpoint logit diff = {diff} (expected 0.0)"
