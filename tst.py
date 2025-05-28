
import fitz

doc = fitz.open("/home/zishan/Documents/Reading/Minimalist White and Grey Professional Resume.pdf")
text = "\n".join(page.get_text() for page in doc)

print(text)