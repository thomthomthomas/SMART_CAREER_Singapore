import glob
import json
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
from flask import Blueprint, jsonify, send_file, current_app, abort

roles_bp = Blueprint("roles", __name__)

# ---------- config helpers ----------

def _load_config_anywhere(config_file: str = "config.json") -> Dict[str, Any]:
    matches = glob.glob(f"**/{config_file}", recursive=True)
    if not matches:
        raise FileNotFoundError("config.json not found anywhere")
    p = Path(matches[0])
    return json.loads(p.read_text(encoding="utf-8"))

def app_config() -> Dict[str, Any]:
    cfg = current_app.config.get("APP_CONFIG")
    return cfg if isinstance(cfg, dict) else _load_config_anywhere()

# ---------- utils ----------

_slug_re = re.compile(r"[^a-z0-9]+")

def slugify(name: str) -> str:
    s = (name or "").strip().lower()
    return _slug_re.sub("-", s).strip("-") or "role"

def _collect_skills(raw: Dict[str, Any]) -> List[str]:
    candidates = []
    for k in ["skills", "key_skills", "top_skills", "required_skills", "competencies", "tags"]:
        v = raw.get(k)
        if isinstance(v, list):
            candidates.extend([str(x).strip() for x in v if str(x).strip()])
        elif isinstance(v, str):
            candidates.extend([t.strip() for t in v.split(",") if t.strip()])
    seen, out = set(), []
    for x in candidates:
        low = x.lower()
        if low not in seen:
            seen.add(low)
            out.append(x)
    return out[:15]

def _role_name_from_json(raw: Dict[str, Any], fallback: str) -> str:
    for k in ["role", "title", "job_title", "name"]:
        if raw.get(k):
            return str(raw[k])
    return fallback

def _desc_from_json(raw: Dict[str, Any]) -> str:
    for k in ["description", "summary", "overview"]:
        v = raw.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""

def _facts_from_json(raw: Dict[str, Any]) -> List[str]:
    v = raw.get("facts")
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()][:4]
    return []

def _gemini_keys(cfg: Dict[str, Any]) -> List[str]:
    api = cfg.get("api_keys", {})
    keys = []
    if isinstance(api.get("gemini_api_keys"), list):
        keys.extend([k for k in api["gemini_api_keys"] if k])
    if api.get("gemini_api_key"):
        keys.append(api["gemini_api_key"])
    return keys

def _gemini_generate_content(key: str, model: str, text: str) -> Optional[str]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = {"contents": [{"parts": [{"text": text}]}]}
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return None

def _with_gemini_summary_facts_skills(cfg: Dict[str, Any], raw: Dict[str, Any]) -> Dict[str, Any]:
    # Defaults from your JSON
    summary = _desc_from_json(raw)
    facts = _facts_from_json(raw)
    skills = _collect_skills(raw)

    keys = _gemini_keys(cfg)
    if not keys:
        return {"summary": summary[:800], "facts": facts[:4], "skills": skills[:15]}

    prompt = (
        "You are a career content editor. Given role JSON, return a **pure JSON** object with keys:\n"
        "summary (100-120 words, Singapore context where relevant),\n"
        "facts (3-4 crisp bullet strings),\n"
        "skills (max 15 concise tags). No markdown. Only JSON.\n\n"
        f"ROLE JSON:\n{json.dumps(raw, ensure_ascii=False)}"
    )
    text = _gemini_generate_content(keys[0], "gemini-1.5-flash", prompt)
    if not text:
        return {"summary": summary[:800], "facts": facts[:4], "skills": skills[:15]}

    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return {"summary": summary[:800], "facts": facts[:4], "skills": skills[:15]}
    try:
        parsed = json.loads(m.group(0))
        return {
            "summary": str(parsed.get("summary") or summary)[:800],
            "facts": list(parsed.get("facts") or facts)[:4],
            "skills": list(parsed.get("skills") or skills)[:15],
        }
    except Exception:
        return {"summary": summary[:800], "facts": facts[:4], "skills": skills[:15]}

def _image_query_for_role(cfg: Dict[str, Any], role_name: str) -> str:
    keys = _gemini_keys(cfg)
    if not keys:
        return role_name
    prompt = (
        "Return 3-6 comma-separated photo keywords (no quotes, no extra text) "
        "for a professional, non-cheesy image depicting the job role: "
        f"{role_name}"
    )
    text = _gemini_generate_content(keys[0], "gemini-1.5-flash", prompt) or ""
    parts = [t.strip() for t in text.split(",") if t.strip()]
    return ", ".join(parts) or role_name

# ---------- filesystem discovery ----------

def _discover(cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    jobs = Path(cfg.get("directories", {}).get("jobs_analysis", "./jobs_analysis")).resolve()
    pdfs = Path(cfg.get("directories", {}).get("pdf_output", "./pdf_reports")).resolve()
    roles = []
    for jf in sorted(jobs.glob("*.json")):
        raw = json.loads(jf.read_text(encoding="utf-8"))
        name = _role_name_from_json(raw, jf.stem)
        slug = slugify(name)
        pdf_path = (pdfs / f"{slug}.pdf")
        roles.append({
            "slug": slug,
            "role": name,
            "json_path": str(jf),
            "pdf_path": str(pdf_path) if pdf_path.exists() else None
        })
    return roles

def _find_role_doc(cfg: Dict[str, Any], slug: str) -> Optional[Dict[str, Any]]:
    for r in _discover(cfg):
        if r["slug"] == slug:
            return r
    return None

# ---------- routes ----------

@roles_bp.get("/roles")
def list_roles():
    cfg = app_config()
    items = _discover(cfg)
    return jsonify({"roles": [{"slug": i["slug"], "role": i["role"], "has_pdf": bool(i["pdf_path"])} for i in items]})

@roles_bp.get("/roles/<slug>")
def get_role(slug: str):
    cfg = app_config()
    doc = _find_role_doc(cfg, slug)
    if not doc:
        abort(404, description="Role not found")

    raw = json.loads(Path(doc["json_path"]).read_text(encoding="utf-8"))
    role_name = doc["role"]

    content = _with_gemini_summary_facts_skills(cfg, raw)

    sig = int(hashlib.sha256(role_name.encode()).hexdigest(), 16) % 10_000_000
    img_query = _image_query_for_role(cfg, role_name)
    image_url = f"https://source.unsplash.com/featured/800x450?{img_query}&sig={sig}"

    return jsonify({
        "role": role_name,
        "summary": content.get("summary", ""),
        "facts": content.get("facts", [])[:4],
        "skills": content.get("skills", [])[:15],
        "pdfUrl": f"/api/roles/{slug}/pdf" if doc.get("pdf_path") else None,
        "imageQuery": img_query,
        "imageUrl": image_url
    })

@roles_bp.get("/roles/<slug>/pdf")
def role_pdf(slug: str):
    cfg = app_config()
    doc = _find_role_doc(cfg, slug)
    if not doc or not doc.get("pdf_path"):
        abort(404, description="PDF not found")
    p = Path(doc["pdf_path"])
    return send_file(str(p), mimetype="application/pdf", as_attachment=True, download_name=f"{slug}.pdf")
