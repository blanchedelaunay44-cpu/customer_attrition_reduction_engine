# C.A.R.E. Frontend

Customer Analytics & Retention Engine Frontend Dashboard

## Features

- 📤 **File Upload**: Drag-and-drop CSV file upload
- 🔄 **Real-time Analysis**: Connects to FastAPI backend for churn prediction
- 📊 **Business Plan Generation**: AI-powered comprehensive retention strategies
- 📈 **Visual Dashboard**: Customer predictions, risk levels, and success metrics
- 📱 **Responsive Design**: Works on desktop and mobile devices
- ⚠️ **Risk Mitigation**: Proactive risk assessment and strategies

## Getting Started

1. **Start the Backend API:**
   ```bash
   cd /path/to/churn_project
   python api/main.py
   # or
   uvicorn api.main:app --reload
   ```

2. **Open the Frontend:**
   ```bash
   open frontend/index.html
   # or simply double-click the index.html file
   ```

3. **Upload Your Data:**
   - Click the upload area or drag & drop a CSV file
   - The file should have the same structure as the training data
   - Click "Analyze Data" to get predictions and business plan

## File Structure

```
frontend/
├── index.html          # Main dashboard HTML
├── css/
│   └── style.css       # Professional styling
├── js/
│   └── app.js         # Application logic and API integration
└── README.md          # This file
```

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## API Integration

The frontend connects to the FastAPI backend running on `http://localhost:8000` by default. You can modify the `apiBaseUrl` in `js/app.js` if your API is running on a different server.

## Data Requirements

The CSV file should contain these columns (same as training data):
- state
- account_length
- area_code
- international_plan
- voice_mail_plan
- number_vmail_messages
- total_day_minutes
- total_day_calls
- total_day_charge
- total_eve_minutes
- total_eve_calls
- total_eve_charge
- total_night_minutes
- total_night_calls
- total_night_charge
- total_intl_minutes
- total_intl_calls
- total_intl_charge
- number_customer_service_calls
- (optional) churn - target column

## Features Explained

### Executive Summary
- Total customers analyzed
- Current churn rate
- High-risk customers


### Business Plan
- **Executive Summary**: AI-generated overview of retention strategy
- **Strategic Priorities**: Critical/High/Medium priority initiatives
- **90-Day Action Plan**: Phased implementation timeline
- **Success Metrics**: Measurable targets and KPIs
- **Risk Mitigation**: Proactive risk management strategies

### Customer Predictions
- Individual customer churn probabilities
- Risk level classification (High/Medium/Low)
- Filter by risk level
- Export results to CSV

## Troubleshooting

**API Connection Issues:**
1. Ensure the FastAPI server is running on port 8000
2. Check for CORS issues in browser console
3. Verify the API status indicator shows "Connected"

**Upload Issues:**
1. Ensure file is in CSV format
2. Check that all required columns are present
3. Verify file size is reasonable (< 50MB)

**Analysis Errors:**
1. Check the API server logs for detailed error messages
2. Verify the CSV file has the correct format
3. Try with a smaller sample of your data

## Customization

The frontend is built with vanilla HTML/CSS/JavaScript for easy customization:

- **Styling**: Modify `css/style.css` for visual changes
- **Layout**: Edit `index.html` for structural changes
- **Functionality**: Update `js/app.js` for new features or API endpoints

## Performance

The frontend is optimized for:
- Fast loading with minimal dependencies
- Smooth animations and transitions
- Mobile-responsive design
- Efficient data handling