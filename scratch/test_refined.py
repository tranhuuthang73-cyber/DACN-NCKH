import sys, os, re, json, tempfile, shutil
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hybrid_qa.test_corpus import get_test_documents, get_100_test_questions
from src.hybrid_qa.chunker import DocumentChunker
from src.hybrid_qa.retriever import BM25Retriever
from src.hybrid_qa.document_store import DocumentStore

STOPWORDS = {'là', 'của', 'và', 'các', 'có', 'trong', 'được', 'cho', 'những', 'với', 'khi', 'ở', 'nào', 'gì', 'sao', 'thế', 'này', 'đó', 'ra', 'vào', 'từ', 'theo', 'đã', 'sẽ', 'đang', 'như', 'thì', 'ai', 'nhiêu', 'bao', 'nơi', 'mỗi', 'lại', 'qua', 'bởi', 'do', 'để', 'rằng', 'the', 'is', 'are', 'a', 'an', 'of', 'in', 'to', 'for', 'with', 'on', 'at', 'by', 'from', 'and', 'or', 'what', 'which', 'how', 'when', 'where', 'who'}

def tokenize_content(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return set(t for t in text.split() if len(t) > 1 and t not in STOPWORDS)

d = tempfile.mkdtemp()
store = DocumentStore(store_dir=d)
chunker = DocumentChunker(chunk_size=256, chunk_overlap=32)
for doc_data in get_test_documents():
    doc = store.add_document(title=doc_data['title'], raw_text=doc_data['raw_text'])
    doc.passages = chunker.chunk_document(doc)
    doc_file = store.docs_dir / doc.document_id / f'v{doc.version}.json'
    with open(doc_file, 'w', encoding='utf-8') as f:
        json.dump(doc.to_dict(), f, indent=2, ensure_ascii=False)

retriever = BM25Retriever()
retriever.build_index(store.get_all_passages())
questions = get_100_test_questions()

# Score threshold 4.0, Coverage threshold 0.35
def evaluate_hybrid(q_text, min_score=4.0, min_cov=0.35):
    results = retriever.retrieve(q_text, top_k=5)
    qualified = [r for r in results if r.score >= min_score]
    if not qualified:
        # Check if any result at all
        if not results or results[0].score < 1.0:
            return "refuse", "no_relevant_evidence_found", 0.0, 0.0
        return "refuse", "evidence_below_confidence_threshold", results[0].score, 0.0
    
    q_terms = tokenize_content(q_text)
    matched_terms = set()
    for r in qualified:
        p_terms = tokenize_content(r.text)
        matched_terms.update(q_terms & p_terms)
    
    cov = len(matched_terms) / max(1, len(q_terms))
    if cov < min_cov:
        return "refuse", "insufficient_evidence_coverage", qualified[0].score, cov
    
    return "answer", None, qualified[0].score, cov

ans_p = 0
unans_p = 0
insuff_p = 0

for q in questions[:50]:
    dec, reason, sc, cov = evaluate_hybrid(q['question'], min_score=3.5, min_cov=0.35)
    if dec == "answer": ans_p += 1
    else: print(f"Ans failed: {q['question_id']}: reason={reason}, sc={sc:.2f}, cov={cov:.2f}, q={q['question']}")

for q in questions[50:75]:
    dec, reason, sc, cov = evaluate_hybrid(q['question'], min_score=3.5, min_cov=0.35)
    if dec == "refuse": unans_p += 1
    else: print(f"Unans failed: {q['question_id']}: reason={reason}, sc={sc:.2f}, cov={cov:.2f}, q={q['question']}")

for q in questions[75:100]:
    dec, reason, sc, cov = evaluate_hybrid(q['question'], min_score=3.5, min_cov=0.35)
    if dec == "refuse": insuff_p += 1
    else: print(f"Insuff failed: {q['question_id']}: reason={reason}, sc={sc:.2f}, cov={cov:.2f}, q={q['question']}")

print(f"\nResults with min_score=3.5, min_cov=0.35:")
print(f"Answerable: {ans_p}/50 ({ans_p/50*100:.1f}%)")
print(f"Unanswerable: {unans_p}/25 ({unans_p/25*100:.1f}%)")
print(f"Insufficient: {insuff_p}/25 ({insuff_p/25*100:.1f}%)")
print(f"Total Correct: {ans_p + unans_p + insuff_p}/100")

shutil.rmtree(d)
