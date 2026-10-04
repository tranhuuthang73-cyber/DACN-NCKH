import sys, os, re, json, tempfile, shutil
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hybrid_qa.test_corpus import get_test_documents, get_100_test_questions
from src.hybrid_qa.chunker import DocumentChunker
from src.hybrid_qa.retriever import BM25Retriever
from src.hybrid_qa.document_store import DocumentStore

STOPWORDS = {'là', 'của', 'và', 'các', 'có', 'trong', 'được', 'cho', 'những', 'với', 'khi', 'ở', 'nào', 'gì', 'sao', 'thế', 'này', 'đó', 'ra', 'vào', 'từ', 'theo', 'đã', 'sẽ', 'đang', 'như', 'thì', 'ai', 'nhiêu', 'bao', 'nơi', 'mỗi', 'lại', 'qua', 'bởi', 'do', 'để', 'rằng', 'the', 'is', 'are', 'a', 'an', 'of', 'in', 'to', 'for', 'with', 'on', 'at', 'by', 'from', 'and', 'or', 'what', 'which', 'how', 'when', 'where', 'who'}

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

print("Answerable with coverage < 0.40:")
for q in questions[:50]:
    q_tokens = get_content_tokens(q['question'])
    res = retriever.retrieve(q['question'], top_k=3)
    cov = max([len(q_tokens & get_content_tokens(r.text))/max(1, len(q_tokens)) for r in res]) if res else 0
    if cov < 0.40:
        print(f"  {q['question_id']}: cov={cov:.2f}, text=\"{q['question']}\"")

print("\nUnanswerable with coverage >= 0.40:")
for q in questions[50:75]:
    q_tokens = get_content_tokens(q['question'])
    res = retriever.retrieve(q['question'], top_k=3)
    cov = max([len(q_tokens & get_content_tokens(r.text))/max(1, len(q_tokens)) for r in res]) if res else 0
    if cov >= 0.40:
        print(f"  {q['question_id']}: cov={cov:.2f}, text=\"{q['question']}\"")

print("\nInsufficient with coverage >= 0.40:")
for q in questions[75:100]:
    q_tokens = get_content_tokens(q['question'])
    res = retriever.retrieve(q['question'], top_k=3)
    cov = max([len(q_tokens & get_content_tokens(r.text))/max(1, len(q_tokens)) for r in res]) if res else 0
    if cov >= 0.40:
        print(f"  {q['question_id']}: cov={cov:.2f}, text=\"{q['question']}\"")

shutil.rmtree(d)
