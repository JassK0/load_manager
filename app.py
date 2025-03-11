from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session storage

# Configure upload folder and allowed file types
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['INVOICE_FOLDER'] = 'static/invoices'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists(app.config['INVOICE_FOLDER']):
    os.makedirs(app.config['INVOICE_FOLDER'])

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Add enumerate to the Jinja environment
app.jinja_env.globals.update(enumerate=enumerate)

# Route for the Dashboard (Home)
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/user_info')
def user_info():
    return render_template('user_info.html')

# Route for Invoice Info Page
@app.route('/invoice_info')
def invoice_info():
    data = {
        "filename": session.get('filename'),
        "company_name": session.get('company_name'),
        "street": session.get('street'),
        "city": session.get('city'),
        "state": session.get('state'),
        "zip": session.get('zip'),
        "bill_to": session.get('bill_to'),
        "street_name": session.get('street_name'),
        "bill_city": session.get('bill_city'),
        "bill_state": session.get('bill_state'),
        "bill_zip": session.get('bill_zip'),
        "invoice_num": session.get('invoice_num'),
        "invoice_lines": session.get('invoice_lines', [])
    }
    return render_template('invoice_info.html', **data)

# Handle Logo Upload and Company Info
@app.route('/process_user_info', methods=['POST'])
def process_user_info():
    if 'logo' not in request.files:
        return 'No file part'
    
    file = request.files['logo']
    if file.filename == '':
        return 'No selected file'
    
    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Store data in session
        session['filename'] = filename
        session['company_name'] = request.form.get("company_name")
        session['street'] = request.form.get("Street")
        session['city'] = request.form.get("city")
        session['state'] = request.form.get("state")
        session['zip'] = request.form.get("zip")
        session['invoice_num'] = request.form.get("invoice_num")

        return redirect(url_for('invoice_info'))
    return 'File not allowed'

# Handle Billed To Info
@app.route('/process_billed_to', methods=['POST'])
def process_billed_to():
    session['bill_to'] = request.form.get("bill_to")
    session['street_name'] = request.form.get("street_name")
    session['bill_city'] = request.form.get("city")
    session['bill_state'] = request.form.get("state")
    session['bill_zip'] = request.form.get("zip")

    return redirect(url_for('invoice_info'))

# Handle Invoice Line Items
@app.route('/invoice_lines', methods=['POST'])
def process_invoice_lines():
    invoice_lines = session.get('invoice_lines', [])
    line_index = request.form.get("line_index")
    
    new_line = {
        "invoice_date": request.form.get("invoice_date"),
        "invoice_location": request.form.get("invoice_location"),
        "waybill_num": request.form.get("waybill_num"),
        "num_loads": request.form.get("num_loads"),
        "load_price": request.form.get("load_price"),
        "total_price": float(request.form.get("num_loads")) * float(request.form.get("load_price"))
    }

    if line_index and line_index.isdigit():
        index = int(line_index)
        if 0 <= index < len(invoice_lines):
            invoice_lines[index] = new_line
    else:
        invoice_lines.append(new_line)

    session['invoice_lines'] = invoice_lines

    return redirect(url_for('invoice_info'))

# Edit Invoice Line
@app.route('/edit_invoice_line/<int:index>')
def edit_invoice_line(index):
    invoice_lines = session.get('invoice_lines', [])
    if 0 <= index < len(invoice_lines):
        line = invoice_lines[index]
        session['edit_line'] = index
        session['invoice_date'] = line['invoice_date']
        session['invoice_location'] = line['invoice_location']
        session['waybill_num'] = line['waybill_num']
        session['num_loads'] = line['num_loads']
        session['load_price'] = line['load_price']
    return redirect(url_for('invoice_info'))

# Delete Invoice Line
@app.route('/delete_invoice_line/<int:index>')
def delete_invoice_line(index):
    invoice_lines = session.get('invoice_lines', [])
    if 0 <= index < len(invoice_lines):
        del invoice_lines[index]
    session['invoice_lines'] = invoice_lines
    return redirect(url_for('invoice_info'))

# Clear Invoice Data
@app.route('/clear_invoice')
def clear_invoice():
    session.pop('invoice_lines', None)
    session.pop('invoice_num', None)
    session.pop('')
    return redirect(url_for('invoice_info'))

# Serve Uploaded Logo Files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Start the Flask app
if __name__ == '__main__':
    app.run(port=8000, debug=True)
