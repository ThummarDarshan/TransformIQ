import os
import re
import html
import socket
import ipaddress
import urllib.parse
from typing import List, Dict, Any, Tuple
import httpx
from app.config.settings import settings

def is_safe_url(url: str) -> Tuple[bool, str]:
    """
    Bulletproof SSRF validation:
    - Validates scheme is HTTP or HTTPS.
    - Resolves host DNS to verify IP is not in private/reserved ranges.
    - Blocks localhost, link-local, private LANs, cloud metadata endpoints.
    """
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme.lower() not in ["http", "https"]:
            return False, "Invalid URL protocol. Only HTTP and HTTPS are permitted."

        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid or missing hostname in URL."

        if hostname.lower() in ["localhost", "127.0.0.1", "::1", "0.0.0.0"]:
            return False, "Access to localhost or loopback is blocked for security."

        # Check cloud metadata endpoints
        if hostname == "169.254.169.254" or "metadata.google.internal" in hostname.lower():
            return False, "Access to cloud metadata services is strictly forbidden."

        # Resolve IP addresses
        addr_info = socket.getaddrinfo(hostname, None)
        for family, socktype, proto, canonname, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)

            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved:
                return False, f"Access to private/internal network address ({ip_str}) is restricted."

        return True, ""
    except Exception as e:
        return False, f"URL validation failed: {str(e)}"

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'[\r\t]', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()

def extract_text_from_url(url: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Safely fetches and extracts clean text content from a web URL or enterprise BRD web resource.
    """
    is_safe, error_reason = is_safe_url(url)
    if not is_safe:
        return f"URL Security Block: {error_reason}", [{"page_number": 1, "content": error_reason}]

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 TransformIQ-Crawler/2.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        timeout = httpx.Timeout(15.0, connect=8.0)
        with httpx.Client(timeout=timeout, follow_redirects=True, max_redirects=3) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            
            content_type = resp.headers.get("content-type", "").lower()
            if "text/html" not in content_type and "application/xhtml" not in content_type and "text/plain" not in content_type:
                return f"Non-HTML content fetched from {url} (Content-Type: {content_type}).", [{"page_number": 1, "content": "Non-HTML resource"}]
            
            html_content = resp.text[:1_000_000] # Limit to 1MB text buffer

        # 1. Strip script, style, noscript, svg, header, footer, nav
        clean_html = re.sub(r'<(script|style|noscript|svg|iframe|header|footer|nav|form)[^>]*>.*?</\1>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        # 2. Convert block elements to newlines
        clean_html = re.sub(r'<(p|br|div|h1|h2|h3|h4|h5|h6|li|tr|article|section)[^>]*>', '\n', clean_html, flags=re.IGNORECASE)
        # 3. Strip remaining tags
        text = re.sub(r'<[^>]+>', ' ', clean_html)
        # 4. Unescape HTML entities
        text = html.unescape(text)
        cleaned = clean_text(text)

        if not cleaned:
            cleaned = f"URL content fetched from {url}, but no readable textual body was detected."

        pages = [{"page_number": 1, "content": cleaned[:3000]}]
        return cleaned, pages
    except Exception as e:
        err_msg = f"Failed to fetch content from URL ({url}): {str(e)}"
        return err_msg, [{"page_number": 1, "content": err_msg}]

def extract_text_from_file(file_path: str, filename: str) -> Tuple[str, List[Dict[str, Any]]]:
    ext = os.path.splitext(filename)[1].lower()
    full_text = ""
    pages_or_slides: List[Dict[str, Any]] = []

    try:
        if ext == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                cleaned = clean_text(page_text)
                if cleaned:
                    pages_or_slides.append({
                        "page_number": idx + 1,
                        "content": cleaned
                    })
                    full_text += f"\n--- Page {idx + 1} ---\n" + cleaned

        elif ext in [".docx", ".doc"]:
            import docx
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = "\n\n".join(paragraphs)
            pages_or_slides.append({
                "page_number": 1,
                "content": full_text
            })

        elif ext in [".pptx", ".ppt"]:
            from pptx import Presentation
            prs = Presentation(file_path)
            for idx, slide in enumerate(prs.slides):
                slide_texts = []
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text:
                        slide_texts.append(shape.text)
                slide_content = clean_text("\n".join(slide_texts))
                if slide_content:
                    pages_or_slides.append({
                        "page_number": idx + 1,
                        "content": slide_content
                    })
                    full_text += f"\n--- Slide {idx + 1} ---\n" + slide_content

        else:  # txt, md, json, csv
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                full_text = f.read()
            pages_or_slides.append({
                "page_number": 1,
                "content": full_text
            })
    except Exception as e:
        full_text = f"Error extracting document contents: {str(e)}"
        pages_or_slides.append({"page_number": 1, "content": full_text})

    return clean_text(full_text), pages_or_slides

def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    c_size = chunk_size or settings.RAG_CHUNK_SIZE or 600
    c_overlap = overlap or settings.RAG_CHUNK_OVERLAP or 120
    cleaned = clean_text(text)
    if not cleaned:
        return []

    chunks = []
    start = 0
    while start < len(cleaned):
        end = min(start + c_size, len(cleaned))
        chunk = cleaned[start:end]
        chunks.append(chunk)
        if end == len(cleaned):
            break
        start += c_size - c_overlap
    return chunks

def search_relevant_chunks(chunks: List[Dict[str, Any]], query: str, top_k: int = 4) -> List[Dict[str, Any]]:
    """
    RAG Relevance Retrieval:
    Scores chunks based on query term frequency, overlap, and keyword matching.
    Returns the top_k most relevant chunks with source metadata.
    """
    if not chunks:
        return []
    if not query or not query.strip():
        return chunks[:top_k]

    query_words = set(re.findall(r'\w+', query.lower()))
    # Remove common stop words
    stop_words = {"the", "a", "an", "is", "in", "it", "of", "and", "or", "for", "with", "on", "at", "to", "from", "by", "what", "how", "why"}
    keywords = query_words - stop_words
    if not keywords:
        keywords = query_words

    scored_chunks = []
    for item in chunks:
        content = item.get("content", "")
        content_lower = content.lower()
        content_words = set(re.findall(r'\w+', content_lower))
        
        # Keyword match count
        match_count = sum(1 for kw in keywords if kw in content_lower)
        word_overlap = len(keywords.intersection(content_words))
        
        score = (match_count * 2.5) + word_overlap
        scored_chunks.append((score, item))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [c[1] for c in scored_chunks[:top_k]]
