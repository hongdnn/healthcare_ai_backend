from openpyxl import Workbook

# Create workbook and sheet
wb = Workbook()
ws = wb.active
ws.title = "HealthCare Data"

# Add headers
ws.append(["id", "health_issue", "symptoms", "advice"])

# Add data rows
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

# Save file
wb.save("healthcare_data.xlsx")

print("✅ Excel file 'healthcare_data.xlsx' created successfully!")