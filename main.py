import math
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

class Target:
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity

def euclidean_distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def is_moving_towards(target_pos, target_vel, key_point):
    dir_to_key = (key_point[0] - target_pos[0], key_point[1] - target_pos[1])
    dot_product = dir_to_key[0] * target_vel[0] + dir_to_key[1] * target_vel[1]
    return dot_product > 0

def calculate_priority(target, key_points, weight_distance=1.0, weight_threat=100.0):
    distance_score = euclidean_distance((0, 0), target.position)
    threat_score = 0
    for kp in key_points:
        if is_moving_towards(target.position, target.velocity, kp):
            threat_score += 1 / (euclidean_distance(target.position, kp) + 1e-5)
    return weight_distance * distance_score - weight_threat * threat_score

@app.route('/get_target', methods=["POST"])
def index():
    data = request.get_json()
    weight_distance = data.get("weight_distance", 1.0)
    weight_threat = data.get("weight_threat", 100.0)

    scores = []
    best_score = float('inf')
    best_target_index = None

    for idx, target_data in enumerate(data.get("targets", [])):
        position = target_data[0]
        velocity = target_data[1]
        target = Target(position, velocity)
        score = calculate_priority(target, data.get("key_points", []), weight_distance, weight_threat)
        scores.append(score)

        if score < best_score:
            best_score = score
            best_target_index = idx

    return jsonify({
        "best_target_index": best_target_index,
        "scores": scores
    })

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)