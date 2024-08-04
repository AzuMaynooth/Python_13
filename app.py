from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages

# Sample data for stock level and account balance
data = {
    "stock_level": 1000,
    "account_balance": 5000
}

# List to store transaction records
transactions = []


@app.route('/')
def main():
    return render_template('main.html', stock_level=data['stock_level'], account_balance=data['account_balance'])

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    if request.method == 'POST':
        product_name = request.form['product-name']
        unit_price = request.form['unit-price']
        num_pieces = request.form['number-pieces']

        # Validate form data
        if not product_name or not unit_price or not num_pieces:
            flash('Please fill in all fields')
            return redirect(url_for('purchase'))

        try:
            unit_price = float(unit_price)
            num_pieces = int(num_pieces)

            if unit_price <= 0 or num_pieces < 1:
                flash('Invalid input: Unit price must be greater than zero and number of pieces must be at least 1')
                return redirect(url_for('purchase'))

            # Update data
            data['stock_level'] += num_pieces
            data['account_balance'] -= unit_price * num_pieces

            # Record transaction
            transactions.append({
                'id': len(transactions) + 1,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'description': f'Purchase of {num_pieces} pieces of {product_name} at ${unit_price:.2f} each'
            })
            save_transactions()  # Save to file

            flash('Purchase recorded successfully')
            return redirect(url_for('purchase'))

        except ValueError:
            flash('Invalid input: Please enter valid numbers for unit price and number of pieces')
            return redirect(url_for('purchase'))

    return render_template('purchase.html')

@app.route('/sale', methods=['GET', 'POST'])
def sale():
    if request.method == 'POST':
        product_name = request.form['product-name']
        unit_price = request.form['unit-price']
        num_pieces = request.form['number-pieces']

        # Validate form data
        if not product_name or not unit_price or not num_pieces:
            flash('Please fill in all fields')
            return redirect(url_for('sale'))

        try:
            unit_price = float(unit_price)
            num_pieces = int(num_pieces)

            if unit_price <= 0 or num_pieces < 1:
                flash('Invalid input: Unit price must be greater than zero and number of pieces must be at least 1')
                return redirect(url_for('sale'))

            if num_pieces > data['stock_level']:
                flash('Insufficient stock for sale')
                return redirect(url_for('sale'))

            # Update data
            data['stock_level'] -= num_pieces
            data['account_balance'] += unit_price * num_pieces

            # Record transaction
            transactions.append({
                'id': len(transactions) + 1,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'description': f'Sale of {num_pieces} pieces of {product_name} at ${unit_price:.2f} each'
            })
            save_transactions()  # Save to file

            flash('Sale recorded successfully')
            return redirect(url_for('sale'))

        except ValueError:
            flash('Invalid input: Please enter valid numbers for unit price and number of pieces')
            return redirect(url_for('sale'))

    return render_template('sale.html')

@app.route('/balance', methods=['GET', 'POST'])
def balance():
    if request.method == 'POST':
        action = request.form['action']
        amount = request.form['amount']

        # Validate form data
        if not action or not amount:
            flash('Please fill in all fields')
            return redirect(url_for('balance'))

        try:
            amount = float(amount)

            if action == 'add':
                data['account_balance'] += amount
                description = f'Added €{amount:.2f} to account balance'
            elif action == 'subtract':
                data['account_balance'] -= amount
                description = f'Subtracted €{amount:.2f} from account balance'
            else:
                flash('Invalid action selected')
                return redirect(url_for('balance'))

            # Record the balance change transaction
            transactions.append({
                'id': len(transactions) + 1,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'description': description
            })
            save_transactions()  # Save to file

            flash('Balance change recorded successfully')
            return redirect(url_for('balance'))

        except ValueError:
            flash('Invalid input: Please enter a valid number for amount')
            return redirect(url_for('balance'))

    return render_template('balance.html')

@app.route('/get_status', methods=['GET'])
def get_status():
    return jsonify({
        'stock_level': data['stock_level'],
        'account_balance': data['account_balance']
    })

@app.route('/api/data')
def api_data():
    return {
        'stock_level': data['stock_level'],
        'account_balance': data['account_balance']
    }


# Sample data (Replace with actual data source)


@app.route('/history/', methods=['GET'])
def get_history():
    # Check if the request is AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from_date_str = request.args.get('from')
        to_date_str = request.args.get('to')

        filtered_records = transactions

        if from_date_str and to_date_str:
            try:
                from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
                to_date = datetime.strptime(to_date_str, '%Y-%m-%d')
                filtered_records = [record for record in transactions if from_date <= datetime.strptime(record["date"], '%Y-%m-%d') <= to_date]
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

        return jsonify(filtered_records)

    # Render the history page with filters
    return render_template('history.html')



transactions_file = 'transactions.json'
# Load transactions from file if it exists
if os.path.exists(transactions_file):
    with open(transactions_file, 'r') as file:
        transactions = json.load(file)
else:
    transactions = []
def save_transactions():
    with open(transactions_file, 'w') as file:
        json.dump(transactions, file)
    #print(f'Transactions saved to {transactions_file}')
    #print(json.dumps(transactions, indent=4))



if __name__ == '__main__':
    app.run(debug=True)
