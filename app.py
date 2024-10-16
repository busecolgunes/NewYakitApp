import io

# Function to convert a DataFrame to an in-memory Excel file
def to_excel_in_memory(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

# Download button for Excel file for 'Kalan Mazot Verileri'
st.download_button(
    label="Kalan Mazot Verilerini İndir",
    data=to_excel_in_memory(global_remaining_fuel_df),
    file_name='global_remaining_fuel.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

# Download button for the selected vehicle plate's data
st.download_button(
    label="Verileri İndir",
    data=to_excel_in_memory(df),
    file_name=f'{selected_file_name}',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

