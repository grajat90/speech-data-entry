import speech_recognition as sr
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

#initializers for voice recognition
rec = sr.Recognizer()
mic = sr.Microphone()
response=[]
x = 180
y = 787

#initializers for pdf generation
packet = io.BytesIO()
# create a new PDF with Reportlab
can = canvas.Canvas(packet, pagesize=A4)



#parse the voice recognition output to remove garbage and uniformize
def parse(response):
    response = response.split('next')
    for i in range(0,len(response)):
        try:
            response.remove('')
            response.remove(' ')
        except ValueError:
            pass
    for i in range(0,len(response)):
        element = response[i]
        element = element.split(' ')
        try:
            element.remove('')
        except ValueError:
            pass
        for j in range(0,len(element)):
            if element[j] == 'plus':
                element[j] = '+'
        element = ' '.join(word for word in element)
        response[i] = element
    return response

#add to pdf canvas
def magic(res):
    global x
    global y
    for response in res:
        textobject = can.beginText()
        textobject.setFont('Helvetica', 10)
        textobject.setTextOrigin(x, y)
        textobject.textLine(text=response)
        can.drawText(textobject)
        if y==37:
            x = 440
            y = 802
        y = y-15

#main interative voice record + recognize + send to magic
with mic as source:
    rec.adjust_for_ambient_noise(source)
    print("speak...")
    while "finish" not in response:
        audio = rec.listen(source)
        try:
            response = rec.recognize_google(audio)
            if "next" in response:
                response = parse(response)
                magic(response)
                print("Added...")
        except sr.RequestError:
            print("Check connection")
        except sr.UnknownValueError:
            pass
        else:
            pass


#save to pdf

can.save()
#move to the beginning of the StringIO buffer
packet.seek(0)
new_pdf = PdfFileReader(packet)
# read your existing PDF
existing_pdf = PdfFileReader(open("original.pdf", "rb"))
output = PdfFileWriter()
# add the "watermark" (which is the new pdf) on the existing page
page = existing_pdf.getPage(0)
page.mergePage(new_pdf.getPage(0))
output.addPage(page)
# finally, write "output" to a real file
outputStream = open("destination.pdf", "wb")
output.write(outputStream)
outputStream.close()
