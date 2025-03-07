from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def is_safe_state(available, allocation, max_matrix, num_processes, num_resources):
    work = available[:]
    finish = [False] * num_processes
    safe_sequence = []

    while len(safe_sequence) < num_processes:
        progress_made = False
        for i in range(num_processes):
            if not finish[i]:
                need = [max_matrix[i][j] - allocation[i][j] for j in range(num_resources)]
                
                if all(need[j] <= work[j] for j in range(num_resources)):
                    for j in range(num_resources):
                        work[j] += allocation[i][j]
                    finish[i] = True
                    safe_sequence.append(i)
                    progress_made = True
                    break
        
        if not progress_made:
            return False, []
    
    return True, safe_sequence

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_deadlock', methods=['POST'])
def check_deadlock():
    try:
        data = request.get_json()

        num_processes = int(data['num_processes'])
        num_resources = int(data['num_resources'])
        available = list(map(int, data['available']))
        allocation = [list(map(int, row)) for row in data['allocation']]
        max_matrix = [list(map(int, row)) for row in data['max_matrix']]

        is_safe, safe_sequence = is_safe_state(available, allocation, max_matrix, num_processes, num_resources)

        return jsonify({
            'result': 'Safe State' if is_safe else 'Deadlock Detected',
            'safe_sequence': safe_sequence if is_safe else []
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
