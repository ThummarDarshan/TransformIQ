import React, { useState } from 'react';
import { Copy, Check, Terminal } from 'lucide-react';

interface FormattedMessageContentProps {
  content: string;
}

export const FormattedMessageContent: React.FC<FormattedMessageContentProps> = ({ content }) => {
  if (!content) return null;

  // Split into blocks by double linebreaks or code fences
  const renderInlineFormatted = (text: string): React.ReactNode => {
    // Process inline code `code`
    const codeParts = text.split(/(`[^`]+`)/g);
    return codeParts.map((codePart, cIdx) => {
      if (codePart.startsWith('`') && codePart.endsWith('`') && codePart.length > 1) {
        return (
          <code
            key={cIdx}
            className="px-1.5 py-0.5 mx-0.5 rounded bg-slate-950/80 border border-slate-700/80 text-emerald-300 font-mono text-[11px] sm:text-xs"
          >
            {codePart.slice(1, -1)}
          </code>
        );
      }

      // Process bold **bold**
      const boldParts = codePart.split(/(\*\*[^*]+\*\*)/g);
      return boldParts.map((boldPart, bIdx) => {
        if (boldPart.startsWith('**') && boldPart.endsWith('**') && boldPart.length > 3) {
          const inner = boldPart.slice(2, -2);
          return (
            <strong key={bIdx} className="font-semibold text-white">
              {inner}
            </strong>
          );
        }

        // Process italic *italic* or _italic_
        const italicParts = boldPart.split(/(\*[^*]+\*|_[^_]+_)/g);
        return italicParts.map((italicPart, iIdx) => {
          if (
            (italicPart.startsWith('*') && italicPart.endsWith('*') && italicPart.length > 2) ||
            (italicPart.startsWith('_') && italicPart.endsWith('_') && italicPart.length > 2)
          ) {
            return (
              <em key={iIdx} className="italic text-slate-300">
                {italicPart.slice(1, -1)}
              </em>
            );
          }
          return italicPart;
        });
      });
    });
  };

  // Parse lines to detect blocks
  const lines = content.split('\n');
  const elements: React.ReactNode[] = [];

  let inCodeBlock = false;
  let codeBlockLang = '';
  let codeBlockLines: string[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Check code fence
    if (trimmed.startsWith('```')) {
      if (inCodeBlock) {
        // End of code block
        const codeText = codeBlockLines.join('\n');
        elements.push(
          <CodeBlockItem key={`code-${i}`} code={codeText} lang={codeBlockLang} />
        );
        inCodeBlock = false;
        codeBlockLines = [];
        codeBlockLang = '';
      } else {
        inCodeBlock = true;
        codeBlockLang = trimmed.slice(3).trim() || 'text';
        codeBlockLines = [];
      }
      continue;
    }

    if (inCodeBlock) {
      codeBlockLines.push(line);
      continue;
    }

    // Blank line
    if (!trimmed) {
      elements.push(<div key={`blank-${i}`} className="h-2" />);
      continue;
    }

    // Headers
    if (trimmed.startsWith('### ')) {
      elements.push(
        <h4 key={`h3-${i}`} className="text-sm font-bold text-blue-300 mt-2.5 mb-1 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
          {renderInlineFormatted(trimmed.slice(4))}
        </h4>
      );
      continue;
    }
    if (trimmed.startsWith('## ')) {
      elements.push(
        <h3 key={`h2-${i}`} className="text-sm sm:text-base font-bold text-white mt-3 mb-1.5 pb-1 border-b border-slate-700/50">
          {renderInlineFormatted(trimmed.slice(3))}
        </h3>
      );
      continue;
    }
    if (trimmed.startsWith('# ')) {
      elements.push(
        <h2 key={`h1-${i}`} className="text-base font-extrabold text-white mt-3.5 mb-2 pb-1 border-b border-slate-700">
          {renderInlineFormatted(trimmed.slice(2))}
        </h2>
      );
      continue;
    }

    // Numbered List (e.g. "1. **Title**: text" or "1. text")
    const numMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
    if (numMatch) {
      const num = numMatch[1];
      const rest = numMatch[2];
      elements.push(
        <div key={`num-${i}`} className="flex items-start gap-2.5 my-1.5 text-xs sm:text-sm pl-1">
          <span className="shrink-0 flex items-center justify-center w-5 h-5 rounded-full bg-blue-500/20 border border-blue-400/40 text-[10px] font-bold text-blue-300">
            {num}
          </span>
          <div className="flex-1 leading-relaxed text-slate-200">
            {renderInlineFormatted(rest)}
          </div>
        </div>
      );
      continue;
    }

    // Bullet points (•, -, *)
    if (trimmed.startsWith('• ') || trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      const rest = trimmed.slice(2);
      elements.push(
        <div key={`bullet-${i}`} className="flex items-start gap-2.5 my-1 text-xs sm:text-sm pl-1.5">
          <span className="shrink-0 w-1.5 h-1.5 rounded-full bg-emerald-400 mt-2 shadow-sm shadow-emerald-400/50" />
          <div className="flex-1 leading-relaxed text-slate-200">
            {renderInlineFormatted(rest)}
          </div>
        </div>
      );
      continue;
    }

    // Standard Paragraph
    elements.push(
      <p key={`p-${i}`} className="my-1 leading-relaxed text-slate-200 text-xs sm:text-sm">
        {renderInlineFormatted(trimmed)}
      </p>
    );
  }

  // Flush trailing code block if unclosed
  if (inCodeBlock && codeBlockLines.length > 0) {
    elements.push(
      <CodeBlockItem key="code-final" code={codeBlockLines.join('\n')} lang={codeBlockLang} />
    );
  }

  return <div className="space-y-0.5">{elements}</div>;
};

interface CodeBlockProps {
  code: string;
  lang: string;
}

const CodeBlockItem: React.FC<CodeBlockProps> = ({ code, lang }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-2.5 rounded-xl bg-slate-950 border border-slate-800 overflow-hidden shadow-lg">
      <div className="flex items-center justify-between px-3 py-1.5 bg-slate-900/90 border-b border-slate-800 text-[11px] text-slate-400">
        <span className="flex items-center gap-1.5 font-mono uppercase text-[10px] tracking-wider text-slate-300">
          <Terminal className="w-3 h-3 text-blue-400" />
          {lang || 'code'}
        </span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 px-2 py-0.5 rounded hover:bg-slate-800 text-slate-300 transition text-[11px]"
        >
          {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>
      <pre className="p-3 text-[11px] sm:text-xs font-mono text-emerald-300 overflow-x-auto whitespace-pre leading-relaxed">
        {code}
      </pre>
    </div>
  );
};
