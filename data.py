import pandas as pd
import os
import time
from constants import DATA_FILE

# Google Sheets integration
import gspread
from oauth2client.service_account import ServiceAccountCredentials

GOOGLE_SHEET_FILE = 'my_experiment_data'  # Name of the Google Sheets file
RESULTS_SHEET = 'Results'
QUESTIONNAIRES_SHEET = 'Questionnaires'

QUESTIONNAIRE_HEADER = [
    'participant_id', 'phase',
    'reason', 'pattern', 'stress', 'confidence', 'perceived_control', 'strategy',
    'avoided', 'motive', 'risk', 'mechanism'
]

def get_gsheet_worksheet(sheet_name):
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name('google_creds.json', scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open(GOOGLE_SHEET_FILE)
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="30")
    return worksheet

def save_rows_to_gsheet_worksheet(sheet_name, rows, header=None):
    try:
        worksheet = get_gsheet_worksheet(sheet_name)
        if header:
            all_values = worksheet.get_all_values()
            # Only insert header if the worksheet is empty
            if not all_values:
                worksheet.insert_row(header, 1)
        worksheet.append_rows(rows)
    except Exception as e:
        print(f'Google Sheets error: {e}')

# Test function for Google Sheets integration
def test_gsheet():
    try:
        save_rows_to_gsheet_worksheet(RESULTS_SHEET, [[
            'test_id', 'test_phase', 'test_round', 'test_box', 'test_time', 'test_result', 'test_reward', 'test_earnings', 'test_p_safe', 'test_p_uncertain', 'test_init_p_safe', 'test_init_p_uncertain'
        ]], header=[
            'participant_id', 'phase', 'round', 'box_chosen', 'decision_time',
            'result', 'reward', 'cumulative_earnings', 'p_safe', 'p_uncertain',
            'init_p_safe', 'init_p_uncertain'
        ])
        save_rows_to_gsheet_worksheet(QUESTIONNAIRES_SHEET, [[
            'test_id', 'test_phase', '', '', '', '', '', '', '', '', '', ''
        ]], header=QUESTIONNAIRE_HEADER)
        print('Google Sheets test rows appended successfully.')
    except Exception as e:
        print(f'Google Sheets integration failed: {e}')

# Save all phase results to a single CSV file for all participants
def save_round_data(data, participant_id, initial_probs=None, seeds=None):
    if not data or not participant_id:
        raise ValueError("No data or participant ID provided for saving.")
    filename = 'experiment_data_all.csv'
    # Get initial probabilities for the phase (if provided)
    if initial_probs is not None and isinstance(initial_probs, dict):
        phase = data[0][1] if data and len(data[0]) > 1 else None
        init_p_safe = initial_probs.get(phase, {}).get('p_safe', None)
        init_p_uncertain = initial_probs.get(phase, {}).get('p_uncertain', None)
    else:
        init_p_safe = None
        init_p_uncertain = None
    # Add initial probs to each row
    data_with_init = [row + [init_p_safe, init_p_uncertain] for row in data]
    df = pd.DataFrame(data_with_init, columns=[
        'participant_id', 'phase', 'round', 'box_chosen', 'decision_time',
        'result', 'reward', 'cumulative_earnings', 'p_safe', 'p_uncertain',
        'init_p_safe', 'init_p_uncertain'
    ])
    file_exists = os.path.isfile(filename)
    write_header = not file_exists or os.stat(filename).st_size == 0
    df.to_csv(filename, mode='a', header=write_header, index=False)
    # Send all rows at once to Google Sheets (batch)
    try:
        save_rows_to_gsheet_worksheet(RESULTS_SHEET, data_with_init, header=list(df.columns))
    except Exception as e:
        print(f'Google Sheets error: {e}')

def get_unique_filename(base, participant_id):
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    return f"{base}_pid{participant_id}_{timestamp}.csv"

def save_questionnaire(participant_id, phase, responses):
    if not participant_id or not phase or not responses:
        raise ValueError("Missing participant ID, phase, or responses for questionnaire.")
    filename = 'questionnaire_data_all.csv'
    # Fill all possible columns, missing values as blank
    row_dict = {col: '' for col in QUESTIONNAIRE_HEADER}
    row_dict['participant_id'] = participant_id
    row_dict['phase'] = phase
    for k, v in responses.items():
        row_dict[k] = v
    df = pd.DataFrame([row_dict], columns=QUESTIONNAIRE_HEADER)
    file_exists = os.path.isfile(filename)
    write_header = not file_exists or os.stat(filename).st_size == 0
    df.to_csv(filename, mode='a', header=write_header, index=False)
    # Send to Google Sheets (batch, but usually one row)
    try:
        save_rows_to_gsheet_worksheet(QUESTIONNAIRES_SHEET, [list(row_dict.values())], header=QUESTIONNAIRE_HEADER)
    except Exception as e:
        print(f'Google Sheets error: {e}')
