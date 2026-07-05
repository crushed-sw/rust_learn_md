import os, re, sys

def find_bare_angle_brackets(filepath):
    """Find angle bracket patterns outside code blocks. Returns list of (line_num, line_text, patterns)."""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return results, str(e)

    in_fenced_block = False

    html_tags = {'div', 'span', 'p', 'a', 'li', 'ul', 'ol', 'br', 'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'table', 'tr', 'td', 'th', 'thead', 'tbody', 'strong', 'em', 'b', 'i', 'u', 'pre',
                'img', 'input', 'form', 'button', 'label', 'select', 'option', 'textarea',
                'head', 'body', 'html', 'meta', 'link', 'title', 'style', 'script',
                'header', 'footer', 'nav', 'main', 'section', 'article', 'aside',
                'summary', 'details', 'figure', 'figcaption', 'blockquote', 'cite',
                'code', 'kbd', 'samp', 'var', 'sub', 'sup', 'small', 'mark', 'del', 'ins',
                'wbr', 'abbr', 'time', 'data', 'output', 'progress', 'meter', 'fieldset', 'legend',
                'iframe', 'canvas', 'video', 'audio', 'source', 'track', 'object', 'embed', 'param',
                'noscript', 'template', 'slot', 'dialog', 'menu', 'menuitem', 'area', 'base', 'col',
                'colgroup', 'command', 'datalist', 'keygen', 'map'}

    for i, line in enumerate(lines, 1):
        stripped = line.rstrip('\n\r')

        # Detect fenced code blocks (triple backticks or tildes)
        fence_match = re.match(r'^(\s*)(`{3,}|~{3,})\s*(.*)', stripped)
        if fence_match:
            if not in_fenced_block:
                in_fenced_block = True
            else:
                in_fenced_block = False
            continue

        if in_fenced_block:
            continue

        # Outside fenced block. Remove inline code spans.
        # Replace single backtick code spans
        cleaned = re.sub(r'`[^`]+`', ' CODESPAN ', stripped)
        # Replace double backtick code spans
        cleaned = re.sub(r'``[^`]+``', ' CODESPAN ', cleaned)

        # Search for Rust-like angle bracket patterns
        # <TypeName>, <Generic<Inner>>, <&ref>, <dyn Trait>
        pattern = r'<(?:[A-Z][A-Za-z0-9_]*(?:::[\w]+)*|&[\w]+|dyn\s+\w+)(?:\s*<[^>]*>)?>'

        found = []
        for m in re.finditer(pattern, cleaned):
            matched = m.group()
            # Filter out HTML tags
            inner = matched[1:-1].strip()  # content between < >
            first_word = inner.split()[0].lower() if inner else ''
            # Also check for things like <br/>, <br />
            if first_word.rstrip('/') in html_tags:
                continue
            # Skip things that look like HTML attributes: <tag attr=val>
            if '=' in inner and first_word in html_tags:
                continue
            found.append(matched)

        if found:
            results.append((i, stripped.strip(), found))

    return results, None

base_dir = os.getcwd()

# Find all .md files
md_files = []
for root, dirs, files in os.walk('.'):
    # Skip hidden dirs
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for f in files:
        if f.endswith('.md') and not f.startswith('_'):
            md_files.append(os.path.join(root, f))

md_files.sort()

total_files_with_issues = 0
grand_total_bare = 0

for filepath in md_files:
    results, error = find_bare_angle_brackets(filepath)
    if error:
        print(f'ERROR: {filepath}: {error}')
        continue
    if not results:
        continue

    total_files_with_issues += 1
    count = len(results)
    grand_total_bare += count

    # Determine category
    phase = ''
    if 'phase1-type-system' in filepath:
        phase = '[Phase1]'
    elif 'phase2-memory' in filepath:
        phase = '[Phase2]'
    else:
        phase = '[Other]'

    print(f'')
    print(f'=== {phase} {filepath} ({count} bare occurrences) ===')
    # Show up to 8 examples
    for line_num, line_text, patterns in results[:8]:
        display = line_text[:150].replace('\n', ' ')
        print(f'  L{line_num}: {display}')
        print(f'         Patterns: {patterns}')
    if count > 8:
        print(f'  ... and {count - 8} more occurrences')

print(f'')
print(f'=== SUMMARY ===')
print(f'Total files with bare angle brackets: {total_files_with_issues}')
print(f'Total bare occurrences: {grand_total_bare}')
