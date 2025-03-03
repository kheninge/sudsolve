import markdown
from PySide6.QtWidgets import  QTextBrowser, QVBoxLayout, QDialog
from PySide6.QtGui import QShortcut, QKeySequence


class MarkdownViewer(QDialog):
    def __init__(self, file):
        super().__init__()

        self.setWindowTitle("Help")
        self.setGeometry(100, 100, 1000, 1200)
        self.setModal(True)
        
        self.main_layout = QVBoxLayout(self)
        
        # Define Shortcuts
        shortcuts = {
            "q": self.close,
        }
        for k, func in shortcuts.items():
            QShortcut(QKeySequence(k), self).activated.connect(func)

        # Create text browser for displaying markdown
        self.text_browser = QTextBrowser()
        self.main_layout.addWidget(self.text_browser)
        
        with open(file, 'r', encoding='utf-8') as file:
            markdown_text = file.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            markdown_text,
            extensions=['tables', 'fenced_code', 'codehilite']
        )
        
        # Apply some basic CSS for better appearance
        styled_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #444; }}
                code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 4px; }}
                pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto; }}
                blockquote {{ border-left: 4px solid #ddd; padding-left: 10px; color: #666; }}
                img {{ max-width: 100%; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Set the HTML content in the text browser
        self.text_browser.setHtml(styled_html)
