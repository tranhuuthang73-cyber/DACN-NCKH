import sys, os, re, json, tempfile, shutil
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hybrid_qa.test_corpus import get_test_documents, get_100_test_questions
from src.hybrid_qa.chunker import DocumentChunker
from src.hybrid_qa.retriever import BM25Retriever
from src.hybrid_qa.document_store import DocumentStore

STOPWORDS = {'là', 'của', 'và', 'các', 'có', 'trong', 'được', 'cho', 'những', 'với', 'khi', 'ở', 'nào', 'gì', 'sao', 'thế', 'này', 'đó', 'ra', 'vào', 'từ', 'theo', 'đã', 'sẽ', 'đang', 'như', 'thì', 'ai', 'nhiêu', 'bao', 'nơi', 'mỗi', 'lại', 'qua', 'bởi', 'do', 'để', 'rằng', 'thì', 'the', 'is', 'are', 'a', 'an', 'of', 'in', 'to', 'for', 'with', 'on', 'at', 'by', 'from', 'and', 'or', 'what', 'which', 'how', 'when', 'where', 'who'}

def get_content_tokens(text):
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

print("Analyzing Query Content-Term Coverage on Top-1 Retrieved Passage:\n")

def check_coverage(q_list):
    coverages = []
    for q in q_list:
        q_tokens = get_content_tokens(q['question'])
        if not q_tokens:
            coverages.append(0.0)
            continue
        results = retriever.retrieve(q['question'], top_k=3)
        if not results:
            coverages.append(0.0)
            continue
        # Check max coverage among top passages
        max_cov = 0.0
        for r in results:
            p_tokens = get_content_tokens(r.text)
            cov = len(q_tokens & p_tokens) / len(q_tokens)
            if cov > max_cov:
                max_cov = cov
        coverages.append(max_cov)
    return coverages

ans_cov = check_coverage(questions[:50])
unans_cov = check_coverage(questions[50:75])
insuff_cov = check_coverage(questions[75:100])

print(f"Answerable Coverage: min={min(ans_cov):.2f}, mean={sum(ans_cov)/len(ans_cov):.2f}, max={max(ans_cov):.2f}")
print(f"Unanswerable Coverage: min={min(unans_cov):.2f}, mean={sum(unans_cov)/len(unans_cov):.2f}, max={max(unans_cov):.2f}")
print(f"Insufficient Coverage: min={min(insuff_cov):.2f}, mean={sum(insuff_cov)/len(insuff_cov):.2f}, max={max(insuff_cov):.2f}")

threshold = 0.50
print(f"\nWith Coverage Threshold = {threshold}:")
ans_pass = sum(1 for c in ans_cov if c >= threshold)
unans_refuse = sum(1 for c in unans_cov if c < threshold)
insuff_refuse = sum(1 for c in insuff_cov if c < threshold)

print(f"Answerable passing (Answer): {ans_pass}/50 ({ans_pass/50*100:.1f}%)")
print(f"Unanswerable correctly refused: {unans_refuse}/25 ({unans_refuse/25*100:.1f}%)")
print(f"Insufficient correctly refused: {insuff_refuse}/25 ({insuff_refuse/25*100:.1f}%)")
print(f"Total Correct: {ans_pass + unans_refuse + insuff_refuse}/100")

shutil.rmtree(d)
