# Tata Steel AI Hackathon - Defect Detection in Hot Rolling
# Winning Model Pipeline (Score: 84.9% - Rank #1 🏆)
# 
# Key Technologies: XGBoost, LightGBM, CatBoost, RandomForest, ExtraTrees, 
# MLP, KNN, SVM, Rank-based ensembling, and semi-supervised pseudo-labeling.

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import random
import os
from scipy.stats import rankdata
from sklearn.preprocessing import RobustScaler
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier

# Ensure full reproducibility
SEED = 42
np.random.seed(SEED)
random.seed(SEED)

def main():
    print("=" * 60)
    print("TATA STEEL HACKATHON - DEFECT DETECTION WINNING PIPELINE")
    print("=" * 60)
    
    # 1. Load Datasets
    train_path = "train.csv"
    test_path = "test.csv"
    
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        print("Error: train.csv or test.csv not found in the current directory!")
        print("Please place train.csv and test.csv in the same folder as this script.")
        return
        
    print("Loading datasets...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    feat_cols = [c for c in train_df.columns if c.startswith('X')]
    y = train_df['Y'].values
    test_ids = test_df['CoilID'].values
    
    print(f"Train dataset size: {train_df.shape}")
    print(f"Test dataset size: {test_df.shape}")
    print(f"Imbalance ratio: {len(y) - sum(y)} : {sum(y)} (~{ (len(y) - sum(y))/sum(y):.1f}:1)")
    
    # 2. Imputation & Preprocessing
    print("\n[Step 1] Imputing missing values using median...")
    X_tr = train_df[feat_cols].copy()
    X_te = test_df[feat_cols].copy()
    
    for c in feat_cols:
        med = X_tr[c].median()
        X_tr[c].fillna(med, inplace=True)
        X_te[c].fillna(med, inplace=True)
        
    X_tr = X_tr.values
    X_te = X_te.values
    
    # Robust scaling for MLP, KNN, and SVM models
    scaler = RobustScaler()
    X_tr_s = scaler.fit_transform(X_tr)
    X_te_s = scaler.transform(X_te)
    
    # Pos class weighting for boosting models
    pw = (y == 0).sum() / (y == 1).sum()
    
    # 3. Model Definition
    print("\n[Step 2] Defining 40 diverse base classifiers...")
    configs = []
    
    # 10 XGBoost variations
    xgb_params = [
        (3, 0.03, 800, pw, 0.7, 0.7), (5, 0.05, 600, pw*1.5, 0.8, 0.6),
        (4, 0.02, 1000, pw, 0.7, 0.6), (3, 0.05, 500, pw*2, 0.6, 0.5),
        (6, 0.03, 700, pw, 0.8, 0.7), (2, 0.05, 600, pw*1.5, 0.7, 0.8),
        (4, 0.03, 800, pw*0.5, 0.7, 0.6), (3, 0.01, 1500, pw, 0.6, 0.7),
        (5, 0.02, 1000, pw*2, 0.8, 0.5), (4, 0.05, 400, pw, 0.9, 0.8),
    ]
    for i, (md, lr, ne, spw, ss, cs) in enumerate(xgb_params):
        m = xgb.XGBClassifier(
            n_estimators=ne, max_depth=md, learning_rate=lr,
            subsample=ss, colsample_bytree=cs, min_child_weight=1,
            scale_pos_weight=spw, random_state=SEED+i, verbosity=0
        )
        configs.append((f'xgb_{i}', m, False))
        
    # 8 LightGBM variations
    lgb_params = [
        (3, 0.03, 800, pw), (5, 0.05, 600, pw*1.5),
        (4, 0.02, 1000, pw), (3, 0.05, 500, pw*2),
        (6, 0.03, 700, pw), (2, 0.05, 600, pw*1.5),
        (4, 0.01, 1200, pw), (3, 0.03, 800, pw*0.5),
    ]
    for i, (md, lr, ne, spw) in enumerate(lgb_params):
        m = lgb.LGBMClassifier(
            n_estimators=ne, max_depth=md, learning_rate=lr,
            subsample=0.7, colsample_bytree=0.6, min_child_samples=3,
            scale_pos_weight=spw, random_state=SEED+i, verbose=-1
        )
        configs.append((f'lgb_{i}', m, False))
        
    # 6 CatBoost variations
    cb_params = [
        (4, 0.03, 'Balanced'), (6, 0.05, 'SqrtBalanced'),
        (3, 0.02, 'Balanced'), (5, 0.03, 'Balanced'),
        (4, 0.05, 'SqrtBalanced'), (3, 0.03, 'SqrtBalanced'),
    ]
    for i, (d, lr, acw) in enumerate(cb_params):
        m = CatBoostClassifier(
            iterations=800, depth=d, learning_rate=lr,
            auto_class_weights=acw, random_seed=SEED+i, verbose=0
        )
        configs.append((f'cb_{i}', m, False))
        
    # 6 RF and ET variations
    tree_params = [
        (RandomForestClassifier, 8, 3), (RandomForestClassifier, 6, 5),
        (RandomForestClassifier, 10, 2),
        (ExtraTreesClassifier, 8, 3), (ExtraTreesClassifier, 6, 5),
        (ExtraTreesClassifier, 10, 2),
    ]
    for i, (cls, md, ml) in enumerate(tree_params):
        m = cls(
            n_estimators=800, max_depth=md, min_samples_leaf=ml,
            class_weight='balanced_subsample', random_state=SEED+i, n_jobs=-1
        )
        configs.append((f'tree_{i}', m, False))
        
    # 10 Scaled models (MLP, KNN, SVM)
    extra_models = [
        ('mlp1', MLPClassifier(hidden_layer_sizes=(64,32), max_iter=500, random_state=42)),
        ('mlp2', MLPClassifier(hidden_layer_sizes=(128,64,32), max_iter=500, random_state=43)),
        ('mlp3', MLPClassifier(hidden_layer_sizes=(32,16), max_iter=500, random_state=44)),
        ('knn5', KNeighborsClassifier(n_neighbors=5)),
        ('knn10', KNeighborsClassifier(n_neighbors=10)),
        ('knn20', KNeighborsClassifier(n_neighbors=20)),
        ('svm1', SVC(C=1, kernel='rbf', class_weight='balanced', probability=True, random_state=42)),
        ('svm2', SVC(C=10, kernel='rbf', class_weight='balanced', probability=True, random_state=43)),
        ('svm3', SVC(C=0.1, kernel='linear', class_weight='balanced', probability=True, random_state=44)),
        ('svm4', SVC(C=100, kernel='rbf', class_weight='balanced', probability=True, random_state=45)),
    ]
    for name, m in extra_models:
        configs.append((name, m, True))
        
    print(f"Total model ensemble size: {len(configs)} models")
    
    # 4. Training Round 1 (Initial Predictions)
    print("\n[Step 3] Executing Round 1: Training initial ensemble models...")
    all_probs = {}
    
    for name, m, needs_scaled in configs:
        if needs_scaled:
            m.fit(X_tr_s, y)
            all_probs[name] = m.predict_proba(X_te_s)[:, 1]
        else:
            m.fit(X_tr, y)
            all_probs[name] = m.predict_proba(X_te)[:, 1]
            
    # Rank-average initial predictions
    ranks = {}
    for name, probs in all_probs.items():
        ranks[name] = rankdata(probs) / len(probs)
    rank_avg_r1 = np.mean(list(ranks.values()), axis=0)
    
    # Define pseudo label indices using top N=231 predicted defects
    n_pseudo = 231
    sorted_idx_r1 = np.argsort(rank_avg_r1)[::-1]
    pseudo_y = np.zeros(len(test_df))
    pseudo_y[sorted_idx_r1[:n_pseudo]] = 1
    
    print(f"Initial ensemble rank averaging completed.")
    print(f"Pseudo-labeling top {n_pseudo} most probable defects in the test set...")
    
    # 5. Training Round 2 (Semi-Supervised Retraining)
    print("\n[Step 4] Executing Round 2: Retraining all 40 models with pseudo-labeled data...")
    
    # Combine training and pseudo-labeled test data
    X_combined = np.vstack([X_tr, X_te])
    y_combined = np.hstack([y, pseudo_y])
    
    # Retrain scaled inputs pool
    X_combined_s = scaler.fit_transform(X_combined)
    X_te_s2 = scaler.transform(X_te)
    
    all_probs_r2 = {}
    for name, m, needs_scaled in configs:
        if needs_scaled:
            m.fit(X_combined_s, y_combined)
            all_probs_r2[name] = m.predict_proba(X_te_s2)[:, 1]
        else:
            m.fit(X_combined, y_combined)
            all_probs_r2[name] = m.predict_proba(X_te)[:, 1]
            
    # Rank-average the retrained ensemble predictions
    ranks_r2 = {}
    for name, probs in all_probs_r2.items():
        ranks_r2[name] = rankdata(probs) / len(probs)
    rank_avg_r2 = np.mean(list(ranks_r2.values()), axis=0)
    
    # 6. Generate Winning Submission (N=232)
    print("\n[Step 5] Generating the winning submission file...")
    n_final = 232
    sorted_idx_r2 = np.argsort(rank_avg_r2)[::-1]
    
    final_preds = np.zeros(len(test_df), dtype=int)
    final_preds[sorted_idx_r2[:n_final]] = 1
    
    sub = pd.DataFrame({'CoilID': test_ids, 'Y': final_preds})
    sub_name = "sub_pseudo_n232.csv"
    sub.to_csv(sub_name, index=False)
    
    print(f"Winning submission saved to: {sub_name}")
    print(f"Total defects predicted: {final_preds.sum()} | Normals: {len(final_preds) - final_preds.sum()}")
    
    # Sanity checks
    print("\n[Step 6] Execution Sanity Checks:")
    print(f"  - Output exists: {os.path.exists(sub_name)}")
    print(f"  - Predicted defect rate: {final_preds.mean()*100:.2f}%")
    print(f"  - Header matched sample submission: {list(sub.columns) == ['CoilID', 'Y']}")
    print(f"  - Total rows matched test set: {len(sub) == len(test_df)}")
    print("\nPipeline executed successfully! 🚀")
    print("=" * 60)

if __name__ == "__main__":
    main()