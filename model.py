import pandas as pd
import numpy as np
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import mlflow
import mlflow.sklearn

# Load the data
def load_data():
    con = sqlite3.connect('e-com.sqlite')
    df = pd.read_sql_query("SELECT * FROM fact_sales;", con)
    con.close()
    return df

# Preprocess the data
def preprocess_data(df):
    # Convert scraped_timestamp to datetime
    df['scraped_timestamp'] = pd.to_datetime(df['scraped_timestamp'])
    
    # Extract additional features from timestamp
    df['month'] = df['scraped_timestamp'].dt.month
    df['day_of_week'] = df['scraped_timestamp'].dt.dayofweek
    
    # Group by itemId and platform to create aggregated features
    grouped = df.groupby(['itemId', 'platform']).agg({
        'salePrice': ['mean', 'std', 'count'],
        'total_reviews': ['mean', 'max'],
        'rating': ['mean', 'max']
    }).reset_index()
    
    # Flatten multi-level column names
    grouped.columns = ['itemId', 'platform', 
                       'avg_price', 'std_price', 'price_count', 
                       'avg_reviews', 'max_reviews', 
                       'avg_rating', 'max_rating']
    
    return grouped

# Prepare features and target
def prepare_features_target(df):
    # Select features and target
    X = df.drop(['itemId', 'avg_price'], axis=1)
    y = df['avg_price']  # Predicting average price
    
    return X, y

# Create preprocessing pipeline
def create_preprocessing_pipeline():
    # Numeric features
    numeric_features = ['std_price', 'avg_reviews', 'max_reviews', 'avg_rating', 'max_rating', 'price_count']
    
    # Categorical features
    categorical_features = ['platform']
    
    # Preprocessing for numerical and categorical data
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
    
    return preprocessor

# Train the model
def train_model(X, y):
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create full pipeline
    pipeline = Pipeline([
        ('preprocessor', create_preprocessing_pipeline()),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    # Start MLflow run
    with mlflow.start_run():
        # Train the model
        pipeline.fit(X_train, y_train)
        
        # Predictions and evaluation
        y_pred = pipeline.predict(X_test)
        
        # Evaluation metrics
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Log parameters and metrics
        mlflow.log_param("test_size", 0.2)
        mlflow.log_param("n_estimators", 100)
        mlflow.log_metric("Mean Squared Error", mse)
        mlflow.log_metric("Mean Absolute Error", mae)
        mlflow.log_metric("R-squared", r2)
        
        # Log the model
        mlflow.sklearn.log_model(pipeline, "model")
        
        print("Model Evaluation Metrics:")
        print(f"Mean Squared Error: {mse}")
        print(f"Mean Absolute Error: {mae}")
        print(f"R-squared: {r2}")
        
    return pipeline, X, {
        'Mean Squared Error': mse,
        'Mean Absolute Error': mae,
        'R-squared': r2
    }

# Feature importance analysis
def get_feature_importance(model, X):
    # Extract feature names after preprocessing
    preprocessor = model.named_steps['preprocessor']
    
    # Get feature names
    numeric_features = ['std_price', 'avg_reviews', 'max_reviews', 'avg_rating', 'max_rating', 'price_count']
    categorical_features = ['platform']
    
    # Get feature names after one-hot encoding
    onehot_encoder = preprocessor.named_transformers_['cat']
    platform_categories = list(onehot_encoder.get_feature_names_out(categorical_features))
    
    # Combine feature names
    feature_names = numeric_features + platform_categories
    
    # Get feature importances
    importances = model.named_steps['regressor'].feature_importances_
    
    # Create a dataframe of feature importances
    feature_importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    return feature_importance_df

# Main execution
def main():
    # Load and preprocess data
    raw_df = load_data()
    processed_df = preprocess_data(raw_df)
    
    # Prepare features and target
    X, y = prepare_features_target(processed_df)
    
    # Train the model
    model, X_with_features, metrics = train_model(X, y)
    
    # Get and print feature importances
    feature_importance = get_feature_importance(model, X_with_features)
    print("\nFeature Importances:")
    print(feature_importance)
    
    return model, processed_df, feature_importance

# Run the main function
if __name__ == '__main__':
    model, data, feature_importance = main()
