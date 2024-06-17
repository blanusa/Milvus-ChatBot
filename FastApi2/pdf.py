from reportlab.pdfgen.canvas import Canvas 
canvas = Canvas("hello.pdf")
canvas.drawString(72, 72, "Hello, World!")
canvas.drawString(150,150,str(123123123123))
canvas.save()