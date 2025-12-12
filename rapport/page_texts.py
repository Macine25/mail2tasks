from pypdf import PdfReader
p='C:/Users/Macine/Documents/mail2tasks/rapport/L2_rapport_BENSAIDmacine_DERRImohammed.pdf'
reader=PdfReader(p)
for i,page in enumerate(reader.pages, start=1):
    txt=page.extract_text() or ''
    print(i, 'chars=', len(txt), 'starts=', repr(txt[:120]))
