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

# Input for "Diğer Verilen Mazot" and "Verilme Nedeni"
diger = st.number_input('Diğer Verilen Mazot:', min_value=0, value=st.session_state.diger)
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

# Load vehicle data function
def load_vehicle_data(file_path):
    if file_path.exists():
        return pd.read_excel(file_path, engine='openpyxl')
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
    toplammazot = df['mazot'].sum() + mazot
    depomazot = df['depomazot'].sum() + depoyaalinanmazot - mazot if not df['depomazot'].empty else depoyaalinanmazot - mazot
    depodakalanmazot = depomazot  # Remaining fuel in depot

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
        'kalanmazot': st.session_state.mevcut_kalan_mazot,
        'digerverilen': st.session_state.diger,
        'verilmenedeni': st.session_state.verilme_nedeni
    }

    df = pd.concat([df, pd.DataFrame(new_record, index=[0])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
    st.success(f'Data saved to {selected_file_name}!')

    # Display the updated DataFrame
    st.dataframe(df)

# Display "Diğer Verilen Mazot" and "Verilme Nedeni" tables
st.subheader('Diğer Verilen Mazot ve Verilme Nedeni Verileri')
if not df.empty:
    st.write('Diğer Verilen Mazot:')
    st.dataframe(df[['digerverilen']])

    st.write('Verilme Nedeni:')
    st.dataframe(df[['verilmenedeni']])

# --- Upload Excel file and append to existing data ---
uploaded_file = st.file_uploader("Bir Excel dosyası yükleyin ve mevcut veriye ekleyin", type="xlsx")
if uploaded_file is not None:
    try:
        uploaded_df = pd.read_excel(uploaded_file, engine='openpyxl')
        uploaded_df.columns = uploaded_df.columns.str.lower().str.strip()
        df = pd.concat([df, uploaded_df], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
        st.success(f'{uploaded_file.name} başarıyla yüklendi ve mevcut veriye eklendi!')
    except Exception as e:
        st.error(f'Dosya yükleme hatası: {e}')

# --- Delete button ---
if st.button('Seçili Veriyi Sil'):
    if not df.empty:
        df = df.iloc[:-1]  # Remove the last entry for demonstration
        df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
        st.success('Son veri silindi!')
    else:
        st.warning('Silinecek veri yok!')

# Display the entire DataFrame
st.subheader('Tüm Veri')
st.dataframe(df)
