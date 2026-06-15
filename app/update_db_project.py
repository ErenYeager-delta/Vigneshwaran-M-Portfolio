"""
🛠️ Database Project Update Utility Script
Purpose:
  A standalone, local developer utility script that connects to MongoDB Atlas
  and updates metadata (source code link, colab links, description, problem statement, metrics)
  specifically for the 'Predictive Analytics Dashboard' project card.
Connections:
  - Run manually by the developer to sync local updates to the MongoDB database collection directly.
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(r"c:\Users\1771v\Downloads\Vigneshwaran-M-Portfolio-main\Vigneshwaran-M-Portfolio-main\.env")

uri = os.getenv("MONGO_URI")
client = MongoClient(uri)
db = client["portfolioDB"]
col = db["projects"]

# Find the existing project
p = col.find_one({"title": "Predictive Analytics Dashboard"})
if p:
    print("Found existing project. Updating metrics and links...")
    col.update_one(
        {"_id": p["_id"]},
        {"$set": {
            "source_code_link": "https://github.com/ErenYeager-delta/Youtube-Dataset-ML-Supervised-Algorithms-",
            "colab_link": "https://colab.research.google.com/github/ErenYeager-delta/Youtube-Dataset-ML-Supervised-Algorithms-/blob/main/youtube%20regression%20and%20classification.ipynb",
            "notebook_url": "https://colab.research.google.com/github/ErenYeager-delta/Youtube-Dataset-ML-Supervised-Algorithms-/blob/main/youtube%20regression%20and%20classification.ipynb",
            "problem_statement": "Analyzing YouTube Top 100 Songs dataset of 2025 using Supervised Machine Learning algorithms (both Regression and Classification) to uncover viewer engagement patterns, duration relationships, and follower metrics.\n\nGoals:\n- Predict view count based on follower count, duration, and metadata (Regression)\n- Classify whether a video goes live or category clusters based on duration and followers (Classification)",
            "solution_approach": "Algorithms Implemented:\n- K-Means & K-Means++ Clustering\n- Naive Bayes Classifier\n- Simple Linear Regression\n- Support Vector Machines (SVM)\n- Logistic Regression\n- Decision Trees & Random Forest (Ensemble Bagging & Boosting)\n- K-Nearest Neighbors (KNN)\n\nEvaluation Metrics Used:\n- Elbow Method (for K-Means)\n- Accuracy, Confusion Matrix & Classification Report\n- OLS Regression Summary, R-Squared, RMSE, MAE, MSE\n- Threshold Adjusting & AUC-ROC curves",
            "key_metrics": "Regression Performance:\n- Mean Absolute Error (MAE): Detailed continuous evaluation\n- R-Squared Score: Quantified fit of linear predictors\n\nClassification Accuracy:\n- Supervised Classifiers: SVM & Random Forest reached over 85% accuracy in distinguishing top-tier video engagement classes.\n- Random Forest out-performed single Decision Trees via ensemble bagging.",
            "ds_metrics": {
                "accuracy": "85%",
                "algorithms": "7+",
                "dataset": "2025 Top 100"
            },
            "highlight_tag": "ML Supervised Algorithms"
        }}
    )
    print("Project successfully updated in Database!")
else:
    print("Predictive Analytics Dashboard project not found in database!")
