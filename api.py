import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Replace with your spreadsheet ID
spreadsheet_id = "" # this is left blank for obvious security reasons

# Define the scopes for Google Sheets API
scopes = ["https://www.googleapis.com/auth/spreadsheets"]

def update_sheet(col, row, value, sheet_name):  # This function updates values on a sheet
    credentials = None
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", scopes)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
            except Exception as e:
                os.remove("token.json")
                return update_sheet(col, row, value, sheet_name)
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes)
            credentials = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(credentials.to_json())

    try:
        service = build("sheets", "v4", credentials=credentials)

        value_range_body = {
            "values": [
                [value]
            ]
        }

        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!{col}{row}",
            valueInputOption="USER_ENTERED",
            body=value_range_body
        ).execute()

        print("Cell updated successfully.")

    except HttpError as error:
        print(f"An error occurred: {error}")

def create_sheet(sheet_name): #This function creats a new sheet given a new name for the new sheet
    credentials = None
    # Check if token.json file exists to load credentials
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", scopes)

    # If credentials are not valid or don't exist, initiate OAuth flow
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
            except Exception as e:
                # Token is expired or revoked, delete the token file
                os.remove("token.json")
                return create_sheet(sheet_name)
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes)
            credentials = flow.run_local_server(port=0)
            # Save the credentials to token.json for next run
            with open("token.json", "w") as token:
                token.write(credentials.to_json())

    try:
        # Build the service object for interacting with Sheets API
        service = build("sheets", "v4", credentials=credentials)

        batch_update_request_body = {
            'requests': [
                {
                    'addSheet': {
                        'properties': {
                            'title': sheet_name,
                            'gridProperties': {
                                'rowCount': 100,
                                'columnCount': 26
                            }
                        }
                    }
                }
            ]
        }

        response = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=batch_update_request_body
        ).execute()

        print(f"Sheet '{sheet_name}' created successfully.")
        # Return the sheetId of the newly created sheet
        return response['replies'][0]['addSheet']['properties']['sheetId']
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def get_cell_value(sheet_name, range_name): #finds the value at a certain cell
    credentials = None
    # Check if token.json file exists to load credentials
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", scopes)

    # If credentials are not valid or don't exist, initiate OAuth flow
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
            except Exception as e:
                # Token is expired or revoked, delete the token file
                os.remove("token.json")
                return get_cell_value(sheet_name, range_name)
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes)
            credentials = flow.run_local_server(port=0)
            # Save the credentials to token.json for next run
            with open("token.json", "w") as token:
                token.write(credentials.to_json())

    try:
        # Build the service object for interacting with Sheets API
        service = build("sheets", "v4", credentials=credentials)

        # Construct the full range including the sheet name
        full_range_name = f"{sheet_name}!{range_name}"

        # Make API request to get values
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=full_range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print(f'No data found in range {full_range_name}.')
            return None
        else:
            # Assuming we are getting the first cell value
            return values[0][0]

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def find_row(sheet_name):
    count = 2
    while get_cell_value(sheet_name,f"A{count}") != None:
        count= count+1
    return count

