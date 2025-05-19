
# RIS to CSV and Back Converter

This repository provides a Python utility to convert bibliographic `.ris` files to `.csv` format, merge them while removing duplicates, and optionally convert them back to `.ris`. It is especially useful for researchers, librarians, or data analysts managing RIS-formatted reference data.

## 📌 Features

- ✅ Batch convert `.ris` files to individual `.csv` files
- ✅ Define field mappings with a `RIS_stds.csv` standards file
- ✅ Merge multiple CSVs into a single deduplicated output
- ✅ Convert merged CSV back to `.ris` format
- ✅ Multi-value fields (e.g., authors, keywords) are preserved correctly
- ✅ Fully based on Python's standard library

## 📁 Project Structure

```
ris-to-csv-converter/
├── RIS/                   # Folder with input .ris files
├── CSV/                   # Output folder for converted .csv files
├── RIS_stds.csv           # RIS standards and tag mapping
├── merged_output.csv      # Merged CSV (auto-generated)
├── merged_output.ris      # Merged RIS (auto-generated)
├── ris2csv.py             # Main Python script
├── README.md              # This file
└── LICENSE                # MIT License
```

## 🛠️ Requirements

- Python 3.6 or higher
- No external dependencies (only uses built-in modules: `csv`, `os`, `glob`, `re`, `pathlib`)

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/jpassos92/ris-to-csv-converter.git
cd ris-to-csv-converter
```

### 2. Prepare Input Files

- Place your `.ris` files in the `RIS/` folder.
- Ensure `RIS_stds.csv` exists in the root directory with the correct RIS tag definitions.

Example RIS entry:
```
TY  - JOUR
AU  - Doe, John
AU  - Smith, Jane
KW  - Quantum computing
T1  - Research on Quantum Tech
ER  -
```

Example `RIS_stds.csv`:
```
TY,Type of reference,1,Type of reference (must be the first tag)
AU,Author,2,Each value should be on a separate line
KW,Keyword,3,Each value should be on a separate line
T1,Title,4,Title of the article
ER,End of Reference,5,Must be empty and the last tag
```

### 3. Adjust Paths (if needed)

Inside `ris2csv.py`, you can configure:
```python
ris_folder = './RIS'
standards_file = './RIS_stds.csv'
csv_output_folder = './CSV'
merged_output_csv = './merged_output.csv'
merged_output_ris = './merged_output.ris'
```

### 4. Run the Script

```bash
python ris2csv.py
```

This will:
- Convert each RIS to CSV
- Save individual CSVs in the `CSV/` folder
- Merge and deduplicate them into `merged_output.csv`
- Convert the merged CSV back to `merged_output.ris`

## 📤 Output Format

### Merged CSV:
```
TY,AU,KW,T1,ER
JOUR,"Doe, John;Smith, Jane","Quantum computing;Quantum tech","Research on Quantum Tech",
```

### Merged RIS:
```
TY  - JOUR
AU  - Doe, John
AU  - Smith, Jane
KW  - Quantum computing
KW  - Quantum tech
T1  - Research on Quantum Tech
ER  -
```

## 🧩 Troubleshooting

- **"No RIS files found"**: Ensure `.ris` files are in the correct folder and path is set properly.
- **"TY field missing"**: Your `RIS_stds.csv` must include a `TY` tag as the first entry.
- **Duplicate rows not removed**: Duplicates are removed based on full row content; minor formatting differences may cause issues.
- **Invalid multi-value field behavior**: Check that `RIS_stds.csv` indicates multi-value fields clearly in the notes (e.g., “each line”).

## 🙋 Contributing

Pull requests are welcome!

1. Fork this repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Added new feature"`
4. Push to your fork: `git push origin feature/your-feature`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## 📬 Contact

- Issues or suggestions? [Open an issue](https://github.com/jpassos92/ris-to-csv-converter/issues)
- Email: jpassos92@gmail.com

---

Built with ❤️ for researchers and data wranglers.
