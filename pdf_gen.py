from reportlab.pdfgen import canvas

# Create a PDF document
pdf_file_path = "example.pdf"
pdf = canvas.Canvas(pdf_file_path)

# Add text to the PDF
pdf.setFont("Helvetica", 12)
pdf.drawString(50, 700, "Hello, this is a PDF generated with reportlab.")
pdf.drawString(50, 680, "You can add more text here.")

# Save the PDF
pdf.save()

print(f"PDF saved to {pdf_file_path}")