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

# Save file
wb.save("healthcare_data.xlsx")

print("✅ Excel file 'healthcare_data.xlsx' created successfully!")