# Australian Employment Data Dashboard 📊

A professional, interactive web dashboard built with Streamlit that visualizes Australian employment data by industry and state using ABS Labour Force Table 10 data.

## 🎯 Features

- **Multi-Select Filters**: Filter by multiple states, territories, and employment types
- **Date Range Slider**: Easily navigate through time periods
- **Multiple Chart Types**:
  - Line charts for employment trends over time
  - Area charts for distribution analysis
  - Bar charts for state comparisons
  - Heatmaps for monthly patterns
  - Comparison charts for side-by-side analysis
- **Key Metrics Dashboard**: Display total employment, changes, and data points
- **Advanced Comparison**: Compare employment trends between two different selections
- **Detailed Data View**: Export and review raw data in a table format
- **Professional Styling**: Modern, gradient-based UI with responsive design
- **Real-time Updates**: Data caching for optimal performance

## 📋 Requirements

- Python 3.8+
- See `requirements.txt` for package dependencies

## 🚀 Quick Start

### 1. Clone or Download the Project

```bash
git clone https://github.com/Zacorn6/DataScience_Projects.git
cd DataScience_Projects/au-employment-dashboard
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download ABS Data

1. Visit: https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia
2. Scroll to **Data downloads** section
3. Download **Table 10**: "Labour force status by Sex, State and Territory - Trend, Seasonally adjusted and Original"
4. Convert to CSV format (if downloaded as XLSX, open in Excel and "Save As" CSV)
5. Save to `data/table10.csv` in the project folder

### 4. Run the Dashboard Locally

```bash
streamlit run app.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

## 📁 Project Structure

```
au-employment-dashboard/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
├── .streamlit/
│   └── config.toml                # Streamlit configuration
└── data/
    └── table10.csv               # ABS Labour Force data (add this)
```

## 🌐 Deployment to Streamlit Cloud

### Step 1: Push to GitHub

1. Ensure all files are committed to your repository
2. Push to GitHub:

```bash
git add .
git commit -m "Add Australian Employment Dashboard"
git push origin main
```

### Step 2: Connect to Streamlit Cloud

1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Click **"New app"**
3. Connect your GitHub account
4. Select:
   - **Repository**: `Zacorn6/DataScience_Projects`
   - **Branch**: `main`
   - **Main file path**: `au-employment-dashboard/app.py`
5. Click **"Deploy"**

### Step 3: Monitor Deployment

The first deployment may take 2-3 minutes. You'll see logs showing:
- Installation of dependencies from `requirements.txt`
- Loading of your data
- Starting of the Streamlit server

Once complete, your dashboard will be live at a URL like:
```
https://datascience-projects-au-employment-dashboard-app-xxxxxxxx.streamlit.app
```

### Step 4: Share Your Dashboard

Share the public URL with anyone to view your dashboard! No installation required.

## 📊 Using the Dashboard

### Sidebar Controls

1. **Date Range Slider**: Select the period you want to analyze
2. **States & Territories**: Choose one or more states to display
3. **Employment Type**: Select employment categories (e.g., Employed, Unemployed)

### Dashboard Sections

#### 📈 Key Metrics
- Total employed persons
- Change from previous period
- Percentage change
- Latest data date
- Number of data points

#### 📈 Employment Trends Over Time
- Line chart showing trends for selected states
- Interactive hover for exact values
- Click legend items to show/hide states

#### 📊 Distribution Analysis
- Stacked area chart showing employment distribution
- Bar chart comparing total employment by state

#### 🔍 State Comparison Analysis
- Bar chart for employment by type
- Heatmap showing monthly employment patterns

#### ⚖️ Advanced Comparison
- Compare two different selections side-by-side
- Separate metrics for each selection
- Visual comparison chart

#### 📋 Detailed Data View
- Toggle to view raw data in table format
- Sort and inspect individual records

## 🔧 Customization

### Change Theme Colors

Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#0052CC"      # Primary color (blue)
backgroundColor = "#FFFFFF"   # Background
secondaryBackgroundColor = "#F0F2F6"  # Secondary
textColor = "#262730"         # Text color
```

### Add More Analysis

Edit `app.py` to add custom analysis, new chart types, or additional metrics.

### Update Dependencies

Modify `requirements.txt` to add new packages and run:
```bash
pip install -r requirements.txt
```

## 📚 Data Source

- **Source**: Australian Bureau of Statistics (ABS)
- **Table**: Labour Force Table 10
- **Data**: Labour force status by Sex, State and Territory
- **Frequency**: Monthly
- **Format**: Trend, Seasonally adjusted, and Original data

More information: https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia

## 🐛 Troubleshooting

### Error: "Data file not found"
- Ensure the CSV file is saved as `data/table10.csv`
- Check the file path is correct relative to the app.py location

### Charts not displaying
- Verify your data CSV has the required columns: Date, State, Value
- Check the data format matches ABS Table 10 structure
- Review the console for error messages

### Slow performance
- Data is cached after first load; refresh should be instant
- For large datasets, filter by date range or fewer states
- Check your internet connection for Streamlit Cloud

### Streamlit Cloud deployment issues
- Ensure `requirements.txt` is in the same directory as `app.py`
- Commit the data file to GitHub (it will be included in deployment)
- Check deployment logs in Streamlit Cloud for specific errors

## 📈 Future Enhancements

Potential features to add:
- Predictive analysis with trend forecasting
- Industry-specific deep dives
- Year-over-year comparisons
- Statistical significance tests
- Export reports to PDF
- Real-time data fetching from ABS API
- Mobile-responsive design improvements

## 📝 License

This project is provided as-is for educational and analytical purposes.

## 🤝 Contributing

Feel free to fork, modify, and improve this dashboard. For major changes, please create an issue or pull request.

## 📧 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Streamlit documentation: https://docs.streamlit.io
3. Check ABS data specifications: https://www.abs.gov.au

---

**Happy analyzing! 📊**
