from api.client import get_info
from log_utils.logger import log_event
from utils.validate_schema import validate_row
import logging
# url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheetID}/values/{sheetName}!A1:E9"
def get_sheet_data(sheetID,sheetName,token):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheetID}/values/{sheetName}"
    
    # token which we receive from OAuth
    headers = {
        "Authorization": f"Bearer {token}"
    }

    data = get_info("GET",url,headers=headers)
    try:
        if not data:
            return None
        data["values"][0][0] = "Full Name"
    except TypeError as e:
        log_event(logging.ERROR,"Type Error",error_type=type(e).__name__,error_message=str(e))
    except ValueError as e:
        log_event(logging.ERROR,"Value Error",error_type=type(e).__name__,error_message=str(e))

    data = to_lower(data)
    return data


def find_new_status(list_data):
    name_list = [[
            "Full Name",
            "Email",
            "Status",
            "Source",
            "Created_At"
        ]]
    try:
        for i in list_data["values"][1:]:
            if i[2].upper()=="NEW":
                name_list.append(i)
        return name_list
    except TypeError as e:
        log_event(logging.ERROR,"Type Error",error_type=type(e).__name__,error_message=str(e))
    except ValueError as e:
        log_event(logging.ERROR,"Value Error",error_type=type(e).__name__,error_message=str(e))
    return None

def to_lower(list_data):
    try:
        valid_rows = [list_data["values"][0]] # keep header
        for i in list_data["values"][1:]:
            if not validate_row(i):
                log_event(logging.WARNING, "Skipping invalid row", row=str(i))
                continue
            i[1] = i[1].lower()
            valid_rows.append(i)
        list_data["values"] = valid_rows
        return list_data
    except TypeError as e:
        log_event(logging.ERROR,"Type Error",error_type=type(e).__name__,error_message=str(e))
    except ValueError as e:
        log_event(logging.ERROR,"Value Error",error_type=type(e).__name__,error_message=str(e))
    return None

# loop from 1st index
# if validat_row() == False i.e. Invalid rows (missing fields or bad emails) are skipped with a log warning
# if True -> rows get their email lowercased
# rows append to valid_rows and copied the complete list back to list_data["values"]