from pathlib import Path
import fitz

doc = fitz.open(r'C:\Users\ronal\Downloads\CHOQUE CALLISAYA EDDY.pdf')
page = doc[-1]
words = page.get_text('words')
target = page.search_for('GESTION TURISTICA MUNICIPAL')[-1]
changes = []
for word in words:
    if abs(word[1] - target.y0) < 3 and word[4] in ('85', 'APROBADO'):
        changes.append((fitz.Rect(word[:4]), '40' if word[4] == '85' else 'REPROBADO'))
assert len(changes) == 2, changes
for rect, text in changes:
    page.add_redact_annot(rect, fill=(1,1,1))
page.apply_redactions()
for rect, text in changes:
    page.insert_text((rect.x0, rect.y1 - 1.5), text, fontsize=6, fontname='helv')
for p in doc:
    p.insert_text((25, p.rect.height - 12), 'COPIA DE PRUEBA - MODIFICADA PARA VALIDACION DEL SISTEMA - SIN VALIDEZ ACADEMICA', fontsize=7, color=(0.8,0,0))
out = Path('output/pdf/historial_prueba_reprobado.pdf')
out.parent.mkdir(parents=True, exist_ok=True)
doc.save(out)
page.get_pixmap(matrix=fitz.Matrix(2,2)).save('tmp/pdfs/revision.png')
print(out.resolve())
