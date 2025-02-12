from flask import Flask, render_template, request
from datetime import datetime
import attendance

app = Flask(__name__)

# Global visitor counter
visitor_count = 0

@app.route('/', methods=['GET', 'POST'])
def index():
    global visitor_count
    visitor_count += 1  # Increment visitor count

    if request.method == 'POST':
        form_data = {
            'attended': int(request.form['attended']),
            'conducted': int(request.form['conducted']),
            'deadline': datetime.strptime(request.form['deadline'], '%Y-%m-%d').date(),
            'today': datetime.now().date()
        }
        
        if request.form.get('simulate_skip'):
            form_data.update({
                'skip_start': datetime.strptime(request.form['skip_start'], '%Y-%m-%d').date(),
                'skip_end': datetime.strptime(request.form['skip_end'], '%Y-%m-%d').date(),
                'skipped_lectures': attendance.calculate_lectures_in_period(
                    datetime.strptime(request.form['skip_start'], '%Y-%m-%d').date(),
                    datetime.strptime(request.form['skip_end'], '%Y-%m-%d').date()
                )
            })
        
        results = attendance.main_web(**form_data)
        return render_template('results.html', results=results, visitor_count=visitor_count, creator_name="Your Name")
    
    return render_template('index.html', today=datetime.now().date(), visitor_count=visitor_count, creator_name="Your Name")

if __name__ == '__main__':
    app.run(debug=True)