from flask import Flask, request, render_template, send_file
import os
from parser import extract_text_from_pdf, parse_companies, get_top_10
from pdf_writer import generate_pdf
from scraper import enrich_company_data
import time

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
UPLOAD_FOLDER = 'uploads'
OUTPUT_PDF = 'top_companies.pdf'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", pdf_ready=False)

@app.route("/upload", methods=["POST"])
def upload():
    start_time = time.time()
    
    if 'pdf' not in request.files:
        return render_template("index.html", error="No file selected", pdf_ready=False)

    file = request.files['pdf']
    if file.filename == '':
        return render_template("index.html", error="No file selected", pdf_ready=False)

    try:
        # Fast file type check
        if not file.filename.lower().endswith('.pdf'):
            return render_template("index.html", error="Only PDF files allowed", pdf_ready=False)

        # Save with timeout check
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        if time.time() - start_time > 5:  # 5 second timeout for upload
            return render_template("index.html", error="Upload took too long", pdf_ready=False)

        # Process with timeout checks
        text = extract_text_from_pdf(filename)
        companies = parse_companies(text)[:50]  # Limit to first 50 companies
        
        # Fast enrichment
        enriched = [enrich_company_data(c) for c in companies]
        top_companies = get_top_10(enriched)
        
        # Generate PDF with timeout
        if time.time() - start_time > 10:  # 10 second total timeout
            return render_template("index.html", error="Processing took too long", pdf_ready=False)
        
        if generate_pdf(top_companies, OUTPUT_PDF):
            print(f"Generated PDF in {time.time()-start_time:.2f}s")
            return render_template("index.html", pdf_ready=True)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return render_template("index.html", error=str(e), pdf_ready=False)

@app.route("/download")
def download():
    return send_file(OUTPUT_PDF, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, threaded=True)