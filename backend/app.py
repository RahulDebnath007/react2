from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
import logging

# Initialize the Flask application
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Configure MongoDB URI
client = MongoClient('mongodb://localhost:27017/')
db = client['learning_assistant_db']
user_progress_collection = db['user_progress']

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Mock study materials for AI recommendations
study_materials = {
    "Math": [
        "Algebra basics: Linear equations, Quadratic equations",
        "Trigonometry practice: Sine, Cosine, Tangent, and their identities",
        "Calculus videos: Derivatives, Integrals, Limits, and Applications",
        "Geometry: Area, Perimeter, Pythagorean theorem, and angles",
        "Probability and Statistics: Basic probability, Descriptive statistics, Hypothesis testing"
    ],
    "Science": [
        "Physics experiments: Motion, Energy, Forces, Newton's Laws, Optics",
        "Biology diagrams: Cell structure, Human anatomy, Photosynthesis",
        "Chemistry notes: Atomic structure, Chemical bonding, Organic chemistry",
        "Environmental Science: Ecosystems, Biodiversity, Pollution",
        "Astronomy: Solar system, Space exploration, Theories of the universe"
    ],
    "History": [
        "Ancient civilizations: Egypt, Mesopotamia, Indus Valley, Greece, Rome",
        "Modern history podcasts: Industrial Revolution, World Wars, Cold War",
        "World history: Renaissance, Enlightenment, Colonialism",
        "American history: Independence, Civil War, Civil Rights Movement",
        "Indian history: Mughal Empire, British Raj, Independence struggle"
    ],
    "English": [
        "Grammar exercises: Tenses, Articles, Pronouns, Prepositions",
        "Literature analysis: Shakespeare, Poetry, Short stories, Prose",
        "Vocabulary building: Word roots, Prefixes, Suffixes, Synonyms, Antonyms",
        "Writing skills: Essays, Letter writing, Creative writing",
        "Speaking skills: Public speaking, Pronunciation, Debates"
    ],
    "Computer Science": [
        "Algorithms: Sorting, Searching, Dynamic programming, Greedy algorithms",
        "Data Structures: Arrays, Linked lists, Trees, Graphs, Stacks, Queues",
        "Operating Systems: Processes, Memory management, File systems",
        "Databases: SQL, NoSQL, Database normalization, Query optimization",
        "Software Development: Version control, Testing, Agile methodology"
    ],
    "Economics": [
        "Microeconomics: Demand and supply, Market equilibrium, Elasticity",
        "Macroeconomics: National income, Unemployment, Inflation, GDP",
        "International Economics: Trade theory, Exchange rates, Globalization",
        "Development Economics: Poverty, Inequality, Economic growth",
        "Financial Economics: Investment analysis, Portfolio theory, Capital markets"
    ],
    "Geography": [
        "Physical geography: Landforms, Climate, Natural resources",
        "Human geography: Population distribution, Urbanization, Migration",
        "World geography: Countries, Capitals, Landmarks, Time zones",
        "Environmental Geography: Sustainable development, Natural hazards, Climate change",
        "Cartography: Map reading, Geospatial technology, GIS (Geographic Information Systems)"
    ],
    "Psychology": [
        "Cognitive Psychology: Memory, Perception, Problem solving, Learning",
        "Behavioral Psychology: Conditioning, Reinforcement, Punishment",
        "Developmental Psychology: Stages of life, Child development, Aging",
        "Social Psychology: Group behavior, Conformity, Social influence, Attitudes",
        "Clinical Psychology: Mental health disorders, Therapy, Diagnosis, Treatment"
    ],
    "Philosophy": [
        "Ethics: Moral theories, Rights and duties, Utilitarianism, Kantian ethics",
        "Logic: Deductive reasoning, Inductive reasoning, Fallacies",
        "Epistemology: Knowledge, Belief, Justification, Truth",
        "Metaphysics: Existence, Reality, Free will, Time, Space",
        "Political Philosophy: Democracy, Justice, Power, Liberty"
    ],
    "Art": [
        "Art history: Classical art, Renaissance, Modernism, Postmodernism",
        "Painting techniques: Watercolor, Oil painting, Acrylics, Digital art",
        "Sculpture: Materials, Techniques, Famous sculptors",
        "Photography: Composition, Lighting, Editing, Portrait photography",
        "Graphic Design: Adobe Illustrator, Photoshop, Logo design, Typography"
    ],
    "Music": [
        "Music theory: Notes, Scales, Chords, Harmony",
        "Instruments: Guitar, Piano, Violin, Drums, Flute",
        "Music history: Classical, Baroque, Jazz, Rock, Pop",
        "Composition: Songwriting, Arrangement, Orchestration",
        "Music production: Digital audio workstations (DAWs), Mixing, Mastering"
    ],
    "Languages": [
        "Spanish: Vocabulary, Grammar, Pronunciation, Common phrases",
        "French: Vocabulary, Grammar, Conversation, Cultural insights",
        "German: Vocabulary, Grammar, Reading comprehension, Pronunciation",
        "Mandarin: Vocabulary, Writing characters, Pronunciation, Pinyin",
        "English as a second language: Vocabulary, Grammar, Speaking, Listening"
    ],
    "Health & Fitness": [
        "Exercise routines: Cardio, Strength training, Yoga, Pilates",
        "Nutrition: Macronutrients, Micronutrients, Diet plans, Healthy eating",
        "Mental health: Stress management, Meditation, Mindfulness",
        "First aid: CPR, Emergency care, Wound care, Basic life support",
        "Wellness: Sleep hygiene, Hydration, Preventative healthcare"
    ]
}


@app.route('/api/recommend', methods=['POST'])
def recommend():
    """
    Endpoint to recommend study materials based on subjects and time.
    """
    data = request.json
    subjects = data.get('subjects', [])
    time = data.get('time', 0)

    if not subjects or time <= 0:
        return jsonify({"error": "Invalid input"}), 400

    recommendations = []
    for subject in subjects:
        materials = study_materials.get(subject, ["General resources"])
        # Allocate time equally among the subjects
        hours = round(time / len(subjects), 2)
        recommendations.append(f"Study {subject} for {hours} hours and check: {', '.join(materials)}")

    return jsonify({"recommendations": recommendations})

@app.route('/api/save-progress', methods=['POST'])
def save_progress():
    """
    Endpoint to save user progress into MongoDB.
    """
    data = request.json
    subject = data.get('subject')
    hours = data.get('hours')

    if not subject or hours is None:
        return jsonify({"error": "Invalid input"}), 400

    # Save the user's progress into MongoDB
    user_progress = {
        "subject": subject,
        "hours": hours
    }
    user_progress_collection.insert_one(user_progress)  # Insert into MongoDB collection

    return jsonify({"message": "Progress saved successfully!"})

@app.route('/api/get-progress', methods=['GET'])
def get_progress():
    """
    Endpoint to retrieve all saved progress from MongoDB.
    """
    progress = user_progress_collection.find()  # Get all records from the MongoDB collection
    progress_list = [{"subject": p["subject"], "hours": p["hours"]} for p in progress]
    return jsonify({"progress": progress_list})

@app.route('/api/update-study-time', methods=['POST'])
def update_study_time():
    """
    Endpoint to update the user's study time based on their preferences and past progress.
    """
    data = request.json
    subjects = data.get('subjects', [])
    total_time = data.get('time', 0)

    if not subjects or total_time <= 0:
        return jsonify({"error": "Invalid input"}), 400

    # Calculate time allocation based on progress and available time
    allocated_time = {}
    for subject in subjects:
        progress = user_progress_collection.find_one({"subject": subject})
        subject_time = progress['hours'] if progress else 0
        additional_time = round(total_time * 0.5)  # Add extra time based on previous progress
        allocated_time[subject] = subject_time + additional_time

    return jsonify({"allocated_time": allocated_time})

@app.route('/api/get-study-materials', methods=['GET'])
def get_study_materials():
    """
    Endpoint to get available study materials.
    """
    return jsonify({"study_materials": study_materials})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
