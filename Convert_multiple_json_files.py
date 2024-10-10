
import streamlit as st
import json
import csv
import io
import pandas as pd

# Function to clean multiline data in JSON fields
def clean_multiline_field(text):
    if isinstance(text, list):
        text = ', '.join(text)
    return text.replace("\n", " | ") if text else ""

# Convert JSON data to CSV rows
def json_to_csv_rows(json_data, columns):
    csv_row = []
    for column in columns:
        value = json_data.get(column, "")
        value = clean_multiline_field(value)
        csv_row.append(value)
    return csv_row

# Handle multiple JSON files and convert them to a single CSV with headers in the original sequence
def convert_multiple_json_to_csv(json_files, custom_headers):
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)

    json_data_list = []  # Store JSON data

    # Load JSON data
    for json_file in json_files:
        try:
            json_data = json.load(io.TextIOWrapper(json_file, encoding='utf-8'))
            json_data_list.append(json_data)
        except (json.JSONDecodeError, TypeError) as e:
            st.error(f"Error processing file {json_file.name}: {e}")

    # Write the custom headers
    writer.writerow(custom_headers)

    # Write CSV rows based on the custom headers
    for json_data in json_data_list:
        csv_rows = json_to_csv_rows(json_data, custom_headers)
        writer.writerow(csv_rows)

    csv_output.seek(0)
    return csv_output.getvalue().encode('utf-8')


# Convert JSON data to Excel format
def convert_json_to_excel(json_files, custom_headers):
    json_data_list = []
    
    # Load JSON data
    for json_file in json_files:
        try:
            json_data = json.load(io.TextIOWrapper(json_file, encoding='utf-8'))
            json_data_list.append(json_data)
        except (json.JSONDecodeError, TypeError) as e:
            st.error(f"Error processing file {json_file.name}: {e}")

    # Create a DataFrame from the JSON data
    df = pd.DataFrame(json_data_list)

    # Rename the DataFrame columns to the custom headers
    if len(custom_headers) == len(df.columns):
        df.columns = custom_headers
    else:
        st.error("Number of custom headers must match the number of JSON fields.")

    # Save to Excel
    excel_output = io.BytesIO()  # Use BytesIO for binary output
    df.to_excel(excel_output, index=False, engine='openpyxl')
    excel_output.seek(0)  # Move to the beginning of the BytesIO object
    return excel_output.getvalue()

# Convert JSON data to JSON format
def convert_json_to_json(json_files):
    json_data_list = []
    
    for json_file in json_files:
        try:
            json_data = json.load(io.TextIOWrapper(json_file, encoding='utf-8'))
            json_data_list.append(json_data)
        except (json.JSONDecodeError, TypeError) as e:
            st.error(f"Error processing file {json_file.name}: {e}")

    return json.dumps(json_data_list, indent=4).encode('utf-8')

# Page layout and design
st.set_page_config(page_title="JSON to CSV Converter", page_icon="📂", layout="centered")

# Main page title and description
st.title("📂 JSON to CSV Converter")
st.write("Easily convert multiple JSON files into a single CSV file. Upload your JSON files, modify headers if needed, and download the combined file in your preferred format!")

# Sidebar with instructions and useful tips
st.sidebar.title("ℹ️ How to use")
st.sidebar.write("""
1. Upload one or more JSON files.
2. The app will combine all files into one format.
3. Customize the headers if needed before downloading.
""")

# JSON file uploader section
st.subheader("Upload your JSON files")
uploaded_files = st.file_uploader("Select JSON files", type="json", accept_multiple_files=True)

# Process and convert the files
if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")

    # Dynamically detect headers from the first JSON file
    try:
        first_json = json.load(uploaded_files[0])
        default_headers = list(first_json.keys())  # Detect headers from the first file, keep the order
    except (json.JSONDecodeError, TypeError) as e:
        st.error(f"Error processing file {uploaded_files[0].name}: {e}")
        default_headers = []

    if default_headers:
        # Display headers in the sidebar for customization without changing sequence
        st.sidebar.subheader("Detected Headers")
        st.sidebar.write("You can modify the headers if needed, but the sequence will remain unchanged.")

        custom_headers = st.sidebar.text_area(
            "Modify Headers (comma-separated, in the same sequence)",
            value=', '.join(default_headers),
            help="Edit the header names but maintain the sequence as detected."
        ).split(',')

        custom_headers = [header.strip() for header in custom_headers if header.strip()]

        if st.sidebar.button("Apply Changes"):
            st.success(f"Custom headers applied: {', '.join(custom_headers)}")

        # Download format selection
        file_format = st.selectbox("Select download format:", options=["CSV", "Excel (.xlsx)", "JSON"])

        # Convert and provide download button based on selected format
        if file_format == "CSV":
            csv_output = convert_multiple_json_to_csv(uploaded_files, custom_headers)
            st.download_button(
                label="📥 Download CSV",
                data=csv_output,
                file_name="custom_file.csv",
                mime="text/csv",
                help="Click to download the CSV file with your customized headers."
            )
        elif file_format == "Excel (.xlsx)":
            excel_output = convert_json_to_excel(uploaded_files, custom_headers)
            st.download_button(
                label="📥 Download Excel",
                data=excel_output,
                file_name="custom_file.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Click to download the Excel file with your customized headers."
            )
        elif file_format == "JSON":
            json_output = convert_json_to_json(uploaded_files)
            st.download_button(
                label="📥 Download JSON",
                data=json_output,
                file_name="custom_file.json",
                mime="application/json",
                help="Click to download the JSON file."
            )

        # Display a preview of the resulting CSV file
        if file_format == "CSV":
            st.write("### CSV Preview (First 5 Rows)")
            csv_preview = csv_output.decode('utf-8').split('\n', 6)[:6]
            st.code('\n'.join(csv_preview), language="csv")

else:
    st.warning("⚠️ Please upload at least one JSON file to proceed.")

# Footer section
st.write("---")
st.write("Created with ❤️ using Streamlit. This tool helps you transform JSON data into CSV quickly and efficiently.")
