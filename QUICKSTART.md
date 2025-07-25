# 🚀 Quick Start Guide - VetAI

## ⚡ 1-Minute Setup

### Option 1: Double-Click Setup (Recommended)
1. **Double-click** `start_vetai.bat` in the project folder
2. **Wait** for automatic setup and installation
3. **Open** your browser to http://localhost:5000
4. **Start** predicting livestock diseases!

### Option 2: Manual Setup
```bash
cd Disease_Prediction/Syntom_based_Disease_Prediction
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python application.py
```

## 🎯 Using VetAI

### Making Your First Prediction
1. **Select Animal**: Choose cow, buffalo, sheep, or goat
2. **Enter Details**: Age (years) and body temperature (°F)
3. **Pick Symptoms**: Select 3 symptoms from the dropdowns
4. **Get Results**: Click "Predict Disease" for instant AI diagnosis
5. **View Treatment**: See treatment recommendations and prevention tips

### Viewing Analytics Dashboard
1. **Click Dashboard** in the top navigation
2. **Explore Charts**: Disease distribution, animal types, trends
3. **Check Stats**: Total predictions, accuracy rates, recent activity
4. **Monitor Health**: AI-powered insights and recommendations

## 🔧 Troubleshooting

### Common Issues

**Python not found?**
- Install Python 3.8+ from [python.org](https://python.org)
- Make sure to check "Add Python to PATH" during installation

**Dependencies failed to install?**
- Run as Administrator (right-click → "Run as administrator")
- Check internet connection
- Try: `pip install --upgrade pip`

**Application won't start?**
- Check if port 5000 is already in use
- Try running: `netstat -an | findstr :5000`
- Kill any process using port 5000

**Blank page in browser?**
- Wait 30 seconds for full startup
- Try refreshing the page (F5)
- Check if antivirus is blocking the application

## 📱 Browser Compatibility

✅ **Supported Browsers**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

❌ **Not Supported**
- Internet Explorer (any version)
- Chrome < 80
- Very old mobile browsers

## 🎨 Best Experience Tips

1. **Use Chrome or Firefox** for best performance
2. **Enable JavaScript** for animations and interactions
3. **Use laptop/desktop** for full dashboard experience
4. **Fullscreen mode** (F11) for immersive experience
5. **Stable internet** for loading animations and charts

## 🆘 Need Help?

- **Check Console**: Press F12 → Console tab for error messages
- **Restart App**: Close terminal, double-click `start_vetai.bat` again
- **GitHub Issues**: Report bugs at our GitHub repository
- **Email Support**: Send logs and screenshots to support team

## 📊 Sample Prediction

Try this example to test the system:

```
Animal: Cow
Age: 5 years
Temperature: 102.5°F
Symptom 1: Depression
Symptom 2: Loss of Appetite  
Symptom 3: Painless Lumps
```

Expected Result: **Lumpy Virus** with high confidence

---

**Happy Predicting! 🐄🔬✨**
