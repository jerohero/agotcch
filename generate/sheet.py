import openpyxl
from openpyxl.styles import PatternFill

def export_to_excel(characters: dict, file_name: str):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Canon Children"

    headers = ["ID", "Name", "Birth", "Father", "Real Father", "Mother"]
    sheet.append(headers)

    fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

    for child_id, child in characters.items():
        if child["skipped"]:
            continue

        row = [
            child_id,
            child["name"]["primary"],
            child["birth"],
            child["father"],
            child["real_father"],
            child["mother"]
        ]
        sheet.append(row)

    for cell in sheet[1]:
        cell.fill = fill

    workbook.save(f"{file_name}.xlsx")
