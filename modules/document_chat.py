
from io import BytesIO
from pypdf import PdfReader
from pptx import Presentation


def extract_document_text(uploaded_file):
    """Extract readable text from PDF or PowerPoint."""

    full_text = ""

    try:
        file_name = uploaded_file.name.lower()
        file_bytes = BytesIO(uploaded_file.getvalue())

        if file_name.endswith(".pdf"):
            pdf = PdfReader(file_bytes)

            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                full_text += f"\nPage {page_number}:\n{text}"

        elif file_name.endswith(".pptx"):
            presentation = Presentation(file_bytes)

            for slide_number, slide in enumerate(
                presentation.slides, start=1
            ):
                full_text += f"\nSlide {slide_number}:\n"

                for shape in slide.shapes:
                    if shape.has_text_frame:
                        full_text += shape.text + "\n"

        else:
            return None, "Unsupported file format."

        if not full_text.strip():
            return None, "No readable text found in this document."

        return full_text, None

    except Exception as e:
        return None, f"Document reading error: {e}"


def create_document_prompt(document_text, question, history):
    """Prepare a prompt using document content and chat history."""

    conversation = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in history[-6:]
    )

    return f"""
You are MILO, a helpful document assistant.

Answer questions using the provided document.
If the answer is not available in the document,
clearly say that.

DOCUMENT:
{document_text[:30000]}

PREVIOUS CONVERSATION:
{conversation}

QUESTION:
{question}
"""
