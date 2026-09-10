import random
import uuid
from datetime import datetime
from pathlib import Path
from typing import Union


class HTMLAdder:
    """Generates and injects dynamic HTML structures, metadata, and body components

    to guarantee distinct markup signatures across synthetic files.
    """

    def __init__(self):
        self.mock_authors = ["DevOps Pipeline", "Content Engine v2", "System Admin", "Data Migration Bot"]
        self.banner_styles = ["info", "warning", "success", "notice"]

    def _generate_meta_tag(self) -> str:
        """Generates a dynamic meta tag or comment string."""
        build_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        author = random.choice(self.mock_authors)
        
        tags = [
            f'<meta name="build-id" content="BUILD-{build_id}">',
            f'<meta name="generated-at" content="{timestamp}">',
            f'<meta name="author" content="{author}">',
            f'<!-- Automated Hydration Build Ref: {build_id} -->'
        ]
        return random.choice(tags)

    def _generate_synthetic_section(self) -> str:
        """Creates a standalone block of HTML markup to inject."""
        section_id = f"sec-{random.randint(100, 999)}"
        style_class = random.choice(self.banner_styles)
        value = round(random.uniform(10.0, 500.0), 2)

        blocks = [
            (
                f'  <section id="{section_id}" class="banner-{style_class}">\n'
                f'    <h3>System Metric #{random.randint(10, 99)}</h3>\n'
                f'    <p>Automated verification checkpoint logged at {datetime.now().strftime("%H:%M:%S")}.</p>\n'
                f'  </section>'
            ),
            (
                f'  <div id="data-widget-{section_id}" class="card">\n'
                f'    <h4>Session Stat</h4>\n'
                f'    <span class="badge">Value: ${value}</span>\n'
                f'  </div>'
            ),
            (
                f'  <!-- Injected Audit Node {section_id} -->\n'
                f'  <aside class="sidebar-box">\n'
                f'    <p>Status: Active | Reference: {str(uuid.uuid4())[:6]}</p>\n'
                f'  </aside>'
            )
        ]
        return random.choice(blocks)

    def inject_and_rearrange(self, file_path: Union[str, Path]) -> None:
        """Reads target HTML file, injects dynamic head metadata and body components,

        rearranges top-level body sections, and writes back to disk.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Target file not found: {path}")

        content = path.read_text(encoding="utf-8")

        # 1. Inject dynamic meta tags into <head> if present
        if "</head>" in content:
            meta_tag = f"  {self._generate_meta_tag()}\n"
            content = content.replace("</head>", f"{meta_tag}</head>", 1)
        else:
            content = f"{self._generate_meta_tag()}\n{content}"

        # 2. Inject dynamic body sections
        new_section = self._generate_synthetic_section()

        if "</body>" in content:
            content = content.replace("</body>", f"{new_section}\n</body>", 1)
        else:
            content += f"\n{new_section}"

        # 3. Rearrange existing block elements if multiple exist
        # Basic block splitting around section dividers
        if "<section" in content and "</section>" in content:
            parts = content.split("</section>")
            if len(parts) > 2:
                # Keep head/prefix and footer/suffix, shuffle mid sections
                head_part = parts[0] + "</section>"
                tail_part = parts[-1]
                mid_sections = [p + "</section>" for p in parts[1:-1]]
                
                random.shuffle(mid_sections)
                content = head_part + "".join(mid_sections) + tail_part

        path.write_text(content, encoding="utf-8")


def modify_html(file_path: Union[str, Path]) -> str:
    """Helper functional wrapper for integration into pipeline content modifiers."""
    adder = HTMLAdder()
    adder.inject_and_rearrange(file_path)
    return "html_hydrated_and_rearranged"