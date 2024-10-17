import streamlit as st
import pandas as pd
from pathlib import Path

# Add a title to the app
st.title('OMAS ARAÇ YAKIT TAKİP SİSTEMİ')

# Define the file paths for global fuel data
current_dir = Path(__file__).parent if '__file__' in locals() else Path.cwd()
GLOBAL_FILE = current_dir / 'global_fuel_data.xlsx'
GLOBAL_REMAINING_FUEL_FILE = current_dir / 'global_remaining_fuel.xlsx'

# Load or initialize the global fuel data
def load_or_initialize_excel(file_path, default_value):
    if file_path.exists():
        try:
            return pd.read_excel(file_path, engine='openpyxl')
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

# Create session state for inputs if they don't exist
if 'mevcut_kalan_mazot' not in st.session_state:
    st.session_state.mevcut_kalan_mazot = float(global_remaining_fuel)
if 'diger' not in st.session_state:
    st.session_state.diger = 0.0
if 'verilme_nedeni' not in st.session_state:
    st.session_state.verilme_nedeni = ''

# Create a number input for the global "Kalan Mazot"
mevcut_kalan_mazot = st.number_input('Kalan Mazot (Mevcut):', value=st.session_state.mevcut_kalan_mazot)
diger = st.number_input('Diğer Verilen Mazot:', min_value=0.0, value=st.session_state.diger)
verilme_nedeni = st.text_input('Verilme Nedeni:', value=st.session_state.verilme_nedeni)

# Calculate the updated global remaining fuel
updated_global_remaining_fuel = mevcut_kalan_mazot - diger

# Button to update the global remaining fuel value
if st.button('Kalan Mazot Güncelle'):
    # Update the "global_remaining_fuel" in the Excel file
    global_remaining_fuel_df['global_remaining_fuel'].iloc[0] = updated_global_remaining_fuel
    global_remaining_fuel_df.to_excel(GLOBAL_REMAINING_FUEL_FILE, index=False)

    # Update the "depodakalanmazot" in the global fuel data
    global_fuel_df['depodakalanmazot'].iloc[0] = updated_global_remaining_fuel
    global_fuel_df.to_excel(GLOBAL_FILE, index=False)

    # Update session state values
    st.session_state.mevcut_kalan_mazot = updated_global_remaining_fuel
    st.session_state.diger = diger
    st.session_state.verilme_nedeni = verilme_nedeni

    st.success('Kalan mazot güncellendi!')

# Display the updated kalan mazot value
st.write('Güncellenmiş Kalan Mazot:', updated_global_remaining_fuel)

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
                    'depodakalanmazot', 'kalanmazot', 'digerverilen', 'verilmenedeni']

# Load vehicle data function with error handling
def load_vehicle_data(file_path):
    if file_path.exists():
        df = pd.read_excel(file_path, engine='openpyxl')
        # Convert numeric columns to appropriate types
        numeric_columns = ['baslangickm', 'mazot', 'katedilenyol', 'toplamyol', 
                           'toplammazot', 'ortalama100', 'kumulatif100', 
                           'depomazot', 'depoyaalinanmazot', 'depodakalanmazot', 
                           'kalanmazot', 'digerverilen']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')  # Convert and handle errors
        return df
    else:
        return pd.DataFrame(columns=expected_columns)

df = load_vehicle_data(EXCEL_FILE)

# Create input fields for the user to input data
tarih = st.text_input('Tarih:')
baslangickm = st.number_input('Mevcut Kilometre:', min_value=0)
mazot = st.number_input('Alınan Mazot:', min_value=0)
depoyaalinanmazot = st.number_input('Depoya Alınan Mazot:', min_value=0)

# When the user clicks the Submit button
if st.button('Ekle'):
    if not df.empty:
        previous_km = df.iloc[-1]['baslangickm']
        katedilenyol = baslangickm - previous_km
    else:
        katedilenyol = 0  # No previous entry

    toplam_yol = df['katedilenyol'].sum() + katedilenyol
    ortalama100 = (100 / katedilenyol) * mazot if katedilenyol > 0 else 0
    kumulatif100 = (100 / toplam_yol) * mazot if toplam_yol > 0 else 0

    # Create a new entry for the DataFrame
    new_entry = {
        'tarih': tarih,
        'baslangickm': baslangickm,
        'mazot': mazot,
        'katedilenyol': katedilenyol,
        'toplamyol': toplam_yol,
        'toplammazot': mazot,
        'ortalama100': ortalama100,
        'kumulatif100': kumulatif100,
        'depomazot': 0,  # Can be set based on your logic
        'depoyaalinanmazot': depoyaalinanmazot,
        'depodakalanmazot': st.session_state.mevcut_kalan_mazot,
        'kalanmazot': mevcut_kalan_mazot,
        'digerverilen': diger,
        'verilmenedeni': verilme_nedeni
    }

    # Append the new entry to the DataFrame
    df = df.append(new_entry, ignore_index=True)

    # Save the updated DataFrame back to Excel
    df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')

    # Provide feedback to the user
    st.success('Yeni veri eklendi!')

    # Update session state values
    st.session_state.mevcut_kalan_mazot = mevcut_kalan_mazot
    st.session_state.diger = diger
    st.session_state.verilme_nedeni = verilme_nedeni

# --- Delete button ---
if st.button('Seçili Veriyi Sil'):
    if not df.empty:
        df = df.iloc[:-1]  # Remove the last entry for demonstration
        df.to_excel(EXCEL_FILE, index=False)
        st.success('Son veri silindi!')
    else:
        st.warning('Silinecek veri yok!')

# Display the entire DataFrame for vehicle data
st.subheader('Araç Verileri')
st.dataframe(df)

# Display data for "verilme nedeni" and "diğer verilen mazot"
if 'verilme_nedeni' in df.columns and 'digerverilen' in df.columns:
    st.subheader('Verilme Nedeni Verileri')
    st.dataframe(df[['verilmenedeni', 'digerverilen']])
else:
    st.warning('Verilme nedeni veya diğer verilen mazot verisi yok.')

# Upload button for each vehicle plate
uploaded_file = st.file_uploader("Excel Dosyası Yükle:", type=['xlsx'])
if uploaded_file is not None:
    try:
        new_data = pd.read_excel(uploaded_file, engine='openpyxl')
        new_data = new_data.apply(pd.to_numeric, errors='coerce')  # Convert to numeric where possible
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
        st.success(f'{uploaded_file.name} başarıyla yüklendi ve mevcut veriye eklendi!')
    except Exception as e:
        st.error(f'Dosya yükleme hatası: {e}')

# Display the entire DataFrame
st.subheader('Tüm Veri')
st.dataframe(df)
