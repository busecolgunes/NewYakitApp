import streamlit as st
import pandas as pd
from pathlib import Path

# Add a title to the app
st.title('OMAS ARAÇ YAKIT TAKİP SİSTEMİ')

# Define the file paths for global fuel data
current_dir = Path.cwd()
GLOBAL_FILE = current_dir / 'global_fuel_data.xlsx'
GLOBAL_REMAINING_FUEL_FILE = current_dir / 'global_remaining_fuel.xlsx'

# Load or initialize the global fuel data
def load_or_initialize_excel(file_path, default_value):
    if file_path.exists():
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            if 'global_remaining_fuel' not in df.columns:
                st.error(f"Error: 'global_remaining_fuel' column is missing in {file_path.name}.")
                return pd.DataFrame({'global_remaining_fuel': [default_value]})
            return df
        except Exception as e:
            st.error(f"Error reading {file_path.name}: {e}. Recreating the file.")
            return pd.DataFrame({'global_remaining_fuel': [default_value]})
    else:
        df = pd.DataFrame({'global_remaining_fuel': [default_value]})
        df.to_excel(file_path, index=False)
        return df

global_fuel_df = load_or_initialize_excel(GLOBAL_FILE, 0)
global_remaining_fuel_df = load_or_initialize_excel(GLOBAL_REMAINING_FUEL_FILE, 0)

# Get the current global remaining fuel value
global_remaining_fuel = global_remaining_fuel_df['global_remaining_fuel'].iloc[0]

# Create a number input for the global "Kalan Mazot"
kalanmazot = st.number_input('Kalan Mazot (Mevcut):', value=float(global_remaining_fuel))

# Input for "Diğer Verilen Mazot"
digerverilen = st.number_input('Diğer Verilen Mazot:', min_value=0)

# Calculate the updated global remaining fuel
updated_global_remaining_fuel = kalanmazot - digerverilen

# Button to update the global remaining fuel value
if st.button('Kalan Mazot Güncelle'):
    # Update global remaining fuel value
    global_remaining_fuel_df['global_remaining_fuel'].iloc[0] = updated_global_remaining_fuel
    global_remaining_fuel_df.to_excel(GLOBAL_REMAINING_FUEL_FILE, index=False)

    # Update the relevant file for the selected vehicle plate
    if EXCEL_FILE.exists():
        try:
            vehicle_df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
            vehicle_df['kalanmazot'].iloc[0] = kalanmazot  # Update kalanmazot
            vehicle_df['digerverilen'].iloc[0] = digerverilen  # Update digerverilen

            # Save updated DataFrame back to the Excel file
            vehicle_df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
            st.success('Kalan mazot güncellendi ve dosyaya kaydedildi!')
        except Exception as e:
            st.error(f"Error updating {selected_file_name}: {e}.")
    else:
        st.error(f"{selected_file_name} does not exist. Please check the file.")

# Display the updated kalan mazot value
st.write('Güncellenmiş Kalan Mazot:', updated_global_remaining_fuel)

# Continue with the rest of your existing code...
# Define the dictionary for vehicle plates and their corresponding Excel files
files_dict = {
    '06BFD673': '06BFD673.xlsx',
    '01ACB022': '01ACB022.xlsx',
    '01AEE72': '01AEE72.xlsx',
    '01CIN12': '01CIN12.xlsx',
    '01GA546': '01GA546.xlsx',
    '01US433': '01US433.xlsx',
    '01ZD116': '01ZD116.xlsx',
    'FORKLIFT': 'FORKLIFT.xlsx',
    '34BAG417': '34BAG417.xlsx',
    '34BIT882': '34BIT882.xlsx',
    '01BOK56': '01BOK56.xlsx',
    '01SH480': '01SH480.xlsx',
    '01ACJ962': '01ACJ962.xlsx',
    'JENERATOR': 'JENERATOR.xlsx'
}

# Allow the user to select which vehicle plate to work with
selected_file_key = st.selectbox('Bir plaka seçiniz:', list(files_dict.keys()))
selected_file_name = files_dict[selected_file_key]

# Define the file path for the selected Excel file
EXCEL_FILE = current_dir / selected_file_name

# Load the data from the file if it exists, otherwise create an empty DataFrame
expected_columns = ['tarih', 'baslangickm', 'mazot', 'katedilenyol', 
                    'toplamyol', 'toplammazot', 'ortalama100', 
                    'kumulatif100', 'depomazot', 'depoyaalinanmazot', 
                    'depodakalanmazot', 'kalanmazot', 'digerverilen']

if EXCEL_FILE.exists():
    try:
        df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
        # Ensure all expected columns are present
        for col in expected_columns:
            if col not in df.columns:
                st.warning(f"Warning: Column '{col}' is missing in {selected_file_name}.")
                df[col] = None  # Add the missing columns with None values
    except Exception as e:
        st.error(f"Error reading {EXCEL_FILE.name}: {e}. Creating a new DataFrame.")
        df = pd.DataFrame(columns=expected_columns)
else:
    df = pd.DataFrame(columns=expected_columns)

# Display the data from the Excel file as a table
if not df.empty:
    st.subheader(f'{selected_file_key} Plakası için Mevcut Veriler')
    st.dataframe(df)  # Display the DataFrame as a table
else:
    st.warning("Henüz veri yok.")

# Create input fields for the user to input data
tarih = st.text_input('Tarih:')
baslangickm = st.number_input('Mevcut Kilometre:', min_value=0)
mazot = st.number_input('Alınan Mazot:', min_value=0)
depoyaalinanmazot = st.number_input('Depoya Alınan Mazot:', min_value=0)

# When the user clicks the Submit button
if st.button('Ekle'):
    # Calculate katedilen yol
    if not df.empty:
        previous_km = df.iloc[-1]['baslangickm']
        katedilenyol = baslangickm - previous_km
    else:
        katedilenyol = 0  # No previous entry

    toplam_yol = df['katedilenyol'].sum() + katedilenyol
    ortalama100 = (100 / katedilenyol) * mazot if katedilenyol > 0 else 0
    kumulatif100 = (100 / toplam_yol) * mazot if toplam_yol > 0 else 0
    toplammazot = df['mazot'].sum() + mazot
    depomazot = df['depomazot'].sum() + depoyaalinanmazot - mazot if not df['depomazot'].empty else depoyaalinanmazot - mazot
    depodakalanmazot = depomazot  # Remaining fuel in depot

    # Create new record
    new_record = {
        'tarih': tarih,
        'baslangickm': baslangickm,
        'mazot': mazot,
        'katedilenyol': katedilenyol,
        'toplamyol': toplam_yol,
        'toplammazot': toplammazot,
        'ortalama100': ortalama100,
        'kumulatif100': kumulatif100,
        'depomazot': depomazot,
        'depoyaalinanmazot': depoyaalinanmazot,
        'depodakalanmazot': depodakalanmazot,
        'kalanmazot': kalanmazot,  # Add kalan mazot
        'digerverilen': digerverilen  # Add diğer verilen mazot
    }

    # Append the new record to the DataFrame
    df = pd.concat([df, pd.DataFrame(new_record, index=[0])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
    st.success(f'Data saved to {selected_file_name}!')

    # Display the updated DataFrame
    st.dataframe(df)

# Display a success message without showing the DataFrame
if not df.empty:
    st.subheader('Veri Girişi Başarılı!')
else:
    st.warning("Veri yok.")

# --- Row deletion functionality ---
if not df.empty:
    st.subheader('Satır Silme')
    row_index_to_delete = st.number_input('Silinecek Satır Numarası:', min_value=0, max_value=len(df)-1)
    if st.button('Sil'):
        df = df.drop(index=row_index_to_delete).reset_index(drop=True)
        df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
        st.success('Seçilen satır silindi.')
        st.dataframe(df)

# --- Delete all data functionality ---
if st.button('Tüm Verileri Sil'):
    df = pd.DataFrame(columns=expected_columns)  # Reset the DataFrame
    df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
    st.success('Tüm veriler silindi.')
