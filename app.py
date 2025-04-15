from flask import Flask, request, render_template, send_file
import os
from parser import extract_text_from_pdf, parse_companies, get_top_10
from pdf_writer import generate_pdf

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_PDF = 'top_companies.pdf'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", pdf_ready=False)

@app.route("/upload", methods=["POST"])
def upload():
    if 'pdf' not in request.files:
        return "No PDF file found", 400

    file = request.files['pdf']
    if file.filename == '':
        return "No selected file", 400

    try:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        ai_weight = int(request.form.get("ai_weight", 1))
        platform_weight = int(request.form.get("platform_weight", 1))
        revenue_weight = int(request.form.get("revenue_weight", 1))

        text = extract_text_from_pdf(filename)
        companies = parse_companies(text)
        top_companies = get_top_10(companies, ai_weight, platform_weight, revenue_weight)

        # Debug output
        print(f"Processing {len(top_companies)} companies")
        for i, c in enumerate(top_companies[:3]):
            print(f"Company {i}: {c.get('name')[:50]}...")

        if not generate_pdf(top_companies, OUTPUT_PDF):
            return "Failed to generate PDF", 500

        return render_template("index.html", pdf_ready=True)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error processing file: {str(e)}", 500

@app.route("/download")
def download():
    return send_file(OUTPUT_PDF, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)



# from flask import Flask, request, render_template, send_file
# import os
# from parser import extract_text_from_pdf, parse_companies, get_top_10
# from pdf_writer import generate_pdf

# app = Flask(__name__)
# UPLOAD_FOLDER = 'uploads'
# OUTPUT_PDF = 'top_companies.pdf'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @app.route("/", methods=["GET"])
# def index():
#     return render_template("index.html", pdf_ready=False)

# @app.route("/upload", methods=["POST"])
# def upload():
#     if 'pdf' not in request.files:
#         return "No PDF file found", 400

#     file = request.files['pdf']
#     if file.filename == '':
#         return "No selected file", 400

#     try:
#         filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#         file.save(filename)
        
#         # Get weights
#         ai_weight = int(request.form.get("ai_weight", 1))
#         platform_weight = int(request.form.get("platform_weight", 1))
#         revenue_weight = int(request.form.get("revenue_weight", 1))

#         # Process PDF
#         text = extract_text_from_pdf(filename)
#         companies = parse_companies(text)
        
#         # Filter out any problematic companies
#         safe_companies = []
#         for company in companies:
#             try:
#                 # Test if text can be cleaned
#                 test_text = clean_text(company.get("description", ""))
#                 safe_companies.append(company)
#             except:
#                 continue
                
#         top_companies = get_top_10(safe_companies, ai_weight, platform_weight, revenue_weight)
        
#         generate_pdf(top_companies, OUTPUT_PDF)
#         return render_template("index.html", pdf_ready=True)
    
#     except Exception as e:
#         return f"Error processing file: {str(e)}", 500

# @app.route("/download")
# def download():
#     return send_file(OUTPUT_PDF, as_attachment=True)

# if __name__ == "__main__":
#     app.run(debug=True)