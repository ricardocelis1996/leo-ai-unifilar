import streamlit as st
import pandas as pd
import ezdxf
import io
from fpdf import FPDF

# --- Función para generar el diagrama unifilar (DXF) ---
import tempfile
import os

def generar_unifilar(df):
    doc = ezdxf.new(dxfversion='R2010')
    msp = doc.modelspace()

    x = 0
    y = 0
    dx = 40

    for index, row in df.iterrows():
        equipo = row['Equipo']
        tipo = row['Tipo']
        potencia = row['Potencia (MVA)']
        tension = row['Tensión (kV)']

        # Dibujar símbolo
        if tipo == "Transformador":
            msp.add_circle(center=(x, y), radius=5, dxfattribs={"color": 1})
        elif tipo == "Interruptor":
            breaker_size = 5
            msp.add_lwpolyline([
                (x - breaker_size, y - breaker_size),
                (x + breaker_size, y - breaker_size),
                (x + breaker_size, y + breaker_size),
                (x - breaker_size, y + breaker_size),
                (x - breaker_size, y - breaker_size),
            ], dxfattribs={"color": 3})
        elif tipo == "Barra":
            msp.add_line((x, y - 5), (x, y + 5), dxfattribs={"color": 5, "lineweight": 50})
        else:
            msp.add_circle(center=(x, y), radius=3, dxfattribs={"color": 6})

        # Texto nombre
        msp.add_text(equipo, dxfattribs={"height": 2.5}).set_placement((x - 5, y - 10))
        # Texto potencia
        if pd.notna(potencia):
            msp.add_text(f"{potencia} MVA", dxfattribs={"height": 2}).set_placement((x - 5, y - 15))
        # Texto tensión
        if pd.notna(tension):
            msp.add_text(f"{tension} kV", dxfattribs={"height": 2}).set_placement((x - 5, y - 20))

        # Línea de conexión
        if index < len(df) - 1:
            msp.add_line((x + 5, y), (x + dx - 5, y), dxfattribs={"color": 7})

        x += dx

    # 👉 Guardamos en un archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp_file:
        doc.saveas(tmp_file.name)
        tmp_file_path = tmp_file.name

    # 👉 Leemos el archivo como bytes
    with open(tmp_file_path, "rb") as f:
        dxf_bytes = f.read()

    # 👉 Eliminamos el archivo temporal
    os.remove(tmp_file_path)

    return dxf_bytes


    # Guardar en memoria
    buffer = io.BytesIO()
    doc.write_stream(buffer)
    buffer.seek(0)
    return buffer

# --- Función para generar la memoria técnica (PDF) ---
def generar_memoria_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Memoria Técnica - Unifilar", ln=True, align='C')

    pdf.ln(10)

    # Encabezados
    pdf.set_font("Arial", style="B", size=10)
    pdf.cell(40, 10, txt="Equipo", border=1)
    pdf.cell(30, 10, txt="Tipo", border=1)
    pdf.cell(40, 10, txt="Potencia (MVA)", border=1)
    pdf.cell(40, 10, txt="Tensión (kV)", border=1)
    pdf.ln()

    pdf.set_font("Arial", size=10)
    for index, row in df.iterrows():
        pdf.cell(40, 10, txt=str(row['Equipo']), border=1)
        pdf.cell(30, 10, txt=str(row['Tipo']), border=1)
        pdf.cell(40, 10, txt=str(row['Potencia (MVA)']), border=1)
        pdf.cell(40, 10, txt=str(row['Tensión (kV)']), border=1)
        pdf.ln()

    # 👉 Obtener el bytearray
    pdf_output = pdf.output(dest='S')

    # 👉 Convertir a bytes
    return bytes(pdf_output)

# --- Streamlit App ---
st.title("⚡ Generador de Unifilares + Memoria Técnica")
st.write("Sube tu archivo Excel y genera el diagrama unifilar en DXF y su memoria técnica en PDF.")

# Subida de archivo
uploaded_file = st.file_uploader("📂 Sube tu archivo Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader("🔎 Vista previa de tus datos")
    st.dataframe(df)

    if st.button("🚀 Generar Unifilar y Memoria Técnica"):
        # Generar archivos
        dxf_file = generar_unifilar(df)
        pdf_file = generar_memoria_pdf(df)

        st.success("✅ Archivos generados exitosamente.")

        # Botón para descargar DXF
        st.download_button(
            label="📥 Descargar Diagrama Unifilar (DXF)",
            data=dxf_file,
            file_name="unifilar_generado.dxf",
            mime="application/dxf"
        )

        # Botón para descargar PDF
        st.download_button(
            label="📄 Descargar Memoria Técnica (PDF)",
            data=pdf_file,
            file_name="memoria_tecnica.pdf",
            mime="application/pdf"
        )
