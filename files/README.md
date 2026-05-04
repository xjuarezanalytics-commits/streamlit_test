# 🪙 Law of Large Numbers — Interactive Simulator

An interactive web application that visualizes the **Law of Large Numbers** through coin flip simulations. Watch in real time how the running mean converges to the theoretical probability of 0.5 as the number of trials increases.

## 🚀 Live Demo
[View on Render](#) ← replace with your Render URL

## 📐 What is the Law of Large Numbers?
As the number of independent trials increases, the average result converges to the expected value. For a fair coin, the expected probability of heads is **0.5**. This app makes that convergence visible and interactive.

## ✨ Features
- **Real-time animated chart** — watch the mean converge flip by flip
- **Multi-experiment overlay** — compare multiple runs on the same chart with unique colors
- **Live convergence metrics** — distance from 0.5, convergence strength indicator
- **Experiment history table** — with a visual progress bar for distance from expected value
- **Reset button** — clear all experiments and start fresh
- **Up to 2,000 flips** per experiment

## 🛠 Tech Stack
- **Python** — core logic and statistical simulation
- **Streamlit** — web app framework
- **Plotly** — interactive charts
- **SciPy** — Bernoulli distribution sampling
- **Pandas** — experiment results management

## ⚙️ Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/law-of-large-numbers
cd law-of-large-numbers
pip install -r requirements.txt
streamlit run app.py
```

## 📁 Project Structure
```
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## 👩‍💻 Author
**Ximena Juárez** — Data Analyst & Biologist  
[LinkedIn](#) · [Portfolio](#)
