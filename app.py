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

# In app.py, modify the upload route
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
                
                if time.time() - start_time > 5:
                    error = "Upload took too long"
                else:
                    text = extract_text_from_pdf(filename)
                    companies = parse_companies(text)
                    
                    # Get weights from form
                    weights = {
                        'revenue_weight': float(request.form.get('revenue_weight', 1)),
                        'growth_weight': float(request.form.get('growth_weight', 1)),
                        'profitability_weight': float(request.form.get('profitability_weight', 1)),
                        'industry_weight': float(request.form.get('industry_weight', 1)),
                        'size_weight': float(request.form.get('size_weight', 1)),
                        'selected_industries': request.form.getlist('industry')  # Get all checked industries
                    }
                    
                    enriched = [enrich_company_data(c) for c in companies]
                    top_companies = get_top_10(enriched, weights)
                    
                    if time.time() - start_time > 10:
                        error = "Processing took too long"
                    else:
                        if generate_pdf(top_companies, OUTPUT_PDF):
                            return render_template("index.html", pdf_ready=True, error=None)
                        else:
                            error = "Failed to generate PDF"
            except Exception as e:
                error = f"Error processing file: {str(e)}"
                print(f"Error details: {str(e)}")
                import traceback
                traceback.print_exc()
    
    return render_template("index.html", pdf_ready=False, error=error)

@app.route("/download")
def download():
    try:
        return send_file(OUTPUT_PDF, as_attachment=True)
    except Exception as e:
        return render_template("index.html", pdf_ready=False, error=f"Download error: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True, threaded=True)