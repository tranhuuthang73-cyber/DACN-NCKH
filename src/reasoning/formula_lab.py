"""
Self-Built Symbolic Formula Transformation, Worked Example & Exercise Generator.

100% Local Self-Built using SymPy + Python stdlib + symbolic_solver.py.
ZERO external LLM/AI API calls.
Powers the Online Study Expansion mode vs strict Document-Locked Offline mode:
  - Offline: answers strictly within uploaded documents.
  - Online (Mở rộng & Bài tập): detects mathematical/scientific formulas (including
    LaTeX/OMML equations, calculus functions, 2-variable linear systems, algebraic
    laws, and numeric word-problem examples) in the attached document, derives exact
    symbolic transformations via SymPy (solve, diff, integrate, expand, factor),
    generates fresh verified worked examples, and creates progressive exercises.
"""

from __future__ import annotations

import re
import unicodedata
from fractions import Fraction
from typing import Any, Dict, List, Optional, Sequence, Tuple

import sympy as sp
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from src.reasoning.symbolic_solver import solve_quadratic


def _strip_accents(text: str) -> str:
    if not text:
        return ""
    s = unicodedata.normalize("NFD", text)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D")


def _normalize_latex_math(text: str) -> str:
    """
    Normalizes common LaTeX / Word OMML math notation into clean SymPy-friendly syntax
    without breaking surrounding Vietnamese prose.
    """
    if not text:
        return ""
    s = text
    # Strip math delimiters and sizing directives
    s = s.replace("$$", " ").replace("$", " ")
    s = re.sub(r"\\(?:left|right|displaystyle|quad|qquad)\b", "", s)
    # Unwrap \text{...} and \mathrm{...}
    s = re.sub(r"\\(?:text|mathrm|mathbf)\{([^{}]*)\}", r"\1", s)
    # Convert \frac{A}{B} iteratively (supports up to 5 levels of nesting)
    for _ in range(5):
        new_s = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", s)
        if new_s == s:
            break
        s = new_s
    # Convert \sqrt{A} -> sqrt(A)
    for _ in range(3):
        new_s = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", s)
        if new_s == s:
            break
        s = new_s
    # Replace LaTeX / Unicode operators
    s = re.sub(r"\\(?:cdot|times)\b", " * ", s)
    s = re.sub(r"\\div\b", " / ", s)
    s = s.replace("×", " * ").replace("·", " * ").replace("÷", " / ")
    s = s.replace("−", "-").replace("–", "-")
    # Convert ^{exp} -> ^(exp) and simple subscripts m_{1} -> m_1
    s = re.sub(r"\^\{([^{}]+)\}", r"^(\1)", s)
    s = re.sub(r"_\{([A-Za-z0-9]+)\}", r"_\1", s)
    return s


def detect_expansion_intent(query: str) -> Dict[str, Any]:
    """
    Detects explicit requests to transform formulas, compute symbolic calculus/algebra,
    generate NEW examples, or create practice exercises beyond static document text.
    Ordinary factual/example lookups inside the document return wants_any=False.
    """
    q_norm = _strip_accents((query or "").lower()).strip()
    q_norm = re.sub(r"\s+", " ", q_norm)

    transform_cues = (
        "bien doi cong thuc", "chuyen ve cong thuc", "rut an", "rut bien",
        "cong thuc suy ra", "sinh them cong thuc", "them cong thuc",
        "cong thuc khac", "cong thuc lien quan", "cong thuc tuong tu",
        "bien doi tuong duong", "cong thuc dao nguoc", "rut gon cong thuc",
        "rut gon bieu thuc", "dao ham", "tich phan", "nguyen ham",
        "khai trien", "phan tich nhan tu", "giai he phuong trinh",
        "he phuong trinh tuong tu", "giai bat ky",
    )
    example_cues = (
        "sinh them vi du", "cho them vi du", "them vi du", "vi du khac",
        "vi du moi", "vi du tuong tu", "tao vi du", "minh hoa them",
        "cho vi du bai tap", "vi du bai tap", "cho vi du moi", "cho vi du tuong tu",
    )
    exercise_cues = (
        "sinh them bai tap", "tao bai tap", "cho bai tap", "them bai tap",
        "cho them bai tap", "bai tap tuong tu", "bai tap luyen tap", "bai tap van dung",
        "bai tap moi", "de bai tap", "luyen tap them", "ra de bai tap",
        "vi du bai tap", "bai tap ve",
    )

    wants_transform = any(c in q_norm for c in transform_cues)
    wants_example = any(c in q_norm for c in example_cues)
    wants_exercise = any(c in q_norm for c in exercise_cues)
    wants_any = wants_transform or wants_example or wants_exercise

    return {
        "wants_any": wants_any,
        "transform_formula": wants_transform,
        "new_example": wants_example,
        "practice_exercise": wants_exercise,
    }


_EQ_CANDIDATE_RE = re.compile(
    r"(?<![A-Za-z0-9_<>!=])([A-Za-z][A-Za-z0-9_]{0,5})\s*=\s*([^\n;.,!?]{3,70})"
)
_FUNC_CANDIDATE_RE = re.compile(
    r"(?<![A-Za-z0-9_<>!=])([fghFGH]\(\s*([a-z])\s*\)|y)\s*=\s*([^\n;.,!?]{3,75})"
)
_LINEAR_XY_RE = re.compile(
    r"(?<![A-Za-z0-9_])([+-]?\s*(?:\d*\s*\*?\s*[xy]\s*[+-]\s*)+(?:\d*\s*\*?\s*[xy]))\s*=\s*([+-]?\s*\d+(?:\.\d+)?)"
)
_SYMPY_TRANSFORMS = standard_transformations + (implicit_multiplication_application,)
_MATH_FUNCS = {"sqrt", "sin", "cos", "tan", "log", "ln", "exp"}


def _has_prose_words(expr_str: str) -> bool:
    words = re.findall(r"[A-Za-z_]{2,}", expr_str)
    for w in words:
        w_low = w.lower()
        if w_low in _MATH_FUNCS:
            continue
        # Allow short subscripted physics/chem symbols like m_1, C_M, E_k, v_0, R_1
        if re.match(r"^[A-Za-z]_[A-Za-z0-9]{1,3}$", w):
            continue
        return True
    return False


def _trim_vn_trailing(rhs_s: str) -> str:
    rhs_s = re.split(
        r"\s+(?:với|khi|nếu|trong\s+đó|tại|và|hoặc|là)\b",
        rhs_s,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0].strip()
    return rhs_s.rstrip(".,;:")


def _safe_parse_equation(lhs_str: str, rhs_str: str) -> Optional[Dict[str, Any]]:
    """Safely parses clean algebraic equations (including LaTeX-normalized ones) into SymPy objects."""
    lhs_c = lhs_str.strip().replace("^", "**")
    rhs_c = rhs_str.strip().replace("^", "**")
    if not lhs_c or not rhs_c:
        return None
    if any(bad in rhs_c for bad in ("->", ">=", "<=", "mod ", "{", "}", "[", "]", "?", "\"", "'", "=")):
        return None
    if _has_prose_words(rhs_c):
        return None

    toks = set(re.findall(r"[A-Za-z][A-Za-z0-9_]*", f"{lhs_c} {rhs_c}"))
    # Avoid imaginary unit 'I' colliding with electrical current symbol I
    local_env: Dict[str, Any] = {
        tok: sp.Symbol(tok, real=True, nonzero=True)
        for tok in toks
        if tok.lower() not in _MATH_FUNCS
    }
    try:
        lhs_expr = parse_expr(lhs_c, local_dict=local_env, transformations=_SYMPY_TRANSFORMS, evaluate=True)
        rhs_expr = parse_expr(rhs_c, local_dict=local_env, transformations=_SYMPY_TRANSFORMS, evaluate=True)
    except Exception:
        return None

    free_syms = sorted(list((lhs_expr - rhs_expr).free_symbols), key=lambda s: s.name)
    if len(free_syms) < 2 or len(free_syms) > 5:
        return None

    return {
        "kind": "algebraic_eq",
        "raw": f"{lhs_str.strip()} = {rhs_str.strip()}",
        "lhs": lhs_expr,
        "rhs": rhs_expr,
        "symbols": free_syms,
    }


def _safe_parse_calculus_func(func_lhs: str, var_name: str, rhs_str: str) -> Optional[Dict[str, Any]]:
    """Safely parses single-variable functions f(x) = ... or y = <nonlinear/poly expr in x>."""
    rhs_c = _trim_vn_trailing(rhs_str).replace("^", "**")
    if not rhs_c or any(bad in rhs_c for bad in ("->", ">=", "<=", "mod ", "{", "}", "[", "]", "?", "\"", "'", "=")):
        return None
    if _has_prose_words(rhs_c):
        return None
    var_sym = sp.Symbol(var_name, real=True)
    local_env: Dict[str, Any] = {
        var_name: var_sym,
        "sqrt": sp.sqrt,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "log": sp.log,
        "ln": sp.log,
        "exp": sp.exp,
    }
    try:
        expr = parse_expr(rhs_c, local_dict=local_env, transformations=_SYMPY_TRANSFORMS, evaluate=True)
    except Exception:
        return None
    if expr.free_symbols != {var_sym}:
        return None
    # For plain `y = ...`, require non-linear or transcendental function (avoid simple y = 2x + 1 colliding with lines)
    if func_lhs.strip() == "y":
        try:
            poly = sp.Poly(expr, var_sym)
            if poly.total_degree() < 2:
                return None
        except Exception:
            pass
    return {
        "kind": "calculus_func",
        "raw": f"{func_lhs.strip()} = {rhs_str.strip()}",
        "func_name": func_lhs.strip(),
        "var": var_sym,
        "expr": expr,
    }


def _extract_linear_system(norm_text: str) -> Optional[Dict[str, Any]]:
    """Detects a pair of 2-variable linear equations in (x, y) with a unique SymPy solution."""
    x, y = sp.symbols("x y", real=True)
    local_env = {"x": x, "y": y}
    parsed_eqs: List[Tuple[str, sp.Eq, sp.Expr]] = []
    seen_exprs: set = set()

    for m in _LINEAR_XY_RE.finditer(norm_text):
        lhs_raw = m.group(1).strip()
        rhs_raw = m.group(2).strip()
        if "x" not in lhs_raw.lower() and "y" not in lhs_raw.lower():
            continue
        try:
            lhs_e = parse_expr(lhs_raw.replace("^", "**"), local_dict=local_env, transformations=_SYMPY_TRANSFORMS)
            rhs_e = parse_expr(rhs_raw, local_dict=local_env, transformations=_SYMPY_TRANSFORMS)
            diff_e = sp.expand(lhs_e - rhs_e)
            poly = sp.Poly(diff_e, x, y)
            if poly.total_degree() != 1:
                continue
            sig = sp.srepr(diff_e)
            if sig not in seen_exprs:
                seen_exprs.add(sig)
                parsed_eqs.append((f"{lhs_raw} = {rhs_raw}", sp.Eq(lhs_e, rhs_e), diff_e))
        except Exception:
            continue

    if len(parsed_eqs) < 2:
        return None

    for i in range(len(parsed_eqs)):
        for j in range(i + 1, len(parsed_eqs)):
            raw1, eq1, d1 = parsed_eqs[i]
            raw2, eq2, d2 = parsed_eqs[j]
            try:
                sol = sp.solve([eq1, eq2], (x, y), dict=True)
            except Exception:
                sol = []
            if sol and x in sol[0] and y in sol[0]:
                return {
                    "kind": "linear_system",
                    "raw": f"{raw1}; {raw2}",
                    "raw1": raw1,
                    "raw2": raw2,
                    "eq1": eq1,
                    "eq2": eq2,
                    "diff1": d1,
                    "diff2": d2,
                    "solution": sol[0],
                }
    return None


def _infer_formulas_from_word_examples(raw_text: str, existing_kinds: set) -> List[Dict[str, Any]]:
    """
    When a document describes numeric worked examples in prose without explicit `=` equations,
    infers the governing canonical formula so SymPy can still derive inversions, examples & exercises.
    """
    if not re.search(r"\d", raw_text or ""):
        return []
    low_ascii = _strip_accents((raw_text or "").lower())
    inferred: List[Dict[str, Any]] = []

    # 1. Kinematics: v = s / t
    if (
        any(k in low_ascii for k in ("quang duong", "van toc", "km/h", "m/s"))
        and any(k in low_ascii for k in ("thoi gian", "gio", "giay", "km", "met"))
    ):
        v, s, t = sp.symbols("v s t", real=True, nonzero=True)
        inferred.append(
            {
                "kind": "algebraic_eq",
                "raw": "v = s / t",
                "lhs": v,
                "rhs": s / t,
                "symbols": [s, t, v],
                "inferred_from_example": True,
                "domain_label": "Chuyển động đều (Vận tốc - Quãng đường - Thời gian)",
            }
        )

    # 2. Solution Molarity: C_M = n / V
    if (
        any(k in low_ascii for k in ("nong do mol", "mol/l", "dung dich"))
        and any(k in low_ascii for k in ("mol", "lit", "ml"))
    ):
        cm, n_s, vol = sp.symbols("C_M n V", real=True, nonzero=True)
        inferred.append(
            {
                "kind": "algebraic_eq",
                "raw": "C_M = n / V",
                "lhs": cm,
                "rhs": n_s / vol,
                "symbols": [cm, vol, n_s],
                "inferred_from_example": True,
                "domain_label": "Nồng độ mol dung dịch (Hóa học)",
            }
        )

    # 3. Molar mass relationship: n = m / M (when not already covered by redox)
    if (
        "chemistry_redox" not in existing_kinds
        and any(k in low_ascii for k in ("khoi luong mol", "g/mol", "so mol"))
        and any(k in low_ascii for k in ("gam", "mol"))
    ):
        n_s, m_s, M_s = sp.symbols("n m M", real=True, nonzero=True)
        inferred.append(
            {
                "kind": "algebraic_eq",
                "raw": "n = m / M",
                "lhs": n_s,
                "rhs": m_s / M_s,
                "symbols": [M_s, m_s, n_s],
                "inferred_from_example": True,
                "domain_label": "Liên hệ Số mol - Khối lượng - Khối lượng mol",
            }
        )

    # 4. Simple interest / growth: A = P * (1 + r * t)
    if (
        any(k in low_ascii for k in ("lai suat", "tien goc", "von dau tu"))
        and ("%" in (raw_text or "") or "nam" in low_ascii or "thang" in low_ascii)
    ):
        A_s, P_s, r_s, t_s = sp.symbols("A P r t", real=True, nonzero=True)
        inferred.append(
            {
                "kind": "algebraic_eq",
                "raw": "A = P * (1 + r * t)",
                "lhs": A_s,
                "rhs": P_s * (1 + r_s * t_s),
                "symbols": [A_s, P_s, r_s, t_s],
                "inferred_from_example": True,
                "domain_label": "Lãi suất đơn (Tài chính - Toán ứng dụng)",
            }
        )

    return inferred


def extract_document_formulas(raw_text: str) -> List[Dict[str, Any]]:
    """Extracts structured formula families present in the attached document."""
    text = raw_text or ""
    norm_text = _normalize_latex_math(text)
    low = norm_text.lower()
    low_ascii = _strip_accents(low)
    found: List[Dict[str, Any]] = []
    seen_keys: set = set()

    # 1. Redox & Electron Conservation Chemistry
    if any(
        k in low_ascii
        for k in ("bao toan electron", "nhuong electron", "nhan electron", "oxi hoa - khu", "n(e nhuong)")
    ):
        found.append(
            {
                "kind": "chemistry_redox",
                "raw": "Σ n(e nhường) = Σ n(e nhận)",
                "molar_vol": 24.79 if ("24,79" in text or "24.79" in text or "đkc" in low) else 22.4,
            }
        )
        seen_keys.add("chemistry_redox")

    # 2. Quadratic equation & Vieta
    if (
        re.search(r"a\s*\*?\s*x\s*\^?\s*\(?2\)?\s*\+\s*b\s*\*?\s*x\s*\+\s*c\s*=\s*0", low)
        or re.search(r"x\s*\^\s*\(?2\)?\s*[+\-].*=\s*0", low)
        or "phuong trinh bac hai" in low_ascii
        or "delta = b^2 - 4ac" in low
        or "hệ thức vi-ét" in low
        or "vi-et" in low_ascii
    ):
        found.append(
            {
                "kind": "quadratic",
                "raw": "ax^2 + bx + c = 0 (a ≠ 0)",
            }
        )
        seen_keys.add("quadratic")

    # 3. Classical modular cryptography
    if "mod 26" in low_ascii or re.search(r"e\(?x\)?\s*=.*mod\s+\d+", low_ascii):
        is_affine = ("a * x + b" in low_ascii) or ("ax + b" in low_ascii) or ("affine" in low_ascii)
        found.append(
            {
                "kind": "crypto_mod",
                "variant": "affine" if is_affine else "caesar",
                "raw": "e(x) = (a * x + b) mod 26" if is_affine else "e_k(x) = (x + k) mod 26",
            }
        )
        seen_keys.add("crypto_mod")

    # 4. 2-variable linear system (e.g. 2x + y = 5 and x - y = 1)
    lin_sys = _extract_linear_system(norm_text)
    if lin_sys is not None:
        found.append(lin_sys)
        seen_keys.add("linear_system")

    # 5. Single-variable calculus / polynomial functions (f(x) = ..., y = x^3 - 3x + 2)
    for fm in _FUNC_CANDIDATE_RE.finditer(norm_text):
        func_lhs = fm.group(1).strip()
        var_name = (fm.group(2) or "x").strip()
        rhs_s = fm.group(3).strip()
        parsed_fn = _safe_parse_calculus_func(func_lhs, var_name, rhs_s)
        if parsed_fn is not None:
            fn_sig = f"calc::{sp.srepr(sp.simplify(parsed_fn['expr']))}"
            if fn_sig not in seen_keys:
                seen_keys.add(fn_sig)
                seen_keys.add("calculus_func")
                found.append(parsed_fn)

    # 6. General symbolic equations LHS = RHS (e.g. U = I * R, E = 1/2 m v^2, F = G*m_1*m_2/r^2)
    for m in _EQ_CANDIDATE_RE.finditer(norm_text):
        lhs_s = m.group(1).strip()
        rhs_s = _trim_vn_trailing(m.group(2))
        if lhs_s.lower() in {"f", "g", "h"} and f"{lhs_s}(" in norm_text:
            continue
        parsed = _safe_parse_equation(lhs_s, rhs_s)
        if parsed is not None:
            sig = sp.srepr(sp.simplify(parsed["lhs"] - parsed["rhs"]))
            if sig not in seen_keys and not any(
                k in ("quadratic", "crypto_mod") for k in seen_keys if parsed["raw"].startswith(("a", "x", "e"))
            ):
                seen_keys.add(sig)
                found.append(parsed)

    # 7. Word-problem / numeric example inference when no explicit algebraic equation covers the domain
    if not any(f.get("kind") in ("algebraic_eq", "calculus_func", "linear_system") for f in found):
        inferred = _infer_formulas_from_word_examples(text, seen_keys)
        for inf_item in inferred:
            sig = sp.srepr(sp.simplify(inf_item["lhs"] - inf_item["rhs"]))
            if sig not in seen_keys:
                seen_keys.add(sig)
                found.append(inf_item)

    return found


def _fmt_sym(expr: Any) -> str:
    return str(expr).replace("**", "^")


def derive_formula_transformations(formulas: Sequence[Dict[str, Any]]) -> List[str]:
    """Derives exact symbolic transformations via SymPy (solve, diff, integrate, expand, factor)."""
    lines: List[str] = []
    for item in formulas:
        kind = item.get("kind")
        if kind == "chemistry_redox":
            mv = item.get("molar_vol", 24.79)
            mv_s = str(mv).replace(".", ",")
            lines.extend(
                [
                    "- **Công thức gốc trong tài liệu:** ∑ n(e nhường) = ∑ n(e nhận)",
                    "- **Biến đổi dạng tổng quát cho kim loại M (hóa trị a) tác dụng tạo sản phẩm khử K (nhận b electron):** `a * n(M) = b * n(K)`",
                    "- **Rút số mol chất khử / khối lượng kim loại:** `n(M) = (b / a) * n(K)` => `m(M) = M_kim_loại * (b / a) * n(K)`",
                    f"- **Liên hệ thể tích khí ở ĐKC:** `V_K = n(K) * {mv_s}` => `n(K) = V_K / {mv_s}`, suy ra `n(M) = (b * V_K) / (a * {mv_s})`",
                    "- **Tính nhanh khối lượng muối nitrat tạo thành (không tạo NH4NO3):** `m_muối = m_kim_loại + 62 * n(e trao đổi)`",
                ]
            )
        elif kind == "quadratic":
            lines.extend(
                [
                    "- **Phương trình gốc:** `ax^2 + bx + c = 0 (a ≠ 0)`",
                    "- **Dạng chuẩn hóa (chia a) & tách bình phương:** `(x + b/(2a))^2 = Delta / (4a^2)` với `Delta = b^2 - 4ac`",
                    "- **Công thức nghiệm (khi Delta >= 0):** `x1,2 = (-b ± sqrt(b^2 - 4ac)) / (2a)`",
                    "- **Biến đổi sang hệ thức Vi-ét & phân tích nhân tử:** `S = x1 + x2 = -b/a`, `P = x1*x2 = c/a` và `a(x - x1)(x - x2) = 0`",
                    "- **Suy ngược đa thức đối xứng từ nghiệm:** `x1^2 + x2^2 = S^2 - 2P = (b^2 - 2ac) / a^2`",
                ]
            )
        elif kind == "crypto_mod":
            if item.get("variant") == "affine":
                lines.extend(
                    [
                        "- **Hàm mã hóa gốc:** `e(x) = (a * x + b) mod 26` với `gcd(a, 26) = 1`",
                        "- **Biến đổi rút bản rõ x (hàm giải mã):** `d(y) = a^(-1) * (y - b) mod 26`",
                        "- **Điều kiện nghịch đảo modulo `a^(-1)`:** `a * a^(-1) ≡ 1 (mod 26)` (Euclid mở rộng)",
                    ]
                )
            else:
                lines.extend(
                    [
                        "- **Hàm mã hóa gốc:** `e_k(x) = (x + k) mod 26`",
                        "- **Biến đổi rút bản rõ x:** `d_k(y) = (y - k) mod 26 = (y + (26 - k)) mod 26`",
                    ]
                )
        elif kind == "calculus_func":
            var = item["var"]
            expr = item["expr"]
            fname = item["func_name"]
            d1 = sp.simplify(sp.diff(expr, var))
            d2 = sp.simplify(sp.diff(expr, var, 2))
            expanded = sp.expand(expr)
            factored = sp.factor(expr)
            lines.append(f"- **Hàm số gốc trích xuất:** `{fname} = {_fmt_sym(expr)}`")
            if expanded != expr:
                lines.append(f"  * **Khai triển đại số (SymPy expand):** `{fname} = {_fmt_sym(expanded)}`")
            if factored != expr and factored != expanded:
                lines.append(f"  * **Phân tích nhân tử (SymPy factor):** `{fname} = {_fmt_sym(factored)}`")
            lines.append(f"  * **Đạo hàm bậc 1 (SymPy diff):** `d/d{var} [{fname}] = {_fmt_sym(d1)}`")
            try:
                crit = [r for r in sp.solve(sp.Eq(d1, 0), var) if r.is_real]
                if crit:
                    crit_str = ", ".join(_fmt_sym(c) for c in crit[:4])
                    lines.append(f"  * **Điểm dừng (nghiệm đạo hàm = 0):** `{var} ∈ {{{crit_str}}}`")
            except Exception:
                pass
            lines.append(f"  * **Đạo hàm bậc 2:** `d^2/d{var}^2 [{fname}] = {_fmt_sym(d2)}`")
            try:
                integ = sp.integrate(expr, var)
                if not isinstance(integ, sp.Integral):
                    lines.append(f"  * **Nguyên hàm bất định (SymPy integrate):** `∫ ({_fmt_sym(expr)}) d{var} = {_fmt_sym(integ)} + C`")
            except Exception:
                pass
        elif kind == "linear_system":
            x, y = sp.symbols("x y", real=True)
            eq1, eq2 = item["eq1"], item["eq2"]
            sol = item["solution"]
            lines.append(f"- **Hệ phương trình tuyến tính gốc:** `{item['raw1']}` và `{item['raw2']}`")
            try:
                y_sub = sp.solve(eq1, y)
                if y_sub:
                    y_expr = sp.simplify(y_sub[0])
                    sub_eq = sp.simplify(item["diff2"].subs(y, y_expr))
                    lines.append(f"  * **Biến đổi thế từ PT (1):** `y = {_fmt_sym(y_expr)}`")
                    lines.append(f"  * **Thế vào PT (2) thu phương trình 1 ẩn:** `{_fmt_sym(sub_eq)} = 0`")
            except Exception:
                pass
            try:
                p1, p2 = sp.Poly(item["diff1"], x, y), sp.Poly(item["diff2"], x, y)
                a1, b1 = p1.coeff_monomial(x), p1.coeff_monomial(y)
                a2, b2 = p2.coeff_monomial(x), p2.coeff_monomial(y)
                det = sp.simplify(a1 * b2 - a2 * b1)
                lines.append(f"  * **Định thức Cramer:** `D = ({a1})*({b2}) - ({a2})*({b1}) = {det} ≠ 0`")
            except Exception:
                pass
            lines.append(f"  * **Nghiệm chính xác (SymPy solve):** `x = {_fmt_sym(sol[x])}`, `y = {_fmt_sym(sol[y])}`")
        elif kind == "algebraic_eq":
            lhs = item["lhs"]
            rhs = item["rhs"]
            eq = sp.Eq(lhs, rhs)
            origin_note = (
                f" *(suy luận từ ví dụ trong tài liệu — {item['domain_label']})*"
                if item.get("inferred_from_example")
                else ""
            )
            lines.append(f"- **Từ công thức gốc:** `{_fmt_sym(lhs)} = {_fmt_sym(rhs)}`{origin_note}")
            for sym in item["symbols"]:
                if sym == lhs:
                    continue
                try:
                    sols = sp.solve(eq, sym)
                except Exception:
                    sols = []
                if sols:
                    # Prefer positive/principal branch when square root yields [-sqrt(...), sqrt(...)]
                    chosen = sols[-1] if (len(sols) == 2 and str(sols[0]).startswith("-")) else sols[0]
                    lines.append(f"  * **Rút biến `{sym}`:** `{sym} = {_fmt_sym(chosen)}`")
    return lines


def generate_worked_examples(
    formulas: Sequence[Dict[str, Any]],
    doc_text: str = "",
    count: int = 2,
) -> List[str]:
    """Generates fresh, mathematically verified worked examples distinct from doc examples."""
    out: List[str] = []
    for item in formulas:
        if len(out) >= count:
            break
        kind = item.get("kind")
        if kind == "chemistry_redox":
            # Choose fresh Al/HNO3 reaction with exact arithmetic via Fraction
            mv = Fraction(str(item.get("molar_vol", 24.79)))
            m_al = Fraction("5.4")
            n_al = m_al / 27
            n_e = n_al * 3
            n_n2o = n_e / 8
            v_n2o = n_n2o * mv
            m_salt = m_al + 62 * n_e
            mv_str = str(float(mv)).replace(".", ",")
            n_al_f = float(n_al)
            n_e_f = float(n_e)
            n_n2o_f = float(n_n2o)
            v_n2o_f = round(float(v_n2o), 4)
            m_salt_f = float(m_salt)
            out.append(
                "**Ví dụ mở rộng (Kim loại Al tác dụng HNO3 tạo khí N2O):**\n"
                f"- **Đề bài mới:** Hòa tan hoàn toàn **5,4 gam Al** vào dung dịch HNO3 loãng dư, thu được V lít khí N2O duy nhất (ĐKC, 1 mol khí = {mv_str} lít) và m gam muối Al(NO3)3. Tính V và m.\n"
                f"- **Bước 1 (Số mol e nhường):** n(Al) = 5,4 / 27 = {n_al_f:g} mol. Quá trình Al -> Al3+ + 3e cho n(e nhường) = 3 * {n_al_f:g} = {n_e_f:g} mol.\n"
                f"- **Bước 2 (Bảo toàn e cho khí N2O):** Khử 2N+5 + 8e -> N2O nhận 8e, nên n(N2O) = {n_e_f:g} / 8 = {n_n2o_f:g} mol.\n"
                f"- **Bước 3 (Thể tích khí & muối tính bằng công thức biến đổi):** V = {n_n2o_f:g} * {mv_str} = {v_n2o_f} lít; m_muối = 5,4 + 62 * {n_e_f:g} = {m_salt_f:g} gam."
            )
        elif kind == "quadratic":
            a, b, c = (2, -5, 2) if "x^2 - 5x + 6" in doc_text else (1, -5, 6)
            sol = solve_quadratic(a, b, c)
            roots_txt = ", ".join(str(r) for r in sol.get("roots", []))
            s_val = sol["vieta_sum"]
            p_val = sol["vieta_product"]
            disc = sol["discriminant"]
            symm_val = Fraction(str(s_val)) ** 2 - 2 * Fraction(str(p_val))
            out.append(
                f"**Ví dụ mở rộng (Giải & kiểm chứng Vi-ét phương trình mới):**\n"
                f"- **Đề bài mới:** Giải phương trình `{a}x^2 {b:+}x {c:+} = 0` và tính giá trị S = x1 + x2, P = x1*x2, x1^2 + x2^2.\n"
                f"- **Bước 1 (Biệt thức):** Delta = ({b})^2 - 4*{a}*{c} = {disc} > 0 (có 2 nghiệm phân biệt).\n"
                f"- **Bước 2 (Nghiệm & Vi-ét kiểm chứng):** x in {{{roots_txt}}}; S = -({b})/{a} = {s_val}, P = {c}/{a} = {p_val}.\n"
                f"- **Bước 3 (Biểu thức đối xứng suy ra):** x1^2 + x2^2 = S^2 - 2P = ({s_val})^2 - 2*({p_val}) = {symm_val}."
            )
        elif kind == "crypto_mod":
            if item.get("variant") == "affine":
                y_val = (5 * 4 + 8) % 26
                d_val = (21 * (y_val - 8)) % 26
                out.append(
                    "**Ví dụ mở rộng (Mã hóa và giải mã nghịch đảo Affine mới):**\n"
                    f"- **Đề bài mới:** Với khóa k = (5, 8) trên Z26 (biết gcd(5,26)=1 và 5^(-1) ≡ 21 (mod 26)), hãy mã hóa x = 4 ('E') rồi kiểm chứng giải mã ngược.\n"
                    f"- **Mã hóa:** y = (5 * 4 + 8) mod 26 = 28 mod 26 = {y_val} ('C').\n"
                    f"- **Giải mã (từ công thức biến đổi):** x = 21 * ({y_val} - 8) mod 26 = -126 mod 26 = {d_val} ('E', khớp ban đầu)."
                )
            else:
                y_val = (7 + 5) % 26
                d_val = (y_val - 5) % 26
                out.append(
                    "**Ví dụ mở rộng (Mã dịch vòng với khóa mới k = 5):**\n"
                    f"- Mã hóa ký tự x = 7 ('H'): y = (7 + 5) mod 26 = {y_val} ('M').\n"
                    f"- Giải mã ngược: x = ({y_val} - 5) mod 26 = {d_val} ('H')."
                )
        elif kind == "calculus_func":
            var = item["var"]
            base_expr = item["expr"]
            # Build a fresh distinct function g(var) = base_expr + 2*var - 1
            new_expr = sp.simplify(base_expr + 2 * var - 1)
            d1 = sp.simplify(sp.diff(new_expr, var))
            val_at_2 = sp.simplify(new_expr.subs(var, 2))
            slope_at_2 = sp.simplify(d1.subs(var, 2))
            integ_01 = None
            try:
                it_val = sp.integrate(new_expr, (var, 0, 1))
                if not isinstance(it_val, sp.Integral):
                    integ_01 = sp.simplify(it_val)
            except Exception:
                integ_01 = None
            step_int = (
                f"\n- **Bước 3 (Tích phân xác định trên [0, 1]):** `∫_0^1 g({var}) d{var} = {_fmt_sym(integ_01)}`."
                if integ_01 is not None
                else ""
            )
            out.append(
                f"**Ví dụ mở rộng (Khảo sát đạo hàm & tích phân hàm biến đổi mới):**\n"
                f"- **Đề bài mới:** Xét hàm số mới `g({var}) = {_fmt_sym(new_expr)}`. Tính `g(2)`, `g'({var})`, hệ số góc tiếp tuyến `g'(2)` và tích phân trên `[0, 1]`.\n"
                f"- **Bước 1 (Giá trị tại {var} = 2):** `g(2) = {_fmt_sym(val_at_2)}`.\n"
                f"- **Bước 2 (Đạo hàm & hệ số góc):** `g'({var}) = {_fmt_sym(d1)}` => `g'(2) = {_fmt_sym(slope_at_2)}`.{step_int}"
            )
        elif kind == "linear_system":
            x, y = sp.symbols("x y", real=True)
            # Fresh clean integer system: 3x + 2y = 16 and x - y = 2 -> (x=4, y=2)
            eq1_n = sp.Eq(3 * x + 2 * y, 16)
            eq2_n = sp.Eq(x - y, 2)
            sol_n = sp.solve([eq1_n, eq2_n], (x, y))
            out.append(
                "**Ví dụ mở rộng (Giải hệ phương trình tuyến tính 2 ẩn mới bằng phương pháp thế):**\n"
                "- **Đề bài mới:** Giải hệ phương trình `3x + 2y = 16` và `x - y = 2`.\n"
                "- **Bước 1 (Rút ẩn từ PT 2):** `x = y + 2`.\n"
                "- **Bước 2 (Thế vào PT 1):** `3(y + 2) + 2y = 16` => `5y = 10` => `y = 2`.\n"
                f"- **Bước 3 (Tìm ẩn còn lại & kiểm chứng):** `x = {sol_n[x]}`, `y = {sol_n[y]}` (thử lại: `3*{sol_n[x]} + 2*{sol_n[y]} = 16`, khớp hoàn toàn)."
            )
        elif kind == "algebraic_eq":
            lhs = item["lhs"]
            rhs = item["rhs"]
            syms = item["symbols"]
            rhs_syms = [s for s in syms if s != lhs]
            if rhs_syms:
                sub_vals = {s: sp.Integer(idx + 2) for idx, s in enumerate(rhs_syms)}
                lhs_val = sp.simplify(rhs.subs(sub_vals))
                subs_desc = ", ".join(f"`{k} = {v}`" for k, v in sub_vals.items())
                target_var = rhs_syms[0]
                inv_exprs = sp.solve(sp.Eq(lhs, rhs), target_var)
                inv_txt = ""
                if inv_exprs:
                    chosen_inv = inv_exprs[-1] if (len(inv_exprs) == 2 and str(inv_exprs[0]).startswith("-")) else inv_exprs[0]
                    inv_check = sp.simplify(chosen_inv.subs({**sub_vals, lhs: lhs_val}))
                    inv_txt = f" Ngược lại, dùng công thức biến đổi `{target_var} = {_fmt_sym(chosen_inv)}` ta thu lại `{target_var} = {_fmt_sym(inv_check)}`."
                out.append(
                    f"**Ví dụ mở rộng (Áp dụng thuận & nghịch công thức `{_fmt_sym(lhs)} = {_fmt_sym(rhs)}`):**\n"
                    f"- Cho {subs_desc}, thay vào công thức thu được `{lhs} = {_fmt_sym(lhs_val)}`.{inv_txt}"
                )
    return out[:count]


def generate_practice_exercises(
    formulas: Sequence[Dict[str, Any]],
    count: int = 3,
) -> List[str]:
    """Creates 3 tiered self-study exercises with verified SymPy / Fraction solutions."""
    exercises: List[str] = []
    for item in formulas:
        kind = item.get("kind")
        if kind == "chemistry_redox":
            mv = Fraction(str(item.get("molar_vol", 24.79)))
            v1 = round(float(Fraction("0.4") / 3 * mv), 3)
            m_salt1 = float(Fraction("4.8") + 62 * Fraction("0.4"))
            n_no2 = Fraction("0.15")
            v2_in = round(float(n_no2 * mv), 4)
            m_cu = round(float((n_no2 * 3 / 2) * 64), 2)
            v3 = round(float(Fraction("0.5") * mv), 3)
            v2_str = str(v2_in).replace(".", ",")
            mv_str = str(float(mv)).replace(".", ",")
            exercises.extend(
                [
                    f"- **Bài 1 (Áp dụng trực tiếp):** Hòa tan hoàn toàn 4,8 gam Mg trong dung dịch HNO3 loãng dư, thu được khí NO duy nhất (ĐKC). Tính thể tích khí NO và khối lượng muối Mg(NO3)2.\n"
                    f"  *Đáp án:* n(Mg) = 0,2 mol => n_e = 0,4 mol => n(NO) = 0,4/3 ≈ 0,133 mol, V ≈ {v1} lít; m_muối = {m_salt1:g} gam.",
                    f"- **Bài 2 (Biến đổi ngược công thức tìm kim loại):** Hòa tan m gam Cu trong HNO3 loãng dư thu được {v2_str} lít khí NO (đo ở 1 mol = {mv_str} lít). Tìm giá trị của m.\n"
                    f"  *Đáp án:* n(NO) = 0,15 mol => n_e = 0,45 mol => n(Cu) = 0,45/2 = 0,225 mol => m = {m_cu:g} gam.",
                    f"- **Bài 3 (Vận dụng hỗn hợp 2 kim loại):** Cho hỗn hợp gồm 6,4 gam Cu và 3,6 gam Mg tác dụng vừa đủ với HNO3 đặc thu được khí NO2 duy nhất (nhận 1e). Tính thể tích khí NO2 ở ĐKC.\n"
                    f"  *Đáp án:* ∑ n(e nhường) = 2*0,1 + 2*0,15 = 0,5 mol => n(NO2) = 0,5 mol => V = {v3} lít.",
                ]
            )
            break
        if kind == "quadratic":
            s1 = solve_quadratic(1, -7, 10)
            s2 = solve_quadratic(1, -6, 9)
            disc1 = s1["discriminant"]
            r1_0, r1_1 = s1["roots"][0], s1["roots"][1]
            disc2 = s2["discriminant"]
            r2_0 = s2["roots"][0]
            exercises.extend(
                [
                    f"- **Bài 1 (Cơ bản):** Giải phương trình `x^2 - 7x + 10 = 0`.\n  *Đáp án:* Delta = {disc1}, nghiệm `x1 = {r1_0}`, `x2 = {r1_1}`.",
                    "- **Bài 2 (Biến đổi Vi-ét):** Không giải phương trình `x^2 - 4x + 1 = 0`, hãy tính `A = x1^2 + x2^2` và `B = 1/x1 + 1/x2`.\n  *Đáp án:* `S = 4`, `P = 1` => `A = S^2 - 2P = 14`, `B = S/P = 4`.",
                    f"- **Bài 3 (Nghiệm kép & kiểm tra biệt thức):** Kiểm tra điều kiện nghiệm của `x^2 - 6x + 9 = 0`.\n  *Đáp án:* Delta = {disc2} = 0 => phương trình có nghiệm kép `x = {r2_0}`.",
                ]
            )
            break
        if kind == "crypto_mod":
            exercises.extend(
                [
                    "- **Bài 1 (Áp dụng thuận):** Dùng hệ mã dịch vòng `k = 4`, hãy mã hóa chữ 'C' (`x = 2`).\n  *Đáp án:* `y = (2 + 4) mod 26 = 6` ('G').",
                    "- **Bài 2 (Biến đổi giải mã):** Dùng hàm giải mã `d(y) = 15 * (y - 3) mod 26` của hệ Affine (`a=7, a^(-1)=15, b=3`) để giải mã `y = 17`.\n  *Đáp án:* `x = 15 * (17 - 3) mod 26 = 210 mod 26 = 2` ('C').",
                    "- **Bài 3 (Điều kiện khóa):** Trong các hệ số `a ∈ {4, 9, 13, 15}`, giá trị nào dùng được cho mã hóa Affine trên Z26?\n  *Đáp án:* Chỉ `a = 9` và `a = 15` vì `gcd(a, 26) = 1`.",
                ]
            )
            break
        if kind == "calculus_func":
            var = item["var"]
            p1 = var ** 2 - 6 * var + 8
            d1 = sp.diff(p1, var)
            p2 = var ** 3 - 3 * var ** 2 + 2
            d2 = sp.diff(p2, var)
            crit2 = sp.solve(sp.Eq(d2, 0), var)
            p3 = 3 * var ** 2 + 2 * var + 1
            int3 = sp.integrate(p3, (var, 0, 2))
            exercises.extend(
                [
                    f"- **Bài 1 (Đạo hàm & phân tích nhân tử):** Cho `h({var}) = {_fmt_sym(p1)}`. Phân tích nhân tử và tính `h'({var})`, `h'(5)`.\n  *Đáp án:* `h({var}) = {_fmt_sym(sp.factor(p1))}`, `h'({var}) = {_fmt_sym(d1)}`, `h'(5) = {d1.subs(var, 5)}`.",
                    f"- **Bài 2 (Tìm điểm cực trị từ đạo hàm):** Tìm các điểm dừng (`k'({var}) = 0`) của `k({var}) = {_fmt_sym(p2)}`.\n  *Đáp án:* `k'({var}) = {_fmt_sym(d2)} = 0` => `{var} ∈ {{{', '.join(str(r) for r in crit2)}}}`.",
                    f"- **Bài 3 (Nguyên hàm & tích phân xác định):** Tính tích phân `I = ∫_0^2 ({_fmt_sym(p3)}) d{var}`.\n  *Đáp án:* Nguyên hàm `{_fmt_sym(sp.integrate(p3, var))} + C` => `I = {int3}`.",
                ]
            )
            break
        if kind == "linear_system":
            x, y = sp.symbols("x y", real=True)
            s1 = sp.solve([sp.Eq(x + y, 7), sp.Eq(x - y, 3)], (x, y))
            s2 = sp.solve([sp.Eq(2 * x + 3 * y, 13), sp.Eq(x - y, -1)], (x, y))
            s3 = sp.solve([sp.Eq(4 * x - y, 11), sp.Eq(2 * x + 5 * y, 11)], (x, y))
            exercises.extend(
                [
                    f"- **Bài 1 (Cộng đại số cơ bản):** Giải hệ `x + y = 7` và `x - y = 3`.\n  *Đáp án:* `x = {s1[x]}`, `y = {s1[y]}`.",
                    f"- **Bài 2 (Phương pháp thế):** Giải hệ `2x + 3y = 13` và `x - y = -1`.\n  *Đáp án:* `x = {s2[x]}`, `y = {s2[y]}`.",
                    f"- **Bài 3 (Quy tắc Cramer / khử ẩn):** Giải hệ `4x - y = 11` và `2x + 5y = 11`.\n  *Đáp án:* `x = {s3[x]}`, `y = {s3[y]}`.",
                ]
            )
            break
        if kind == "algebraic_eq":
            lhs = item["lhs"]
            rhs = item["rhs"]
            syms = [s for s in item["symbols"] if s != lhs]
            if len(syms) >= 2:
                vals_a = {s: sp.Integer(2 * (idx + 2)) for idx, s in enumerate(syms)}
                vals_c = {s: sp.Integer(3 * (idx + 1)) for idx, s in enumerate(syms)}
                ans1 = sp.simplify(rhs.subs(vals_a))
                ans3 = sp.simplify(rhs.subs(vals_c))
                v0 = syms[0]
                inv0 = sp.solve(sp.Eq(lhs, rhs), v0)
                chosen_inv0 = inv0[-1] if (len(inv0) == 2 and str(inv0[0]).startswith("-")) else (inv0[0] if inv0 else None)
                vals_b_other = {s: sp.Integer(idx + 2) for idx, s in enumerate(syms[1:])}
                # Pick lhs_target cleanly from substituting v0 = 4
                lhs_target = sp.simplify(rhs.subs({**vals_b_other, v0: sp.Integer(4)}))
                ans2 = sp.simplify(chosen_inv0.subs({**vals_b_other, lhs: lhs_target})) if chosen_inv0 is not None else "?"
                desc_a = ", ".join(f"`{k} = {v}`" for k, v in vals_a.items())
                desc_b = ", ".join(f"`{k} = {v}`" for k, v in vals_b_other.items())
                desc_c = ", ".join(f"`{k} = {v}`" for k, v in vals_c.items())
                exercises.extend(
                    [
                        f"- **Bài 1 (Áp dụng thuận):** Từ `{_fmt_sym(lhs)} = {_fmt_sym(rhs)}`, tính `{lhs}` khi {desc_a}.\n  *Đáp án:* `{lhs} = {_fmt_sym(ans1)}`.",
                        f"- **Bài 2 (Biến đổi ngược):** Rút ẩn `{v0}` khi biết `{lhs} = {_fmt_sym(lhs_target)}`, {desc_b}.\n  *Đáp án:* `{v0} = {_fmt_sym(ans2)}`.",
                        f"- **Bài 3 (Mở rộng bộ số mới):** Tính `{lhs}` khi {desc_c}.\n  *Đáp án:* `{lhs} = {_fmt_sym(ans3)}`.",
                    ]
                )
                break
    return exercises[:count]


def build_online_study_expansion(
    query: str,
    doc_text: str,
    doc_title: str = "Tài liệu",
) -> Optional[Dict[str, Any]]:
    """
    Main entry point for Online mode formula transformation, example synthesis,
    and practice exercise creation grounded on formulas extracted from `doc_text`.
    """
    intent = detect_expansion_intent(query)
    if not intent["wants_any"]:
        return None

    formulas = extract_document_formulas(doc_text)
    if not formulas:
        return None

    # Prioritize formula families explicitly referenced by the user's query
    q_low = _strip_accents((query or "").lower())

    def _formula_query_priority(item: Dict[str, Any]) -> int:
        kind = item.get("kind", "")
        raw_l = _strip_accents(str(item.get("raw", "")).lower())
        if kind == "calculus_func" and any(
            k in q_low for k in ("dao ham", "tich phan", "nguyen ham", "khai trien", "nhan tu", "ham so", "cuc tri", "f(x)", "g(x)")
        ):
            return 5
        if kind == "linear_system" and any(k in q_low for k in ("he phuong trinh", "giai he", "2 an", "hai an", "cramer")):
            return 5
        if kind == "quadratic" and any(k in q_low for k in ("x^2", "bac hai", "delta", "vi-et", "phuong trinh")):
            return 3
        if kind == "chemistry_redox" and any(
            k in q_low for k in ("oxi hoa", "chat khu", "electron", "hno3", "hcl", "mol", "hoa hoc")
        ):
            return 3
        if kind == "crypto_mod" and any(k in q_low for k in ("mod", "affine", "caesar", "ma hoa", "giai ma")):
            return 3
        if kind == "algebraic_eq":
            lhs_name = str(item.get("lhs", "")).lower()
            sym_names = [s.name.lower() for s in item.get("symbols", [])]
            if raw_l in q_low or (lhs_name and re.search(rf"\b{re.escape(lhs_name)}\s*=", q_low)):
                return 4
            if sym_names and sum(1 for sn in sym_names if re.search(rf"\b{re.escape(sn)}\b", q_low)) >= 2:
                return 3
        return 1

    formulas = sorted(formulas, key=_formula_query_priority, reverse=True)

    include_all = not (intent["transform_formula"] or intent["new_example"] or intent["practice_exercise"])
    show_transform = intent["transform_formula"] or include_all or intent["new_example"]
    show_examples = intent["new_example"] or include_all
    show_exercises = intent["practice_exercise"] or include_all

    sections: List[str] = [
        "🌐 **Chế độ Online — Mở rộng Công thức, Ví dụ & Bài tập (Động cơ Symbolic tự build)** [1]",
        f"*Dựa trên công thức gốc trích từ **{doc_title}**, hệ thống thực hiện biến đổi biểu thức và sinh dữ liệu luyện tập mới (đã kiểm chứng bằng SymPy):*",
    ]
    modes_generated: List[str] = []

    if show_transform:
        t_lines = derive_formula_transformations(formulas[:2])
        if t_lines:
            modes_generated.append("transform_formula")
            sections.append("**1. Biến đổi công thức & rút ẩn liên quan:**\n" + "\n".join(t_lines))

    if show_examples:
        ex_blocks = generate_worked_examples(formulas[:2], doc_text=doc_text, count=2)
        if ex_blocks:
            modes_generated.append("new_example")
            sections.append("**2. Ví dụ minh họa mới (độc lập với ví dụ gốc):**\n" + "\n\n".join(ex_blocks))

    if show_exercises:
        ex_list = generate_practice_exercises(formulas[:2], count=3)
        if ex_list:
            modes_generated.append("practice_exercise")
            sections.append("**3. Bài tập luyện tập kèm đáp án kiểm chứng:**\n" + "\n".join(ex_list))

    if not modes_generated:
        return None

    return {
        "answer": "\n\n".join(sections),
        "formulas_found": len(formulas),
        "modes_generated": modes_generated,
        "engine": "SymbolicFormulaLab-SymPy-SelfBuilt",
    }


__all__ = [
    "detect_expansion_intent",
    "extract_document_formulas",
    "derive_formula_transformations",
    "generate_worked_examples",
    "generate_practice_exercises",
    "build_online_study_expansion",
]
