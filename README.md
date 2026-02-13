# Finance Visualizer

A robust and flexible Command Line Interface (CLI) tool designed to automate the generation of charts from CSV data. It scans directories for CSV files based on configurable patterns, aggregates data, and generates Line or Bar charts using `matplotlib`.

## 🚀 Features

- **Recursive File Scanning:** Uses glob patterns (e.g., `data/**/*.csv`) to find files in nested directories.
- **Flexible Aggregation:**
  - Group data by specific columns (e.g., Year, Category).
  - sum specific columns or calculated totals of multiple columns.
- **Chart Types:** Supports **Line** and **Bar** charts.
- **Batch Processing:** Define multiple configuration sets in a single JSON file to process different datasets simultaneously.
- **Automatic Output:** Saves generated charts as `.png` files directly alongside the source CSVs.

## 📦 Installation & Requirements

1.  **Clone the repository** (or download the source code).
2.  **Install dependencies**:
    ```bash
    pip install -r requirement.txt
    ```

### Required dependencies:

- Python 3.x
- pandas
- matplotlib

## 🛠️ Usage

Run the tool from the command line by providing the path to your configuration JSON file:

```bash
python main.py --config config.json
```

## Configuration

The tool is driven by a JSON configuration file. The file should contain a **list** of configuration objects.

### Configuration Options

| Key           | Type               | Description                                                                                                                  |
| :------------ | :----------------- | :--------------------------------------------------------------------------------------------------------------------------- |
| `directory`   | `string`           | The glob pattern to search for CSV files. Supports `**` for recursive search.                                                |
| `columns`     | `string` or `list` | The column name(s) to plot on the Y-axis. If a **list** is provided, the tool sums the values of these columns for the plot. |
| `groupby`     | `string` or `list` | The column name(s) to group data by (X-axis).                                                                                |
| `chart_type`  | `string`           | The type of chart to generate. Options: `"line"` or `"bar"`.                                                                 |
| `chart_label` | `string`           | (Optional) Custom label for the chart legend/Y-axis.                                                                         |

### Example `config.json`

```json
[
  {
    "directory": "data/finance/**/*.csv",
    "columns": ["Income", "Dividends"],
    "groupby": "Year",
    "chart_type": "bar",
    "chart_label": "Total Revenue"
  },
  {
    "directory": "data/expenses/*.csv",
    "columns": "Amount",
    "groupby": "Category",
    "chart_type": "line"
  }
]
```

## Example Scenario

**Input File:** `data/2023_financials.csv`

| Year | Category | Salary | Bonus |
| :--- | :------- | :----- | :---- |
| 2023 | Tech     | 50000  | 5000  |
| 2023 | Tech     | 52000  | 6000  |
| 2024 | HR       | 48000  | 4000  |

**Config:**

```json
{
  "directory": "data/*.csv",
  "columns": ["Salary", "Bonus"],
  "groupby": "Year",
  "chart_type": "bar",
  "chart_label": "Total Compensation"
}
```

**Result:**
The tool will:

1.  Read `data/2023_financials.csv`.
2.  Sum `Salary` + `Bonus` into a calculated total.
3.  Group by `Year` (summing the totals for 2023).
4.  Generate a Bar chart named `2023_financials_Year_bar.png` in the `data/` folder.
