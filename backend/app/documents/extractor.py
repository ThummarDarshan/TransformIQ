import os
import re
import html
import socket
import ipaddress
import urllib.parse
import zipfile
from typing import List, Dict, Any, Tuple, Optional
import httpx
from app.config.settings import settings

BLOCKED_HOSTS = {
    "localhost", "127.0.0.1", "::1", "0.0.0.0", "169.254.169.254",
    "metadata.google.internal", "instance-data", "metadata"
}

def is_safe_url(url: str) -> Tuple[bool, str]:
    """
    Bulletproof SSRF validation:
    - Validates scheme is strictly HTTP or HTTPS.
    - Resolves host DNS to verify IP is not in private/reserved/loopback/link-local ranges.
    - Blocks localhost, link-local, private LANs, cloud metadata endpoints.
    - Validates both IPv4 and IPv6 addresses.
    """
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme.lower() not in ["http", "https"]:
            return False, "Invalid URL protocol. Only HTTP and HTTPS are permitted."

        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid or missing hostname in URL."

        hostname_lower = hostname.lower()
        if hostname_lower in BLOCKED_HOSTS or any(b in hostname_lower for b in ["169.254.169.254", "metadata.google.internal"]):
            return False, "Access to localhost or cloud metadata services is strictly forbidden."

        # Check if hostname itself is a raw IP
        try:
            ip_obj = ipaddress.ip_address(hostname)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved or ip_obj.is_unspecified:
                return False, f"Access to private/internal network address ({hostname}) is restricted."
        except ValueError:
            pass  # Hostname is a domain name, proceed to DNS resolution

        # Resolve DNS IP addresses
        addr_info = socket.getaddrinfo(hostname, None)
        for family, socktype, proto, canonname, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)

            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved or ip_obj.is_unspecified:
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
    Includes redirect re-validation to prevent redirect-based SSRF and response size limiting.
    """
    current_url = url
    max_redirects = 3
    redirect_count = 0

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 TransformIQ-SecurityAuditor/2.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        timeout = httpx.Timeout(10.0, connect=5.0)

        with httpx.Client(timeout=timeout, follow_redirects=False) as client:
            while redirect_count <= max_redirects:
                is_safe, error_reason = is_safe_url(current_url)
                if not is_safe:
                    return f"URL Security Block: {error_reason}", [{"page_number": 1, "content": error_reason}]

                resp = client.get(current_url, headers=headers)
                
                # Check for redirects
                if resp.status_code in [301, 302, 303, 307, 308]:
                    redirect_target = resp.headers.get("Location")
                    if not redirect_target:
                        break
                    # Resolve relative redirect URLs
                    current_url = urllib.parse.urljoin(current_url, redirect_target)
                    redirect_count += 1
                    continue
                
                resp.raise_for_status()
                break

            if redirect_count > max_redirects:
                return "URL Security Block: Exceeded maximum allowed redirects.", [{"page_number": 1, "content": "Excessive redirects"}]

            content_type = resp.headers.get("content-type", "").lower()
            if "text/html" not in content_type and "application/xhtml" not in content_type and "text/plain" not in content_type:
                return f"Non-HTML content fetched from {url} (Content-Type: {content_type}).", [{"page_number": 1, "content": "Non-HTML resource"}]

            # Read text with maximum response buffer limit
            html_content = resp.text[:settings.MAX_URL_RESPONSE_SIZE_BYTES]

        # 1. Strip script, style, noscript, svg, header, footer, nav, iframe
        clean_html = re.sub(r'<(script|style|noscript|svg|iframe|header|footer|nav|form|embed|object)[^>]*>.*?</\1>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
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

def validate_file_signature(file_path: str, ext: str) -> Tuple[bool, str]:
    """
    Validates file magic bytes to prevent spoofed extensions.
    """
    try:
        with open(file_path, "rb") as f:
            header = f.read(16)
        
        if ext == "pdf":
            if not header.startswith(b"%PDF-"):
                return False, "Invalid PDF file signature."
        elif ext in ["docx", "pptx"]:
            # Zip container signature
            if not header.startswith(b"PK\x03\x04") and not header.startswith(b"PK\x05\x06"):
                return False, f"Invalid {ext.upper()} archive container signature."
            
            # Zip Bomb protection: check uncompressed size
            try:
                with zipfile.ZipFile(file_path, 'r') as z:
                    total_uncompressed = sum(info.file_size for info in z.infolist())
                    if total_uncompressed > 100 * 1024 * 1024:  # 100 MB max uncompressed
                        return False, "File exceeds safe uncompressed expansion limit."
            except Exception as e:
                return False, f"Invalid archive structure: {str(e)}"
        elif ext in ["txt", "md"]:
            # Check UTF-8 validity
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    f.read(1024)
            except UnicodeDecodeError:
                return False, "Text file is not valid UTF-8."
        
        return True, ""
    except Exception as e:
        return False, f"Signature validation error: {str(e)}"

def extract_text_from_file(file_path: str, filename: str) -> Tuple[str, List[Dict[str, Any]]]:
    ext = os.path.splitext(filename)[1].lower().replace('.', '')
    full_text = ""
    pages_or_slides: List[Dict[str, Any]] = []

    # Validate file signature
    is_valid, sig_err = validate_file_signature(file_path, ext)
    if not is_valid:
        err_msg = f"Document processing security block: {sig_err}"
        return err_msg, [{"page_number": 1, "content": err_msg}]

    try:
        if ext == "pdf":
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

        elif ext in ["docx", "doc"]:
            import docx
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = "\n\n".join(paragraphs)
            pages_or_slides.append({
                "page_number": 1,
                "content": full_text
            })

        elif ext in ["pptx", "ppt"]:
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
                full_text = f.read(500_000)  # Max 500k characters for plain text
            pages_or_slides.append({
                "page_number": 1,
                "content": full_text
            })
    except Exception as e:
        full_text = f"Error extracting document contents: {str(e)}"
        pages_or_slides.append({"page_number": 1, "content": full_text})

    return clean_text(full_text), pages_or_slides

def detect_section_heading(text: str) -> Optional[str]:
    """Detect section header from chunk text if present."""
    if not text:
        return None
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return None
    first_line = lines[0]
    # Check for markdown header or numbered section or all-caps header
    if first_line.startswith(('#', '§', '---')):
        return re.sub(r'^[#§\-\s]+', '', first_line).strip()
    if re.match(r'^(Section|\d+(\.\d+)*|[A-Z\s]{4,}:|[A-Z][a-zA-Z\s]{3,25}:)', first_line):
        return first_line.rstrip(':').strip()
    if len(first_line) < 60 and (first_line.isupper() or first_line.endswith(':')):
        return first_line.rstrip(':').strip()
    return None

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

def chunk_document_with_metadata(
    full_text: str,
    pages_or_slides: List[Dict[str, Any]] = None,
    chunk_size: int = None,
    overlap: int = None,
    source_prefix: str = "SRC"
) -> List[Dict[str, Any]]:
    """
    Provenance-preserving chunking:
    Produces structured chunk records with page number, detected section heading,
    paragraph offsets, exact sentence text, and stable source citation IDs.
    """
    c_size = chunk_size or settings.RAG_CHUNK_SIZE or 600
    c_overlap = overlap or settings.RAG_CHUNK_OVERLAP or 120
    structured_chunks = []
    chunk_counter = 1

    # If we have structured per-page/slide data, chunk within each page
    if pages_or_slides and len(pages_or_slides) > 0:
        global_offset = 0
        for page_data in pages_or_slides:
            page_num = page_data.get("page_number", 1)
            page_content = clean_text(page_data.get("content", ""))
            if not page_content:
                continue

            # Detect page section heading if any
            page_heading = detect_section_heading(page_content)
            
            p_start = 0
            while p_start < len(page_content):
                p_end = min(p_start + c_size, len(page_content))
                chunk_text_slice = page_content[p_start:p_end].strip()
                
                if chunk_text_slice:
                    chunk_heading = detect_section_heading(chunk_text_slice) or page_heading or f"Page {page_num} Section"
                    code = f"{source_prefix}-{chunk_counter:03d}"
                    
                    structured_chunks.append({
                        "source_code": code,
                        "chunk_index": chunk_counter - 1,
                        "page_number": page_num,
                        "section_heading": chunk_heading,
                        "paragraph_number": p_start // (c_size or 1) + 1,
                        "start_offset": global_offset + p_start,
                        "end_offset": global_offset + p_end,
                        "content": chunk_text_slice,
                        "exact_text": chunk_text_slice
                    })
                    chunk_counter += 1

                if p_end == len(page_content):
                    break
                p_start += c_size - c_overlap
            global_offset += len(page_content) + 1
    else:
        # Fallback to linear text chunking with offset tracking
        raw_chunks = chunk_text(full_text, c_size, c_overlap)
        offset = 0
        for idx, c in enumerate(raw_chunks):
            heading = detect_section_heading(c) or f"Section {idx + 1}"
            code = f"{source_prefix}-{chunk_counter:03d}"
            structured_chunks.append({
                "source_code": code,
                "chunk_index": idx,
                "page_number": (offset // 2500) + 1,
                "section_heading": heading,
                "paragraph_number": idx + 1,
                "start_offset": offset,
                "end_offset": offset + len(c),
                "content": c,
                "exact_text": c
            })
            chunk_counter += 1
            offset += len(c)

    return structured_chunks

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
    stop_words = {"the", "a", "an", "is", "in", "it", "of", "and", "or", "for", "with", "on", "at", "to", "from", "by", "what", "how", "why"}
    keywords = query_words - stop_words
    if not keywords:
        keywords = query_words

    scored_chunks = []
    for item in chunks:
        content = item.get("content", "")
        content_lower = content.lower()
        content_words = set(re.findall(r'\w+', content_lower))
        
        match_count = sum(1 for kw in keywords if kw in content_lower)
        word_overlap = len(keywords.intersection(content_words))
        
        score = (match_count * 2.5) + word_overlap
        scored_chunks.append((score, item))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [c[1] for c in scored_chunks[:top_k]]
