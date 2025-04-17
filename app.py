# app.py
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
    error = None
    
    if 'pdf' not in request.files:
        error = "No file selected"
    else:
        file = request.files['pdf']
        if file.filename == '':
            error = "No file selected"
        elif not file.filename.lower().endswith('.pdf'):
            error = "Only PDF files allowed"
        else:
            try:
                # Save the file
                filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filename)
                
                # Check for timeout
                if time.time() - start_time > 5:
                    error = "Upload took too long"
                else:
                    # Process the PDF
                    text = extract_text_from_pdf(filename)
                    companies = parse_companies(text)[:50]  # Limit to first 50 companies
                    
                    # Enrich company data
                    enriched = [enrich_company_data(c) for c in companies]
                    top_companies = get_top_10(enriched)
                    
                    # Check for timeout again
                    if time.time() - start_time > 10:
                        error = "Processing took too long"
                    else:
                        # Generate PDF
                        if generate_pdf(top_companies, OUTPUT_PDF):
                            print(f"Generated PDF in {time.time()-start_time:.2f}s")
                            return render_template("index.html", pdf_ready=True, error=None)
                        else:
                            error = "Failed to generate PDF"
            except Exception as e:
                error = f"Error processing file: {str(e)}"
    
    # If we get here, there was an error
    return render_template("index.html", pdf_ready=False, error=error)

@app.route("/download")
def download():
    try:
        return send_file(OUTPUT_PDF, as_attachment=True)
    except Exception as e:
        return render_template("index.html", pdf_ready=False, error=f"Download error: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True, threaded=True)