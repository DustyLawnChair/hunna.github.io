from pathlib import Path
import html

POSTS_DIR = Path("posts")
OUTPUT_DIR = Path("blog/posts")
BLOG_INDEX = Path("blog/index.html")


def get_metadata(markdown):
    lines = markdown.strip().splitlines()

    title = "Untitled Post"
    date = ""

    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()

        elif line.startswith("Date: "):
            date = line[6:].strip()

    return title, date


def markdown_to_html(markdown):
    lines = markdown.strip().splitlines()

    output = []
    paragraph_lines = []

    def close_paragraph():
        if paragraph_lines:
            text = " ".join(paragraph_lines)
            output.append(f"<p>{html.escape(text)}</p>")
            paragraph_lines.clear()

    for line in lines:
        line = line.strip()

        # Ignore metadata
        if line.startswith("Date: "):
            continue

        # Blank line = end paragraph
        if not line:
            close_paragraph()
            continue

        # H1
        if line.startswith("# "):
            close_paragraph()
            title = html.escape(line[2:].strip())
            output.append(f"<h1>// {title}</h1>")
            continue

        # H2
        if line.startswith("## "):
            close_paragraph()
            heading = html.escape(line[3:].strip())
            output.append(f"<h2>{heading}</h2>")
            continue

        # Bullet list
        if line.startswith("- "):
            close_paragraph()

            if not output or not output[-1].startswith("<ul>"):
                output.append("<ul>")

            item = html.escape(line[2:].strip())
            output.append(f"<li>{item}</li>")
            continue

        # End bullet list
        if output and output[-1].startswith("<li>") and not line.startswith("- "):
            output.append("</ul>")

        # Regular paragraph
        paragraph_lines.append(line)

    close_paragraph()

    # Close list if the final element was a list item
    if output and output[-1].startswith("<li>"):
        output.append("</ul>")

    return "\n".join(output)


def get_summary(markdown):
    lines = markdown.strip().splitlines()

    paragraph = []

    for line in lines:
        line = line.strip()

        if not line:
            if paragraph:
                break
            continue

        if line.startswith("# ") or line.startswith("Date: "):
            continue

        if line.startswith("- "):
            continue

        paragraph.append(line)

    summary = " ".join(paragraph)

    if len(summary) > 160:
        summary = summary[:157] + "..."

    return summary


def build_post(markdown_file):
    markdown = markdown_file.read_text(encoding="utf-8")

    title, date = get_metadata(markdown)
    content = markdown_to_html(markdown)

    output_file = OUTPUT_DIR / f"{markdown_file.stem}.html"

    page = f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>{html.escape(title)} - Hunna.dev</title>

    <link rel="stylesheet" href="../../style.css">
    <link rel="icon" type="image/png" href="../../favicon.png">
</head>

<body>

    <header>
        <nav>
            <a href="../../" class="logo">hunna.dev</a>

            <div class="nav-links">
                <a href="../../">// home</a>
                <a href="../">// blog</a>
            </div>
        </nav>
    </header>

    <main>

        <section class="blog-entry">

            <p class="terminal-line">$ cat {markdown_file.stem}.log</p>

            {content}

            <p>
                <a href="../">// ← Back to blog</a>
            </p>

        </section>

    </main>

    <footer>
        <p>© 2026 Hunter</p>
        <p>Built from scratch.</p>
    </footer>

</body>

</html>
"""

    output_file.write_text(page, encoding="utf-8")

    print(f"Built: {output_file}")


def build_index(posts):
    post_entries = []

    for markdown_file in posts:
        markdown = markdown_file.read_text(encoding="utf-8")

        title, date = get_metadata(markdown)
        summary = get_summary(markdown)

        post_entries.append(
            f"""
            <article class="blog-post">

                <p class="blog-date">{html.escape(date)}</p>

                <h2>
                    <a href="posts/{markdown_file.stem}.html">
                        {html.escape(title)}
                    </a>
                </h2>

                <p>{html.escape(summary)}</p>

            </article>
            """
        )

    posts_html = "\n".join(post_entries)

    page = f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Hunna.dev - Blog</title>

    <link rel="stylesheet" href="../style.css">
    <link rel="icon" type="image/png" href="../favicon.png">
</head>

<body>

    <header>
        <nav>

            <a href="../" class="logo">hunna.dev</a>

            <div class="nav-links">
                <a href="../">// home</a>
                <a href="../#about">// about</a>
                <a href="../#experience">// experience</a>
                <a href="../#projects">// projects</a>
                <a href="../#skills">// skills</a>
                <a href="../#education">// education</a>
                <a href="../#contact">// contact</a>
            </div>

        </nav>
    </header>

    <main>

        <section id="blog">

            <p class="terminal-line">$ ls ./posts</p>

            <h1>// Blog</h1>

            <div class="blog-posts">

                {posts_html}

            </div>

        </section>

    </main>

    <footer>
        <p>© 2026 Hunter</p>
        <p>Built from scratch.</p>
    </footer>

</body>

</html>
"""

    BLOG_INDEX.write_text(page, encoding="utf-8")

    print(f"Built: {BLOG_INDEX}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    markdown_files = sorted(
        POSTS_DIR.glob("*.md"),
        reverse=True
    )

    if not markdown_files:
        print("No Markdown posts found.")
        return

    for markdown_file in markdown_files:
        build_post(markdown_file)

    build_index(markdown_files)

    print("Blog build complete.")


if __name__ == "__main__":
    main()