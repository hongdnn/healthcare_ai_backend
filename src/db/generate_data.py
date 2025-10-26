from datetime import datetime, timedelta, time
from dotenv import load_dotenv
from pymongo import MongoClient
from faker import Faker
import random
import os

load_dotenv(".env.local")

# Conenct to database
mongodb_client = MongoClient(os.environ["MONGODB_URL"])
db = mongodb_client.healthcare_db

# Collections
users = db.users
calendars = db.calendars
conversations = db.conversations

# Generate fake data
fake = Faker('en_US')
Faker.seed(round(random.randint(0, 100000)))

# Health Issues
ws = []
ws.append([0, "Flu", "headache, cold", "take rest, drink more water"])
ws.append([1, "Covid", "fever, cough, tired", "isolate, drink water"])
ws.append([2, "Allergy", "sneeze, itchy eyes", "take antihistamines, avoid allergens"])
ws.append([3, "Migraine", "headache, nausea, light sensitivity", "rest in dark room, pain relief medication"])
ws.append([4, "Stomach Infection", "nausea, vomiting, diarrhea, abdominal pain", "stay hydrated, eat light meals"])
ws.append([5, "Bronchitis", "cough, chest pain, fatigue, shortness of breath", "rest, drink fluids, avoid smoke"])
ws.append([6, "Sinusitis", "headache, nasal congestion, facial pain, runny nose", "steam inhalation, decongestants"])
ws.append([7, "Food Poisoning", "nausea, vomiting, diarrhea, fever", "stay hydrated, eat bland foods"])
ws.append([8, "Cold", "runny nose, cough, sore throat, fatigue", "rest, fluids, over-the-counter cold remedies"])
ws.append([9, "Chickenpox", "rash, fever, fatigue, itchy skin", "isolate, calamine lotion"])
ws.append([10, "Dengue", "fever, headache, joint pain, rash", "stay hydrated, rest"])
ws.append([11, "Pneumonia", "fever, cough, fatigue, shortness of breath", "rest, fluids"])
ws.append([12, "Viral Infection", "fever, cough, fatigue, headache", "rest, fluids, monitor symptoms"])
ws.append([13, "Sinus Infection", "headache, facial pain, fatigue, mild fever", "rest, fluids, nasal irrigation"])
ws.append([14, "Influenza B", "fever, cough, fatigue, muscle aches", "rest, fluids, take medication if early"])
ws.append([15, "Tension Headache", "dull head pain, tight neck, pressure around forehead", "rest, gentle stretching, warm compress, stay hydrated"])
ws.append([16, "Back Strain", "lower back pain, muscle tightness, stiffness", "gentle stretching, avoid heavy lifting, warm compress, short walks"])
ws.append([17, "Dehydration", "dry mouth, dizziness, tiredness", "sip fluids gradually, add electrolytes, avoid caffeine, rest"])
ws.append([18, "Constipation", "hard stools, bloating, stomach discomfort", "increase fiber, drink water, light exercise, warm tea"])
ws.append([19, "Eczema", "dry skin, redness, itching", "apply moisturizer, avoid harsh soaps, cool compress, breathable fabrics"])
ws.append([20, "Acid Reflux", "chest burning, bitter taste, throat irritation", "smaller meals, avoid lying down after eating, limit spicy foods, sip water"])
ws.append([21, "Lactose Intolerance", "bloating, gas, stomach discomfort", "choose lactose-free products, track trigger foods, enzyme supplements, smaller portions"])
ws.append([22, "Plantar Fasciitis", "heel pain, stiffness, pain worse in morning", "arch stretches, supportive shoes, cold pack, avoid prolonged standing"])
ws.append([23, "Carpal Tunnel", "wrist tingling, hand numbness, grip weakness", "wrist rest, ergonomic posture, finger stretches, avoid strain"])
ws.append([24, "Mild Anxiety", "restlessness, racing thoughts, trouble sleeping", "deep breathing, journaling, calming music, light exercise"])
ws.append([25, "Dry Eyes", "redness, gritty feeling, mild irritation", "use artificial tears, blink breaks, avoid dry air, reduce screen time"])
ws.append([26, "Indigestion", "bloating, fullness, stomach discomfort", "eat slowly, avoid greasy foods, warm herbal tea, light movement"])
ws.append([27, "Irritable Bowel", "cramping, bloating, irregular bowel movements", "avoid trigger foods, increase fiber gradually, warm compress, relax and rest"])
ws.append([28, "Neck Strain", "neck stiffness, shoulder tension, limited movement", "gentle stretches, warm shower, avoid poor posture, slow movement"])
ws.append([29, "Ear Congestion", "ear pressure, muffled sound, mild discomfort", "yawn/swallow often, warm compress, stay upright, avoid loud sounds"])
ws.append([30, "Dry Throat", "scratchy throat, dryness, irritation", "sip warm liquids, use humidifier, avoid overly cold drinks, rest voice"])
ws.append([31, "Gas Pain", "bloating, stomach cramping, pressure", "gentle walking, warm tea, avoid carbonated drinks, light meals"])
ws.append([32, "Eye Strain", "tired eyes, slight headache, blurred focus", "20-20-20 screen break rule, blink often, adjust brightness, relax eyes"])
ws.append([33, "Muscle Soreness", "tender muscles, stiffness, mild weakness", "light stretching, warm bath, stay hydrated, avoid sudden strain"])
ws.append([34, "Shin Splints", "shin pain, tenderness, discomfort while walking", "rest legs, ice pack, supportive footwear, gradual activity return"])
ws.append([35, "Mild Heartburn", "burning chest sensation, throat irritation, sour taste", "avoid large meals, eat slowly, avoid acidic foods, stay upright"])
ws.append([36, "Allergic Rhinitis", "sneeze, runny nose, itchy nose", "avoid allergens, saline rinse, keep windows closed, use air filter"])
ws.append([37, "Scalp Irritation", "itchy scalp, dryness, flaking", "use mild shampoo, avoid hot water, moisturize scalp, avoid scratching"])
ws.append([38, "Jaw Tension", "jaw tightness, clicking, facial discomfort", "jaw relaxation exercises, soft foods, warm compress, avoid clenching"])
ws.append([39, "Shoulder Strain", "shoulder stiffness, soreness, reduced range of motion", "light stretching, warm compress, avoid heavy bags, slow arm circles"])
ws.append([40, "Hip Tightness", "stiff hips, discomfort when sitting, limited mobility", "hip stretches, short walks, avoid prolonged sitting, light mobility work"])
ws.append([41, "Mouth Ulcers", "small sore, tenderness, discomfort when eating", "avoid spicy foods, rinse with salt water, stay hydrated, eat soft foods"])
ws.append([42, "Cold Sores", "tingling around lips, small blisters, mild pain", "apply lip balm, avoid picking, cold compress, stay hydrated"])
ws.append([43, "Dry Skin", "rough patches, flakiness, mild itching", "use moisturizer, avoid hot showers, drink water, wear soft fabrics"])
ws.append([44, "Chapped Lips", "dry lips, cracking, stinging sensation", "use lip balm, avoid licking lips, drink water, protect from wind"])
ws.append([45, "Mild Nausea", "queasy feeling, stomach unease, loss of appetite", "sip clear liquids, avoid heavy foods, fresh air, small snacks"])
ws.append([46, "Mild Dizziness", "lightheadedness, unsteady feeling, tiredness", "sit down, drink water, slow breathing, avoid sudden movements"])
ws.append([47, "Sinus Pressure", "facial pressure, nasal stuffiness, dull headache", "steam inhalation, warm compress, stay hydrated, rest"])
ws.append([48, "Dry Nose", "nasal dryness, slight irritation, discomfort", "saline spray, humidifier, drink water, avoid very dry air"])
ws.append([49, "Mild Tooth Sensitivity", "sensitivity to cold foods, gum tenderness, slight ache", "use sensitivity toothpaste, avoid cold items, gentle brushing, rinse with warm water"])
ws.append([50, "Inner Thigh Chafing", "skin redness, soreness, irritation", "apply moisturizer, wear breathable fabrics, avoid friction, keep area dry"])
ws.append([51, "Mild Insomnia", "difficulty falling asleep, restless mind, tossing and turning", "set sleep schedule, avoid screens before bed, calming breathing, dim lights"])
ws.append([52, "Overthinking", "mental fatigue, racing thoughts, tension", "deep breathing, write thoughts out, take a walk, calming music"])
ws.append([53, "Mild Jet Lag", "sleep disruption, tiredness, low focus", "expose to daylight, stay hydrated, short naps, adjust sleep time gradually"])
ws.append([54, "Sore Feet", "tender soles, tingling, discomfort after standing", "foot stretches, supportive shoes, elevate feet, warm soak"])
ws.append([55, "Mild Wrist Sprain", "wrist soreness, mild swelling, reduced strength", "rest wrist, gentle movement, cold pack, avoid strain"])
ws.append([56, "Finger Joint Irritation", "stiff fingers, small aches, reduced grip", "warm soak, gentle finger stretches, avoid overuse, light hand exercise"])
ws.append([57, "Skin Irritation", "redness, mild itching, surface discomfort", "avoid irritants, rinse with cool water, apply gentle lotion, keep area dry"])
ws.append([58, "Low Appetite", "reduced hunger, low interest in food, mild fatigue", "eat small meals, try warm soups, choose easy-to-digest foods, relax before meals"])
ws.append([59, "Hiccup Episode", "repetitive hiccups, chest spasms, brief discomfort", "slow breathing, sip water, swallow slowly, relax body"])
ws.append([60, "Throat Dryness", "scratchy feeling, dryness, rough speech", "sip warm tea, use humidifier, rest voice, avoid dry environments"])
ws.append([61, "Skin Sensitivity", "mild burning sensation, surface tenderness, discomfort when touched", "avoid friction, use soft fabrics, apply moisturizer, keep area cool"])
ws.append([62, "Mild Nerve Tingling", "pins and needles, slight numbness, light buzzing sensation", "change sitting position, stretch area, gentle movement, avoid pressure"])
ws.append([63, "Stiff Elbow", "joint tightness, reduced range, mild soreness", "slow stretching, warm compress, avoid repetitive motion, light movement"])
ws.append([64, "Hamstring Tightness", "back of leg stiffness, reduced flexibility, pulling sensation", "gentle stretching, warm up before activity, avoid sudden strain, light massage"])
ws.append([65, "Knee Discomfort", "mild ache, stiffness, pressure when bending", "avoid deep bends, slow stretching, supportive shoes, short walks"])
ws.append([66, "Mild Dehydrated Skin", "tight skin, flakiness, dullness", "apply moisturizer, drink water, avoid very hot showers, use gentle cleansers"])
ws.append([67, "Light Sensitivity", "discomfort in bright light, eye strain, mild headache", "wear sunglasses, reduce screen brightness, rest eyes, avoid glare"])
ws.append([68, "Nasal Dryness", "dry passages, slight burning, crusting", "saline spray, humidifier, sip water, avoid dry wind"])
ws.append([69, "Mild Bloating", "fullness, stomach pressure, discomfort", "peppermint tea, gentle walk, avoid carbonated drinks, chew slowly"])
ws.append([70, "Sore Jaw", "jaw fatigue, dull ache, difficulty chewing", "soft foods, jaw rest, warm compress, gentle stretching"])
ws.append([71, "Chronic Sitting Fatigue", "lower back discomfort, hip tightness, sluggishness", "stand and stretch regularly, short walks, adjust chair height, keep posture neutral"])
ws.append([72, "Low Hydration Skin", "dull complexion, tight feeling, uneven texture", "apply hydrating moisturizer, increase water intake, avoid hot showers, use humidifier"])
ws.append([73, "Brittle Nails", "nail splitting, dryness, weak texture", "apply cuticle oil, avoid harsh cleaners, keep nails trimmed, increase hydration"])
ws.append([74, "Static Hair", "flyaway hair, dryness, frizz", "use conditioner, avoid over-brushing, humidify room, gentle combing"])
ws.append([75, "Scalp Dryness", "flaking, tightness, mild itch", "use moisturizing shampoo, avoid very hot showers, massage scalp gently, stay hydrated"])
ws.append([76, "Shoulder Blade Tightness", "tension between shoulder blades, stiffness, mild discomfort", "gentle stretching, correct posture, warm compress, slow deep breaths"])
ws.append([77, "Mild Sinus Dryness", "dry nasal passages, mild pressure, slight irritation", "steam inhalation, humidifier, sip warm liquids, avoid dry air"])
ws.append([78, "Keyboard Strain", "finger tension, wrist tightness, forearm fatigue", "ergonomic typing posture, wrist breaks, stretch hands, relax shoulders"])
ws.append([79, "Heavy Eyes from Screens", "eyelid heaviness, eye strain, low focus", "screen breaks, blink often, adjust lighting, hydrate body"])
ws.append([80, "Morning Grogginess", "sluggish waking, low energy, slow thinking", "gradually adjust sleep schedule, morning sunlight, water on waking, gentle stretching"])
ws.append([81, "Mild Motion Sickness", "nausea, dizziness, head discomfort", "fresh airflow, focus on horizon, sip water, avoid heavy meals"])
ws.append([82, "Post-Workout Fatigue", "low energy, muscle tiredness, mild soreness", "replenish fluids, light stretching, small nutritious snack, rest"])
ws.append([83, "Mild Sugar Crash", "tiredness, irritability, low energy", "eat balanced snack, drink water, steady breathing, avoid sugary foods"])
ws.append([84, "Screen Overuse Fatigue", "eye strain, tension headache, mental fog", "take screen breaks, reduce brightness, stretch neck, look at distant objects"])
ws.append([85, "Crowded-Space Overstimulation", "head tension, restlessness, difficulty focusing", "step into fresh air, deep breathing, calming music, quiet environment"])
ws.append([86, "Mild Chest Muscle Strain", "localized chest soreness, pain when moving, mild tightness", "rest chest muscles, warm compress, slow deep breathing, avoid heavy lifting"])
ws.append([87, "Ankle Soreness", "joint tightness, light swelling, discomfort walking", "rest ankle, elevate foot, supportive footwear, gentle ankle rotations"])
ws.append([88, "Thigh Muscle Fatigue", "tired legs, heaviness, tightness", "light stretching, hydrate, avoid sudden exertion, warm shower"])
ws.append([89, "Head Pressure from Stress", "tight forehead, temples pressure, mental fatigue", "slow breathing, dim lights, gentle neck stretch, drink water"])
ws.append([90, "Skin Drying from Weather", "tight skin, roughness, flaking", "use moisturizer, avoid harsh wind, drink water, use gentle soap"])
ws.append([91, "Windburned Skin", "redness, tenderness, dryness", "apply soothing lotion, avoid further wind, cool compress, keep skin covered"])
ws.append([92, "Mild Hunger Headache", "dull headache, low energy, light irritability", "eat small snack, drink water, rest briefly, avoid skipping meals"])
ws.append([93, "Mild Dehydration Fatigue", "low energy, dry lips, sluggishness", "sip fluids steadily, include electrolytes, avoid excessive caffeine, rest"])
ws.append([94, "Heat Exposure Fatigue", "tiredness, dry mouth, light dizziness", "move to shade, sip water, cool body slowly, loosen clothing"])
ws.append([95, "Cold Air Throat Irritation", "dry throat, scratchiness, mild hoarseness", "sip warm water, use scarf, humidify air, rest voice"])
ws.append([96, "Arm Muscle Tightness", "stiff arms, muscle tension, reduced flexibility", "gentle stretching, warm shower, stay hydrated, avoid sudden strain"])
ws.append([97, "Calf Tightness", "tight calves, pulling sensation, discomfort during walking", "calf stretches, gradual movement, warm compress, avoid long standing"])
ws.append([98, "Abdominal Tightness", "stomach muscle tenderness, stiffness, discomfort when bending", "light stretching, warm compress, slow breathing, avoid heavy meals"])
ws.append([99, "Mild Overwork Fatigue", "mental tiredness, slow focus, low motivation", "short break, light snack, drink water, gentle movement"])

from datetime import datetime, timedelta, time
import random

def generate_weekday_appointment(
    working_start=time(9, 0),
    working_end=time(17, 0),
    duration_minutes=60
):
    # Hardcoded date range (inclusive)
    start_date = datetime(2025, 10, 22)
    end_date = datetime(2025, 10, 25)

    delta_days = (end_date - start_date).days
    random_day = start_date + timedelta(days=random.randint(0, delta_days))

    # Random hour within working window
    start_hour = random.randint(working_start.hour, working_end.hour - 1)

    start_dt = datetime(
        random_day.year,
        random_day.month,
        random_day.day,
        start_hour,
        0
    )

    end_dt = start_dt + timedelta(minutes=duration_minutes)

    return {
        "start_datetime": start_dt,
        "end_datetime": end_dt,
        "confirmation": "confirmed",
        "created_at": datetime.now()
    }

    
def get_random_health_issue():
    entry = random.choice(ws)

    issue = entry[1]
    symptoms = [s.strip() for s in entry[2].split(",")]
    recommendations = [r.strip() for r in entry[3].split(",")]

    return {
        "issue": issue,
        "symptoms": symptoms,
        "recommendations": recommendations
    }


def generate_user():
    user = {
        "name": fake.name(),
        "email": fake.email(),
        "phone": fake.numerify("+1##########"),
        "type": "patient"
    }
    user = users.insert_one(user)
    return user

from datetime import datetime

def generate_calendar(user_id: str, health: dict, time: dict):
    # Determine status based on whether appointment has already ended
    status = "completed" if time["end_datetime"] < datetime.now() else "confirmed"

    calendar = {
        "user_id": str(user_id),
        "doctor_id": "68fc65ca4916df00cfe6ec9d",
        "issue": f"Appointment regarding {health['issue']}",
        "start_datetime": time["start_datetime"],
        "end_datetime": time["end_datetime"],
        "confirmation": status,   # <---- status applied here
        "created_at": time["created_at"]
    }

    result = calendars.insert_one(calendar)
    return result



def generate_conversation(user_id: str, health: dict, time: dict, calendar: dict):
    conversation = {
        "user_id": str(user_id),
        "issue": health["issue"],
        "symptoms": health["symptoms"],
        "recommendations" : health["recommendations"],
        "appointment_id": str(calendar.inserted_id),
        "created_at": datetime.now()
    }
    conversation = conversations.insert_one(conversation)
    return conversation

def main():
    for _ in range(1):
        health_issue = get_random_health_issue()
        print(health_issue)

        time = generate_weekday_appointment()
        print(time)

        # user = generate_user()
        user = {
            "inserted_id": "68fdf8c6b830ab32db40416f"
        }
        print(user["inserted_id"])

        calendar = generate_calendar(user["inserted_id"], health=health_issue, time=time)
        print(calendar)

        conversation = generate_conversation(user["inserted_id"], health=health_issue, time=time, calendar=calendar)
        print(conversation)




if __name__ == "__main__":
    main()