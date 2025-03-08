from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_safe_state(available, allocation, max_matrix, num_processes, num_resources):
    work = np.array(available)
    finish = [False] * num_processes
    safe_sequence = []

    while len(safe_sequence) < num_processes:
        progress_made = False
        for i in range(num_processes):
            if not finish[i]:
                need = np.array(max_matrix[i]) - np.array(allocation[i])
                if np.all(need <= work):
                    work += allocation[i]
                    finish[i] = True
                    safe_sequence.append(i)
                    progress_made = True
                    break
        if not progress_made:
            logging.warning("Deadlock detected. System is not in a safe state.")
            return False, []
    
    logging.info(f"Safe sequence found: {safe_sequence}")
    return True, safe_sequence

@app.route('/check_deadlock', methods=['POST'])
def check_deadlock():
    try:
        data = request.get_json()

        # 🚨 Debugging: Print received JSON data
        logging.info(f"Received JSON: {data}")

        if data is None:
            return jsonify({'error': 'Invalid JSON or empty request'}), 400

        num_processes = int(data.get('num_processes', 0))
        num_resources = int(data.get('num_resources', 0))
        available = list(map(int, data.get('available', [])))
        allocation = [list(map(int, row)) for row in data.get('allocation', [])]
        max_matrix = [list(map(int, row)) for row in data.get('max_matrix', [])]

        # 🚨 Debugging: Print parsed values
        logging.info(f"Parsed Values - Processes: {num_processes}, Resources: {num_resources}")
        logging.info(f"Available: {available}")
        logging.info(f"Allocation: {allocation}")
        logging.info(f"Max Matrix: {max_matrix}")

        if num_processes <= 0 or num_resources <= 0:
            return jsonify({'error': 'Invalid number of processes or resources'}), 400
        
        if len(available) != num_resources:
            return jsonify({'error': 'Available resources size mismatch'}), 400
        
        if not all(len(row) == num_resources for row in allocation):
            return jsonify({'error': 'Allocation matrix dimensions do not match the number of resources'}), 400
        
        if not all(len(row) == num_resources for row in max_matrix):
            return jsonify({'error': 'Max matrix dimensions do not match the number of resources'}), 400

        is_safe, safe_sequence = is_safe_state(available, allocation, max_matrix, num_processes, num_resources)
        
        return jsonify({
            'result': 'Safe State' if is_safe else 'Deadlock Detected',
            'safe_sequence': safe_sequence if is_safe else []
        })
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
